<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue";
import { useRoute } from "vue-router";
import { useListingStore } from "@/stores/listings";
import ListingCard from "@/components/listings/ListingCard.vue";

const route = useRoute();
const listingStore = useListingStore();

const listings = computed(() => listingStore.listings);
const loading = computed(() => listingStore.loading);

onMounted(() => {
  fetchResults();
});

watch(
  () => route.query,
  () => {
    fetchResults();
  },
);

function fetchResults() {
  listingStore.fetchListings(route.query);
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <h1 class="text-3xl font-bold mb-6">Search Results</h1>

    <div v-if="loading" class="text-center py-20">
      <div
        class="animate-spin rounded-full h-12 w-12 border-b-2 border-doge mx-auto"
      ></div>
    </div>

    <div
      v-else-if="listings.length === 0"
      class="text-center py-20 text-gray-500"
    >
      No listings found.
    </div>

    <div
      v-else
      class="grid grid-cols-1 gap-y-10 sm:grid-cols-2 gap-x-6 lg:grid-cols-3 xl:grid-cols-4 xl:gap-x-8"
    >
      <ListingCard
        v-for="listing in listings"
        :key="listing.id"
        :listing="listing"
      />
    </div>
  </div>
</template>
