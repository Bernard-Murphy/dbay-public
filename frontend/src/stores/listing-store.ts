import { create } from "zustand";
import { api } from "@/services/api";
import type { Listing } from "@/types";

interface ListingState {
  listings: Listing[];
  currentListing: Listing | null;
  loading: boolean;
  error: string | null;
  fetchListings: (params?: Record<string, string>) => Promise<void>;
  fetchListing: (id: string) => Promise<void>;
  createListing: (data: Partial<Listing>, images?: File[]) => Promise<Listing>;
}

export const useListingStore = create<ListingState>((set, get) => ({
  listings: [],
  currentListing: null,
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

  createListing: async (data, images = []) => {
    set({ loading: true, error: null });
    try {
      const res = await api.post<Listing>("/listings/listings/", data);
      const listing = res.data;
      for (const file of images) {
        const presignRes = await api.post<{ upload_url: string }>(
          `/listings/listings/${listing.id}/presigned-upload/`,
          { filename: file.name, content_type: file.type },
        );
        if (presignRes.data?.upload_url) {
          await fetch(presignRes.data.upload_url, {
            method: "PUT",
            body: file,
            headers: { "Content-Type": file.type },
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
