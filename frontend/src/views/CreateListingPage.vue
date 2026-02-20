<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useListingStore } from "@/stores/listings";
import type { Listing } from "@/types/listing";

const router = useRouter();
const listingStore = useListingStore();

const formData = ref<Partial<Listing>>({
  title: "",
  description: "",
  category_id: undefined,
  condition: "NEW",
  listing_type: "AUCTION",
  starting_price: 0,
  buy_it_now_price: 0,
  reserve_price: 0,
  quantity: 1,
  shipping_cost: 0,
  shipping_from_country: "US",
  returns_accepted: false,
  return_period_days: 0,
});

const images = ref<File[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);

function handleImageUpload(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files) {
    images.value = Array.from(target.files);
  }
}

async function submitForm() {
  loading.value = true;
  error.value = null;

  try {
    const newListing = await listingStore.createListing(
      formData.value,
      images.value,
    );
    router.push({ name: "listing-detail", params: { id: newListing.id } });
  } catch (e: any) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
    <h1 class="text-3xl font-extrabold text-gray-900">Create a Listing</h1>

    <form
      @submit.prevent="submitForm"
      class="mt-8 space-y-8 divide-y divide-gray-200"
    >
      <div class="space-y-8 divide-y divide-gray-200">
        <div>
          <div class="mt-6 grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <div class="sm:col-span-4">
              <label for="title" class="block text-sm font-medium text-gray-700"
                >Title</label
              >
              <div class="mt-1">
                <input
                  type="text"
                  v-model="formData.title"
                  id="title"
                  class="shadow-sm focus:ring-doge focus:border-doge block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </div>
            </div>

            <div class="sm:col-span-6">
              <label
                for="description"
                class="block text-sm font-medium text-gray-700"
                >Description</label
              >
              <div class="mt-1">
                <textarea
                  id="description"
                  v-model="formData.description"
                  rows="3"
                  class="shadow-sm focus:ring-doge focus:border-doge block w-full sm:text-sm border-gray-300 rounded-md"
                ></textarea>
              </div>
            </div>

            <div class="sm:col-span-3">
              <label
                for="category"
                class="block text-sm font-medium text-gray-700"
                >Category</label
              >
              <div class="mt-1">
                <select
                  id="category"
                  v-model="formData.category_id"
                  class="shadow-sm focus:ring-doge focus:border-doge block w-full sm:text-sm border-gray-300 rounded-md"
                >
                  <!-- Categories would be fetched from API in real app -->
                  <option :value="1">Electronics</option>
                  <option :value="2">Clothing</option>
                  <option :value="3">Home & Garden</option>
                </select>
              </div>
            </div>

            <div class="sm:col-span-3">
              <label
                for="condition"
                class="block text-sm font-medium text-gray-700"
                >Condition</label
              >
              <div class="mt-1">
                <select
                  id="condition"
                  v-model="formData.condition"
                  class="shadow-sm focus:ring-doge focus:border-doge block w-full sm:text-sm border-gray-300 rounded-md"
                >
                  <option value="NEW">New</option>
                  <option value="LIKE_NEW">Like New</option>
                  <option value="GOOD">Good</option>
                  <option value="FAIR">Fair</option>
                  <option value="POOR">Poor</option>
                </select>
              </div>
            </div>

            <div class="sm:col-span-3">
              <label
                for="listing_type"
                class="block text-sm font-medium text-gray-700"
                >Listing Type</label
              >
              <div class="mt-1">
                <select
                  id="listing_type"
                  v-model="formData.listing_type"
                  class="shadow-sm focus:ring-doge focus:border-doge block w-full sm:text-sm border-gray-300 rounded-md"
                >
                  <option value="AUCTION">Auction</option>
                  <option value="BUY_IT_NOW">Buy It Now</option>
                  <option value="BOTH">Both</option>
                </select>
              </div>
            </div>

            <div class="sm:col-span-3">
              <label
                for="starting_price"
                class="block text-sm font-medium text-gray-700"
                >Starting Price (Ð)</label
              >
              <div class="mt-1">
                <input
                  type="number"
                  v-model="formData.starting_price"
                  id="starting_price"
                  step="0.01"
                  class="shadow-sm focus:ring-doge focus:border-doge block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </div>
            </div>

            <div class="sm:col-span-6">
              <label
                for="images"
                class="block text-sm font-medium text-gray-700"
                >Images</label
              >
              <div
                class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md"
              >
                <div class="space-y-1 text-center">
                  <svg
                    class="mx-auto h-12 w-12 text-gray-400"
                    stroke="currentColor"
                    fill="none"
                    viewBox="0 0 48 48"
                    aria-hidden="true"
                  >
                    <path
                      d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                  <div class="flex text-sm text-gray-600">
                    <label
                      for="file-upload"
                      class="relative cursor-pointer bg-white rounded-md font-medium text-doge hover:text-yellow-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-doge"
                    >
                      <span>Upload files</span>
                      <input
                        id="file-upload"
                        name="file-upload"
                        type="file"
                        multiple
                        class="sr-only"
                        @change="handleImageUpload"
                      />
                    </label>
                    <p class="pl-1">or drag and drop</p>
                  </div>
                  <p class="text-xs text-gray-500">PNG, JPG, GIF up to 10MB</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="pt-5">
        <div class="flex justify-end">
          <button
            type="button"
            class="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-doge"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-doge hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-doge"
            :disabled="loading"
          >
            {{ loading ? "Creating..." : "Create Listing" }}
          </button>
        </div>
      </div>
    </form>
  </div>
</template>
