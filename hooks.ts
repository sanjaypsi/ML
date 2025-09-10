import { useEffect, useState, useReducer } from 'react';
import { Asset, ReviewInfo } from './types';
import { fetchAssets, fetchAssetReviewInfos, fetchAssetThumbnail } from './api';
import { Project } from '../types';

export function useFetchAssets(
  project: Project | null | undefined,
  page: number,
  rowsPerPage: number,
): { assets: Asset[], total: number } {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    if (project == null) {
      return;
    }
    const controller = new AbortController();

    (async () => {
      const res = await fetchAssets(
        project.key_name,
        page,
        rowsPerPage,
        controller.signal,
      ).catch((err) => {
        if (err.name === 'AbortError') {
          return;
        }
        console.error(err)
      });
      if (res != null) {
        setAssets(res.assets);
        setTotal(res.total);
      }
    })();
    return () => controller.abort();
  }, [project, page, rowsPerPage]);

  return { assets, total };
};

function reducer(
  state: { [key: string]: ReviewInfo },
  action: { asset: Asset, reviewInfos: ReviewInfo[] },
): { [key: string]: ReviewInfo } {
  const data: { [key: string]: ReviewInfo } = {};
  for (const reviewInfo of action.reviewInfos) {
    data[`${action.asset.name}-${action.asset.relation}-${reviewInfo.phase}`] = reviewInfo;
  }
  return { ...state, ...data };
};

export function useFetchAssetReviewInfos(
  project: Project,
  assets: Asset[],
): { reviewInfos: { [key: string]: ReviewInfo } } {
  const [reviewInfos, dispatch] = useReducer(reducer, {});
  const controller = new AbortController();

  useEffect(() => {
    const loadAssetReviewInfos = async (asset: Asset) => {
      try {
        const res = await fetchAssetReviewInfos(
          project.key_name,
          asset.name,
          asset.relation,
          controller.signal,
        );
        const data = res.reviews;
        if (data.length > 0) {
          dispatch({ asset, reviewInfos: data });
        }
      } catch (err) {
        console.error('Failed to fetch asset review infos:', err);
      }
    };

    for (const asset of assets) {
      loadAssetReviewInfos(asset);
    }

    return () => controller.abort();
  }, [project, assets]);

  return { reviewInfos };
};

function assetThumbnailReducer(
  state: { [key: string]: string },
  action: { asset: Asset, responseResult: string },
): { [key: string]: string } {
  const data: { [key: string]: string } = {};
  data[`${action.asset.name}-${action.asset.relation}`] = action.responseResult;
  return { ...state, ...data };
};

export function useFetchAssetThumbnails(
  project: Project,
  assets: Asset[],
): { thumbnails: { [key: string]: string } } {
  const [thumbnails, dispatch] = useReducer(assetThumbnailReducer, {});
  const controller = new AbortController();

  useEffect(() => {
    const loadAssetThumbnails = async (asset: Asset) => {
      try {
        const res = await fetchAssetThumbnail(
          project.key_name,
          asset.name,
          asset.relation,
          controller.signal,
        );
        if (res != null && res.ok) {
          const reader = new FileReader();
          const blob = await res.blob();
          reader.onload = () => {
            dispatch({ asset, responseResult: reader.result as string });
          };
          reader.readAsDataURL(blob);
        }
      } catch (err) {
        console.error(err);
      }
    };

    for (const asset of assets) {
      loadAssetThumbnails(asset);
    }

    return () => controller.abort();
  }, [project, assets]);

  return { thumbnails };
};
