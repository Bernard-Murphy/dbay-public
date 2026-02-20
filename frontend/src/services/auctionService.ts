import api from "@/services/api";

export default {
  placeBid(listingId: string, amount: number) {
    return api.post(`/auctions/${listingId}/bid`, { amount });
  },
  getBids(listingId: string) {
    return api.get(`/auctions/${listingId}/bids`);
  },
  getState(listingId: string) {
    return api.get(`/auctions/${listingId}/state`);
  },
};
