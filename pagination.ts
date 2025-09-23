// src/project/asset-data/pagination.ts
export type PageResult<T> = {
  items: T[];
  total: number;
  start: number; // 0-based index of first item returned
  end: number;   // 1-based index of last item returned
  page: number;  // 0-based page
  pageCount: number;
};

/**
 * Paginate a sorted array safely (clamps page).
 * - `page` is 0-based
 * - `pageSize` must be >= 1
 */
export function paginate<T>(allItems: T[], page: number, pageSize: number): PageResult<T> {
  const total = allItems.length;
  const safePageSize = Math.max(1, Math.floor(pageSize));
  const pageCount = Math.max(1, Math.ceil(total / safePageSize));
  const safePage = Math.min(Math.max(0, Math.floor(page)), pageCount - 1);

  const start = safePage * safePageSize;
  const endIndex = Math.min(start + safePageSize, total);
  const items = allItems.slice(start, endIndex);

  return {
    items,
    total,
    start,
    end: endIndex, // 1-based-like end index (exclusive converted to count)
    page: safePage,
    pageCount,
  };
}