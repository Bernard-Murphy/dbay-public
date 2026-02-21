import { create } from "zustand";
import { api } from "@/services/api";
import type { LedgerEntry } from "@/types";

interface Balance {
  available: number;
  locked: number;
  pending: number;
}

interface WalletState {
  balance: Balance | null;
  depositAddress: string | null;
  history: LedgerEntry[];
  loading: boolean;
  error: string | null;
  fetchBalance: () => Promise<void>;
  fetchDepositAddress: () => Promise<void>;
  fetchHistory: () => Promise<void>;
  withdraw: (amount: number, address: string) => Promise<void>;
}

export const useWalletStore = create<WalletState>((set, get) => ({
  balance: null,
  depositAddress: null,
  history: [],
  loading: false,
  error: null,

  fetchBalance: async () => {
    set({ loading: true });
    try {
      const res = await api.get<Balance>("/wallet/wallet/balance/");
      set({ balance: res.data });
    } catch {
      set({ balance: { available: 0, locked: 0, pending: 0 } });
    } finally {
      set({ loading: false });
    }
  },

  fetchDepositAddress: async () => {
    try {
      const res = await api.get<{ address: string }>(
        "/wallet/wallet/deposit-address/",
      );
      set({ depositAddress: res.data?.address ?? null });
    } catch {
      set({ depositAddress: null });
    }
  },

  fetchHistory: async () => {
    set({ loading: true });
    try {
      const res = await api.get<LedgerEntry[] | { results: LedgerEntry[] }>(
        "/wallet/wallet/history/",
      );
      const list = Array.isArray(res.data)
        ? res.data
        : ((res.data as { results: LedgerEntry[] }).results ?? []);
      set({ history: list });
    } catch {
      set({ history: [] });
    } finally {
      set({ loading: false });
    }
  },

  withdraw: async (amount, address) => {
    await api.post("/wallet/wallet/withdraw/", {
      amount,
      destination_address: address,
    });
    get().fetchBalance();
    get().fetchHistory();
  },
}));
