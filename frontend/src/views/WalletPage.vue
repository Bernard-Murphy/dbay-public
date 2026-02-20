<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useWalletStore } from "@/stores/wallet";

const walletStore = useWalletStore();
const balance = computed(() => walletStore.balance);
const depositAddress = computed(() => walletStore.depositAddress);
const history = computed(() => walletStore.history);
const loading = computed(() => walletStore.loading);
const error = computed(() => walletStore.error);

const withdrawAmount = ref(0);
const withdrawAddress = ref("");
const withdrawLoading = ref(false);
const withdrawError = ref("");

onMounted(() => {
  walletStore.fetchBalance();
  walletStore.fetchDepositAddress();
  walletStore.fetchHistory();
});

async function handleWithdraw() {
  withdrawLoading.value = true;
  withdrawError.value = "";
  try {
    await walletStore.withdraw(withdrawAmount.value, withdrawAddress.value);
    withdrawAmount.value = 0;
    withdrawAddress.value = "";
  } catch (e: any) {
    withdrawError.value = e.message || "Withdrawal failed";
  } finally {
    withdrawLoading.value = false;
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString();
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <h1 class="text-3xl font-bold mb-6">Wallet</h1>

    <!-- Balance Section -->
    <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
      <div class="px-4 py-5 sm:px-6">
        <h3 class="text-lg leading-6 font-medium text-gray-900">
          Your Balance
        </h3>
      </div>
      <div class="border-t border-gray-200 px-4 py-5 sm:p-0">
        <dl class="sm:divide-y sm:divide-gray-200">
          <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt class="text-sm font-medium text-gray-500">Available</dt>
            <dd
              class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2 text-2xl font-bold text-doge"
            >
              Ð{{ balance?.available || 0 }}
            </dd>
          </div>
          <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt class="text-sm font-medium text-gray-500">Locked (Orders)</dt>
            <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              Ð{{ balance?.locked || 0 }}
            </dd>
          </div>
          <div class="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt class="text-sm font-medium text-gray-500">
              Pending (Withdrawals)
            </dt>
            <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              Ð{{ balance?.pending || 0 }}
            </dd>
          </div>
        </dl>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
      <!-- Deposit Section -->
      <div class="bg-white shadow sm:rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Deposit Dogecoin</h3>
        <p class="text-sm text-gray-500 mb-4">
          Send DOGE to this address to top up your account.
        </p>
        <div class="bg-gray-100 p-4 rounded-md break-all font-mono text-center">
          {{ depositAddress || "Generating..." }}
        </div>
        <div class="mt-4 flex justify-center">
          <!-- QR Code Placeholder -->
          <img
            v-if="depositAddress"
            :src="`https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${depositAddress}`"
            alt="Deposit QR Code"
          />
        </div>
      </div>

      <!-- Withdrawal Section -->
      <div class="bg-white shadow sm:rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">
          Withdraw Dogecoin
        </h3>
        <form @submit.prevent="handleWithdraw">
          <div class="mb-4">
            <label for="address" class="block text-sm font-medium text-gray-700"
              >Destination Address</label
            >
            <input
              type="text"
              id="address"
              v-model="withdrawAddress"
              required
              class="mt-1 shadow-sm focus:ring-doge focus:border-doge block w-full sm:text-sm border-gray-300 rounded-md"
            />
          </div>
          <div class="mb-4">
            <label for="amount" class="block text-sm font-medium text-gray-700"
              >Amount (Ð)</label
            >
            <input
              type="number"
              id="amount"
              v-model="withdrawAmount"
              step="0.00000001"
              min="0.00000001"
              required
              class="mt-1 shadow-sm focus:ring-doge focus:border-doge block w-full sm:text-sm border-gray-300 rounded-md"
            />
          </div>
          <div v-if="withdrawError" class="text-red-600 text-sm mb-4">
            {{ withdrawError }}
          </div>
          <button
            type="submit"
            :disabled="withdrawLoading"
            class="w-full inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-doge hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-doge"
          >
            {{ withdrawLoading ? "Processing..." : "Withdraw" }}
          </button>
        </form>
      </div>
    </div>

    <!-- History Section -->
    <div class="bg-white shadow overflow-hidden sm:rounded-lg">
      <div class="px-4 py-5 sm:px-6">
        <h3 class="text-lg leading-6 font-medium text-gray-900">
          Transaction History
        </h3>
      </div>
      <div class="border-t border-gray-200">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Date
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Type
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Description
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Amount
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="entry in history" :key="entry.id">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(entry.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ entry.entry_type }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">
                {{ entry.description }}
              </td>
              <td
                class="px-6 py-4 whitespace-nowrap text-sm text-right font-medium"
                :class="entry.credit > 0 ? 'text-green-600' : 'text-red-600'"
              >
                {{ entry.credit > 0 ? "+" : "-" }}Ð{{
                  entry.credit > 0 ? entry.credit : entry.debit
                }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
