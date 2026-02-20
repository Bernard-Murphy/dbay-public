import { defineStore } from "pinia";
import { ref } from "vue";
import walletService from "@/services/walletService";

export interface WalletBalance {
  available: number;
  locked: number;
  pending: number;
}

export interface LedgerEntry {
  id: string;
  entry_type: string;
  debit: number;
  credit: number;
  balance_after: number;
  created_at: string;
  description: string;
}

export const useWalletStore = defineStore("wallet", () => {
  const balance = ref<WalletBalance>({ available: 0, locked: 0, pending: 0 });
  const depositAddress = ref<string>("");
  const history = ref<LedgerEntry[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetchBalance() {
    loading.value = true;
    try {
      const response = await walletService.getBalance();
      balance.value = response.data;
    } catch (e: any) {
      error.value = e.message;
    } finally {
      loading.value = false;
    }
  }

  async function fetchDepositAddress() {
    try {
      const response = await walletService.getDepositAddress();
      depositAddress.value = response.data.address;
    } catch (e: any) {
      error.value = e.message;
    }
  }

  async function fetchHistory() {
    try {
      const response = await walletService.getHistory();
      history.value = response.data;
    } catch (e: any) {
      error.value = e.message;
    }
  }

  async function withdraw(amount: number, address: string) {
    loading.value = true;
    try {
      await walletService.withdraw(amount, address);
      // Refresh balance
      await fetchBalance();
      await fetchHistory();
    } catch (e: any) {
      error.value = e.message;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  return {
    balance,
    depositAddress,
    history,
    loading,
    error,
    fetchBalance,
    fetchDepositAddress,
    fetchHistory,
    withdraw,
  };
});
