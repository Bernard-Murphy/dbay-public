import { create } from "zustand";
import { api } from "@/services/api";
import type { Listing } from "@/types";

export interface SearchParams {
  q?: string;
  category?: string;
  listing_type?: string;
  sort?: string;
  page?: string;
}

interface SearchResponse {
  results: Listing[];
  total: number;
  page: number;
  per_page: number;
}

interface ListingState {
  listings: Listing[];
  currentListing: Listing | null;
  searchTotal: number;
  loading: boolean;
  error: string | null;
  fetchListings: (params?: Record<string, string>) => Promise<void>;
  searchListings: (params: SearchParams) => Promise<void>;
  fetchListing: (id: string) => Promise<void>;
  createListing: (
    data: Partial<Listing>,
    images?: File[],
    onFileProgress?: (fileIndex: number, percent: number) => void,
  ) => Promise<Listing>;
}

export const useListingStore = create<ListingState>((set, get) => ({
  listings: [],
  currentListing: null,
  searchTotal: 0,
  loading: false,
  error: null,

  fetchListings: async (params = {}) => {
    set({ loading: true, error: null });
    try {
      const res = await api.get<Listing[] | { results: Listing[] }>(
        "/listings/listings/",
        { params },
      );
      const list = Array.isArray(res.data)
        ? res.data
        : ((res.data as { results: Listing[] }).results ?? []);
      set({ listings: list });
    } catch (e) {
      set({ error: (e as Error).message, listings: [] });
    } finally {
      set({ loading: false });
    }
  },

  searchListings: async (params) => {
    set({ loading: true, error: null });
    try {
      const query: Record<string, string> = {};
      if (params.q) query.q = params.q;
      if (params.category) query.category_id = params.category;
      if (params.listing_type) query.listing_type = params.listing_type;
      if (params.sort) query.sort = params.sort;
      if (params.page) query.page = params.page;
      query.per_page = "20";
      const res = await api.get<SearchResponse>("/search", { params: query });
      const data = res.data as SearchResponse;
      set({
        listings: data.results ?? [],
        searchTotal: data.total ?? 0,
      });
    } catch (e) {
      set({ error: (e as Error).message, listings: [], searchTotal: 0 });
    } finally {
      set({ loading: false });
    }
  },

  fetchListing: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const res = await api.get<Listing>(`/listings/listings/${id}/`);
      set({ currentListing: res.data });
    } catch (e) {
      set({ error: (e as Error).message, currentListing: null });
    } finally {
      set({ loading: false });
    }
  },

  createListing: async (data, images = [], onFileProgress) => {
    set({ loading: true, error: null });
    try {
      const body = { ...data } as Record<string, unknown>;
      if (body.category_id != null) {
        body.category = body.category_id;
        delete body.category_id;
      }
      const res = await api.post<Listing>("/listings/listings/", body);
      const listing = res.data;
      for (let i = 0; i < images.length; i++) {
        const file = images[i];
        onFileProgress?.(i, 0);
        const presignRes = await api.post<{
          upload_url: string;
          s3_key: string;
        }>(`/listings/listings/${listing.id}/images/presigned-url/`, {
          file_name: file.name,
          content_type: file.type,
        });
        const { upload_url, s3_key } = presignRes.data ?? {};
        if (upload_url && s3_key) {
          await new Promise<void>((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.upload.addEventListener("progress", (e) => {
              if (e.lengthComputable)
                onFileProgress?.(i, Math.round((e.loaded / e.total) * 100));
            });
            xhr.addEventListener("load", () =>
              xhr.status >= 200 && xhr.status < 300
                ? resolve()
                : reject(new Error(`Upload failed: ${xhr.status}`)),
            );
            xhr.addEventListener("error", () =>
              reject(new Error("Upload failed")),
            );
            xhr.open("PUT", upload_url);
            xhr.setRequestHeader("Content-Type", file.type);
            xhr.send(file);
          });
          onFileProgress?.(i, 100);
          const mediaType = file.type.startsWith("video/") ? "video" : "image";
          await api.post(`/listings/listings/${listing.id}/images/confirm/`, {
            s3_key: s3_key,
            media_type: mediaType,
            file_size: file.size,
          });
        }
      }
      set({ currentListing: listing });
      return listing;
    } catch (e) {
      set({ error: (e as Error).message });
      throw e;
    } finally {
      set({ loading: false });
    }
  },
}));
