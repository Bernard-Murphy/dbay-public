<script setup lang="ts">
import { ref, computed } from "vue";
import type { Listing } from "@/types/listing";
import auctionService from "@/services/auctionService";

const props = defineProps<{
  listing: Listing;
}>();

const bidAmount = ref<number>(0);
const loading = ref(false);
const error = ref<string | null>(null);
const success = ref<string | null>(null);

const minBid = computed(() => {
  return props.listing.current_price + 1.0; // Simplistic increment logic
});

async function submitBid() {
  loading.value = true;
  error.value = null;
  success.value = null;

  if (bidAmount.value < minBid.value) {
    error.value = `Bid must be at least Ð${minBid.value.toFixed(2)}`;
    loading.value = false;
    return;
  }

  try {
    await auctionService.placeBid(props.listing.id, bidAmount.value);
    success.value = "Bid placed successfully!";
    bidAmount.value = 0;
  } catch (e: any) {
    error.value = e.response?.data?.error || e.message || "Failed to place bid";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="bg-gray-50 p-6 rounded-lg border border-gray-200">
    <h3 class="text-lg font-medium text-gray-900 mb-4">Place a Bid</h3>

    <div class="mb-4">
      <p class="text-sm text-gray-500">
        Current Price:
        <span class="text-lg font-bold text-doge"
          >Ð{{ listing.current_price.toFixed(2) }}</span
        >
      </p>
      <p class="text-xs text-gray-400">Minimum Bid: Ð{{ minBid.toFixed(2) }}</p>
    </div>

    <form @submit.prevent="submitBid">
      <div class="mb-4">
        <label for="bidAmount" class="sr-only">Bid Amount</label>
        <div class="mt-1 relative rounded-md shadow-sm">
          <div
            class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
          >
            <span class="text-gray-500 sm:text-sm">Ð</span>
          </div>
          <input
            type="number"
            name="bidAmount"
            id="bidAmount"
            v-model="bidAmount"
            :min="minBid"
            step="0.01"
            class="focus:ring-doge focus:border-doge block w-full pl-7 pr-12 sm:text-sm border-gray-300 rounded-md"
            placeholder="0.00"
          />
        </div>
      </div>

      <div v-if="error" class="text-red-600 text-sm mb-4">{{ error }}</div>
      <div v-if="success" class="text-green-600 text-sm mb-4">
        {{ success }}
      </div>

      <button
        type="submit"
        :disabled="loading"
        class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-doge hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-doge disabled:opacity-50"
      >
        {{ loading ? "Placing Bid..." : "Place Bid" }}
      </button>
    </form>

    <div class="mt-4 text-xs text-center text-gray-500">
      <p>Enter Ð{{ minBid.toFixed(2) }} or more</p>
    </div>
  </div>
</template>
