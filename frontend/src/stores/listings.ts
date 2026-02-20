import { defineStore } from "pinia";
import { ref } from "vue";
import type { Listing } from "@/types/listing";
import listingService from "@/services/listingService";

export const useListingStore = defineStore("listings", () => {
  const listings = ref<Listing[]>([]);
  const currentListing = ref<Listing | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetchListings(params: any = {}) {
    loading.value = true;
    error.value = null;
    try {
      const response = await listingService.getAll(params);
      listings.value = response.data.results;
    } catch (e: any) {
      error.value = e.message || "Failed to fetch listings";
    } finally {
      loading.value = false;
    }
  }

  async function fetchListing(id: string) {
    loading.value = true;
    error.value = null;
    try {
      const response = await listingService.get(id);
      currentListing.value = response.data;
    } catch (e: any) {
      error.value = e.message || "Failed to fetch listing";
    } finally {
      loading.value = false;
    }
  }

  async function createListing(listing: Partial<Listing>, images: File[]) {
    loading.value = true;
    error.value = null;
    try {
      const response = await listingService.create(listing);
      const newListing = response.data;

      // Upload images
      if (images.length > 0) {
        await Promise.all(
          images.map((file) => listingService.uploadImage(newListing.id, file)),
        );
      }

      return newListing;
    } catch (e: any) {
      error.value = e.message || "Failed to create listing";
      throw e;
    } finally {
      loading.value = false;
    }
  }

  return {
    listings,
    currentListing,
    loading,
    error,
    fetchListings,
    fetchListing,
    createListing,
  };
});
