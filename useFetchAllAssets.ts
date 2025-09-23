// src/project/asset-data/useFetchAllAssets.ts
import { useEffect, useState } from "react";
// import the helper that iteratively fetches pages
import { fetchAllAssets } from "./fetchAllAssetsPages"; // adjust path if you put helper somewhere else
import { Asset } from "./types"; // <- regular import, not `import type`

export default function useFetchAllAssets(project: string | null) {
  const [data, setData] = useState<Asset[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!project) {
      setData(null);
      setIsLoading(false);
      setError(null);
      return;
    }

    const ac = new AbortController();
    setIsLoading(true);
    setError(null);

    fetchAllAssets(project, 100, ac.signal)
      .then((all) => {
        setData(all);
      })
      .catch((err) => {
        if ((err as any).name === "AbortError") return;
        setError(err as Error);
      })
      .finally(() => setIsLoading(false));

    return () => {
      ac.abort();
    };
  }, [project]);

  return { data, isLoading, error };
}