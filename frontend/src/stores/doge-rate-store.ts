import { create } from "zustand";

const COINGECKO_URL =
  "https://api.coingecko.com/api/v3/simple/price?ids=dogecoin&vs_currencies=usd";
const FALLBACK_RATE = 0.25;
const TTL_MS = 5 * 60 * 1000; // 5 minutes

interface DogeRateState {
  rate: number;
  loading: boolean;
  error: string | null;
  lastFetched: number | null;
  fetchRate: () => Promise<void>;
}

export const useDogeRateStore = create<DogeRateState>((set, get) => ({
  rate: FALLBACK_RATE,
  loading: false,
  error: null,
  lastFetched: null,

  fetchRate: async () => {
    const { lastFetched } = get();
    if (lastFetched && Date.now() - lastFetched < TTL_MS) {
      return;
    }
    set({ loading: true, error: null });
    try {
      const res = await fetch(COINGECKO_URL);
      const data = await res.json();
      const rate = data?.dogecoin?.usd;
      if (typeof rate === "number" && rate > 0) {
        set({ rate, lastFetched: Date.now(), error: null });
      } else {
        set({ error: "Invalid rate response", rate: FALLBACK_RATE });
      }
    } catch (e) {
      set({
        error: (e as Error).message,
        rate: FALLBACK_RATE,
      });
    } finally {
      set({ loading: false });
    }
  },
}));

/** Get current DOGE/USD rate (from store, or fallback). Triggers fetch if stale. */
export function getDogeRate(): number {
  const state = useDogeRateStore.getState();
  if (!state.lastFetched || Date.now() - state.lastFetched >= TTL_MS) {
    state.fetchRate();
  }
  return state.rate;
}
