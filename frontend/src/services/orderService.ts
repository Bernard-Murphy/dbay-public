import api from "./api";

export default {
  getAll() {
    return api.get("/orders");
  },
  get(id: string) {
    return api.get(`/orders/${id}`);
  },
  create(order: any) {
    return api.post("/orders", order);
  },
  purchase(listingId: string) {
    return api.post("/orders/purchase", { listing_id: listingId });
  },
  markShipped(id: string, trackingNumber: string, carrier: string) {
    return api.post(`/orders/${id}/ship`, {
      tracking_number: trackingNumber,
      carrier,
    });
  },
  complete(id: string) {
    return api.post(`/orders/${id}/complete`);
  },
};
