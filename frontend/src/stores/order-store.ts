import { create } from "zustand";
import { api } from "@/services/api";
import type { Order } from "@/types";

interface OrderState {
  orders: Order[];
  loading: boolean;
  fetchOrders: () => Promise<void>;
  markShipped: (
    orderId: string,
    trackingNumber: string,
    carrier: string,
  ) => Promise<void>;
  complete: (orderId: string) => Promise<void>;
}

export const useOrderStore = create<OrderState>((set, get) => ({
  orders: [],
  loading: false,

  fetchOrders: async () => {
    set({ loading: true });
    try {
      const res = await api.get<Order[] | { results: Order[] }>(
        "/order/orders/",
      );
      const list = Array.isArray(res.data)
        ? res.data
        : ((res.data as { results: Order[] }).results ?? []);
      set({ orders: list });
    } catch {
      set({ orders: [] });
    } finally {
      set({ loading: false });
    }
  },

  markShipped: async (orderId, trackingNumber, carrier) => {
    await api.post(`/order/orders/${orderId}/ship/`, {
      tracking_number: trackingNumber,
      carrier,
    });
    get().fetchOrders();
  },

  complete: async (orderId) => {
    await api.post(`/order/orders/${orderId}/complete/`);
    get().fetchOrders();
  },
}));
