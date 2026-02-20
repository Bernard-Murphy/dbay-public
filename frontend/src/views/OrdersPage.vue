<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useOrderStore } from "@/stores/orders";
import { useAuthStore } from "@/stores/auth";

const orderStore = useOrderStore();
const authStore = useAuthStore();

const orders = computed(() => orderStore.orders);
const loading = computed(() => orderStore.loading);
const currentUserId = computed(() => authStore.user?.id);

onMounted(() => {
  orderStore.fetchOrders();
});

async function shipOrder(orderId: string) {
  const tracking = prompt("Enter tracking number:");
  if (tracking) {
    await orderStore.markShipped(orderId, tracking, "FedEx");
  }
}

async function completeOrder(orderId: string) {
  if (confirm("Are you sure you received the item?")) {
    await orderStore.complete(orderId);
  }
}

function isBuyer(order: any) {
  return order.buyer_id === currentUserId.value;
}

function isSeller(order: any) {
  return order.seller_id === currentUserId.value;
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <h1 class="text-3xl font-bold mb-6">My Orders</h1>

    <div v-if="loading" class="text-center py-20">Loading...</div>

    <div v-else class="bg-white shadow overflow-hidden sm:rounded-md">
      <ul role="list" class="divide-y divide-gray-200">
        <li v-for="order in orders" :key="order.id">
          <div class="px-4 py-4 sm:px-6">
            <div class="flex items-center justify-between">
              <p class="text-sm font-medium text-doge truncate">
                Order #{{ order.id }} - Ð{{ order.amount }}
              </p>
              <div class="ml-2 flex-shrink-0 flex">
                <p
                  class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800"
                >
                  {{ order.status }}
                </p>
              </div>
            </div>
            <div class="mt-2 sm:flex sm:justify-between">
              <div class="sm:flex">
                <p class="flex items-center text-sm text-gray-500">
                  {{ isBuyer(order) ? "Buying from" : "Selling to" }}
                  {{ isBuyer(order) ? order.seller_id : order.buyer_id }}
                </p>
              </div>
              <div class="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                <button
                  v-if="isSeller(order) && order.status === 'PAID'"
                  @click="shipOrder(order.id)"
                  class="text-indigo-600 hover:text-indigo-900 mr-4"
                >
                  Mark Shipped
                </button>
                <button
                  v-if="
                    isBuyer(order) &&
                    (order.status === 'SHIPPED' || order.status === 'DELIVERED')
                  "
                  @click="completeOrder(order.id)"
                  class="text-green-600 hover:text-green-900"
                >
                  Confirm Receipt
                </button>
              </div>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>
