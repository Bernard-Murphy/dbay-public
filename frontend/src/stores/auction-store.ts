import { create } from "zustand";
import { api } from "@/services/api";

interface AuctionState {
  loading: boolean;
  error: string | null;
  placeBid: (listingId: string, amount: number) => Promise<void>;
}

export const useAuctionStore = create<AuctionState>((set, get) => ({
  loading: false,
  error: null,

  placeBid: async (listingId, amount) => {
    set({ loading: true, error: null });
    try {
      await api.post(`/auction/auctions/${listingId}/bid/`, { amount });
      set({ error: null });
    } catch (e) {
      set({ error: (e as Error).message });
    } finally {
      set({ loading: false });
    }
  },
}));
