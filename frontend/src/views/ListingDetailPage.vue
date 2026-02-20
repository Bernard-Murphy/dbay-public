<script setup lang="ts">
import { ref, onMounted, computed, watch, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { useListingStore } from "@/stores/listings";
import BidPanel from "@/components/auction/BidPanel.vue";
import { useWebSocket } from "@/composables/useWebSocket";

const route = useRoute();
const listingStore = useListingStore();
const listingId = route.params.id as string;

const listing = computed(() => listingStore.currentListing);
const loading = computed(() => listingStore.loading);
const error = computed(() => listingStore.error);

const currentImage = ref<string>("");

// WebSocket
const wsUrl = import.meta.env.VITE_WS_URL || "ws://localhost:3001"; // Mock or API Gateway
const { isConnected, messages, subscribe, unsubscribe } = useWebSocket(wsUrl);

onMounted(async () => {
  await listingStore.fetchListing(listingId);
  if (listing.value?.images && listing.value.images.length > 0) {
    currentImage.value =
      listing.value.images[0].url_large || listing.value.images[0].url_medium;
  }

  if (listing.value?.listing_type === "AUCTION") {
    subscribe(listingId);
  }
});

onUnmounted(() => {
  if (listing.value?.listing_type === "AUCTION") {
    unsubscribe(listingId);
  }
});

watch(messages, (newMessages) => {
  const lastMessage = newMessages[newMessages.length - 1];
  if (lastMessage && lastMessage.listing_id === listingId) {
    // Update listing price
    if (listing.value) {
      listing.value.current_price = parseFloat(
        lastMessage.current_price || lastMessage.amount,
      );
      // Also update bid count, etc.
      if (lastMessage.bid_count)
        listing.value.bid_count = lastMessage.bid_count;
    }
  }
});

function selectImage(url: string) {
  currentImage.value = url;
}
</script>

<template>
  <div v-if="loading" class="flex justify-center items-center py-20">
    <div
      class="animate-spin rounded-full h-12 w-12 border-b-2 border-doge"
    ></div>
  </div>

  <div v-else-if="error" class="text-red-600 text-center py-20">
    {{ error }}
  </div>

  <div v-else-if="listing" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <div class="lg:grid lg:grid-cols-2 lg:gap-x-8 lg:items-start">
      <!-- Image Gallery -->
      <div class="flex flex-col-reverse">
        <div
          class="hidden mt-6 w-full max-w-2xl mx-auto sm:block lg:max-w-none"
        >
          <div
            class="grid grid-cols-4 gap-6"
            aria-orientation="horizontal"
            role="tablist"
          >
            <button
              v-for="image in listing.images"
              :key="image.id"
              class="relative h-24 bg-white rounded-md flex items-center justify-center text-sm font-medium uppercase text-gray-900 cursor-pointer hover:bg-gray-50 focus:outline-none focus:ring focus:ring-offset-4 focus:ring-opacity-50"
              @click="selectImage(image.url_large || image.url_medium)"
            >
              <span class="sr-only">View Image</span>
              <span class="absolute inset-0 rounded-md overflow-hidden">
                <img
                  :src="image.url_thumb || image.url_medium"
                  alt=""
                  class="w-full h-full object-center object-cover"
                />
              </span>
              <span
                class="ring-transparent absolute inset-0 rounded-md ring-2 ring-offset-2 pointer-events-none"
                aria-hidden="true"
                :class="{
                  'ring-doge':
                    currentImage === (image.url_large || image.url_medium),
                }"
              ></span>
            </button>
          </div>
        </div>

        <div class="w-full aspect-w-1 aspect-h-1">
          <img
            :src="currentImage || 'https://via.placeholder.com/600'"
            alt="Product Image"
            class="w-full h-full object-center object-cover sm:rounded-lg"
          />
        </div>
      </div>

      <!-- Listing Info -->
      <div class="mt-10 px-4 sm:px-0 sm:mt-16 lg:mt-0">
        <h1 class="text-3xl font-extrabold tracking-tight text-gray-900">
          {{ listing.title }}
        </h1>

        <div class="mt-3">
          <h2 class="sr-only">Product information</h2>
          <p class="text-3xl text-gray-900">Ð{{ listing.current_price }}</p>
        </div>

        <div class="mt-6">
          <h3 class="sr-only">Description</h3>
          <div
            class="text-base text-gray-700 space-y-6"
            v-html="listing.description"
          ></div>
        </div>

        <div class="mt-8 border-t border-gray-200 pt-8">
          <h3 class="text-sm font-medium text-gray-900">Listing Details</h3>
          <dl class="mt-4 space-y-4">
            <div class="flex items-center justify-between">
              <dt class="text-sm text-gray-600">Condition</dt>
              <dd class="text-sm font-medium text-gray-900">
                {{ listing.condition }}
              </dd>
            </div>
            <div class="flex items-center justify-between">
              <dt class="text-sm text-gray-600">Category</dt>
              <dd class="text-sm font-medium text-gray-900">
                {{ listing.category_id }}
              </dd>
            </div>
            <div class="flex items-center justify-between">
              <dt class="text-sm text-gray-600">Listing Type</dt>
              <dd class="text-sm font-medium text-gray-900">
                {{ listing.listing_type }}
              </dd>
            </div>
          </dl>
        </div>

        <!-- Action Buttons (Place Bid / Buy Now) -->
        <div class="mt-10 flex sm:flex-col1">
          <BidPanel
            v-if="listing.listing_type === 'AUCTION'"
            :listing="listing"
          />
          <button
            v-else
            type="submit"
            class="max-w-xs flex-1 bg-doge border border-transparent rounded-md py-3 px-8 flex items-center justify-center text-base font-medium text-white hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-50 focus:ring-doge sm:w-full"
          >
            Buy Now
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
