import { useState, useEffect, useCallback } from "react";
import { api } from "@/services/api";

export function useQuery<T>(url: string, options?: { fallback?: T }) {
  const [data, setData] = useState<T | undefined>(options?.fallback as T);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const refetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<T>(url);
      setData(res.data);
    } catch (e) {
      setError(e instanceof Error ? e : new Error("Failed to fetch"));
      if (options?.fallback !== undefined) setData(options.fallback as T);
    } finally {
      setLoading(false);
    }
  }, [url, options?.fallback]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { data, loading, error, refetch };
}
