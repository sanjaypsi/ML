// src/project/asset-data/fetchAllAssetsPages.ts
import { fetchAssets } from "./api"; // your fetchAssets function from api.ts
import { Asset } from "./types";

export async function fetchAllAssets(
  project: string,
  rowsPerPage = 100,
  signal?: AbortSignal | null
): Promise<Asset[]> {
  const all: Asset[] = [];
  let page = 0;
  let total = Infinity;

  while (all.length < total) {
    const { assets, total: returnedTotal } = await fetchAssets(
      project,
      page,
      rowsPerPage,
      signal || null
    );

    if (total === Infinity) total = returnedTotal;
    all.push(...assets);

    if (assets.length === 0) break;
    page += 1;
  }

  return all;
}