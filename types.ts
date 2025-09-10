import { TableCellProps } from "@material-ui/core/TableCell";
import { ReactElement } from "react";
import { Project } from '../types';

export type AssetsDataTableProps = {
  project: Project | null | undefined,
  assets: Asset[],
  tableFooter: ReactElement,
  dateTimeFormat: Intl.DateTimeFormat,
};

export type RecordTableHeadProps = {
  columns: Column[],
};

export type Colors = Readonly<{
  lineColor: string,
  backgroundColor: string,
}>;

export type Column = Readonly<{
  id: string,
  label: string,
  colors?: Colors,
  align?: TableCellProps['align'],
}>;

export type PageProps = Readonly<{
  page: number,
  rowsPerPage: number,
}>;

export type ReviewInfo = {
  task_id: string,
  project: string,
  take_path: string,
  root: string,
  relation: string,
  phase: string,
  component: string,
  take: string,
  approval_status: string,
  work_status: string,
  submitted_at_utc: string,
  submitted_user: string,
  modified_at_utc: string,
  id: number,
  groups: string[],
  group_1: string,
  review_comments: ReviewComment[],
};

type ReviewComment = {
  text: string,
  language: string,
  attachments: string[],
  is_translated: boolean,
  need_translation: boolean
};

export type Asset = Readonly<{
  name: string,
  relation: string,
}>;

export type FilterProps = Readonly<{
  assetNameKey: string,
  applovalStatues: string[],
  workStatues: string[],
}>;

export type ChipDeleteFunction = (value: string) => void;

export type AssetRowProps = Readonly<{
  asset: Asset,
  reviewInfos: { [key: string]: ReviewInfo },
  thumbnails: { [key: string]: string },
  dateTimeFormat: Intl.DateTimeFormat,
  isLastRow: boolean,
}>;
