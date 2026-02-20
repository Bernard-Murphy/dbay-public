<script setup lang="ts">
import type { Listing } from "@/types/listing";
import { computed } from "vue";

const props = defineProps<{
  listing: Listing;
}>();

const formattedPrice = computed(() => {
  return props.listing.current_price
    ? `Ð${props.listing.current_price.toFixed(2)}`
    : "Ð0.00";
});

const thumbnailUrl = computed(() => {
  if (props.listing.images && props.listing.images.length > 0) {
    return (
      props.listing.images[0].url_thumb || "https://via.placeholder.com/150"
    );
  }
  return "https://via.placeholder.com/150";
});
</script>

<template>
  <div
    class="group relative bg-white border border-gray-200 rounded-lg flex flex-col overflow-hidden hover:shadow-md transition-shadow"
  >
    <div
      class="aspect-w-3 aspect-h-4 bg-gray-200 group-hover:opacity-75 sm:aspect-none sm:h-56"
    >
      <img
        :src="thumbnailUrl"
        :alt="listing.title"
        class="w-full h-full object-center object-cover sm:w-full sm:h-full"
      />
    </div>
    <div class="flex-1 p-4 space-y-2 flex flex-col">
      <h3 class="text-sm font-medium text-gray-900">
        <router-link
          :to="{ name: 'listing-detail', params: { id: listing.id } }"
        >
          <span aria-hidden="true" class="absolute inset-0" />
          {{ listing.title }}
        </router-link>
      </h3>
      <p class="text-sm text-gray-500 line-clamp-2">
        {{ listing.description }}
      </p>
      <div class="flex-1 flex flex-col justify-end">
        <p class="text-lg font-bold text-doge">{{ formattedPrice }}</p>
        <p
          class="text-xs text-gray-500"
          v-if="listing.listing_type === 'AUCTION'"
        >
          {{ listing.view_count }} views
        </p>
      </div>
    </div>
  </div>
</template>
