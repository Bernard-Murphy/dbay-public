import { defineStore } from "pinia";
import { ref } from "vue";
import orderService from "@/services/orderService";

export const useOrderStore = defineStore("orders", () => {
  const orders = ref<any[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetchOrders() {
    loading.value = true;
    try {
      const response = await orderService.getAll();
      orders.value = response.data;
    } catch (e: any) {
      error.value = e.message;
    } finally {
      loading.value = false;
    }
  }

  async function purchase(listingId: string) {
    loading.value = true;
    try {
      await orderService.purchase(listingId);
      await fetchOrders();
    } catch (e: any) {
      error.value = e.message;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function markShipped(
    id: string,
    trackingNumber: string,
    carrier: string,
  ) {
    loading.value = true;
    try {
      await orderService.markShipped(id, trackingNumber, carrier);
      await fetchOrders();
    } catch (e: any) {
      error.value = e.message;
    } finally {
      loading.value = false;
    }
  }

  async function complete(id: string) {
    loading.value = true;
    try {
      await orderService.complete(id);
      await fetchOrders();
    } catch (e: any) {
      error.value = e.message;
    } finally {
      loading.value = false;
    }
  }

  return {
    orders,
    loading,
    error,
    fetchOrders,
    purchase,
    markShipped,
    complete,
  };
});
