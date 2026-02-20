import api from "./api";

export default {
  getBalance() {
    return api.get("/wallet/balance");
  },
  getDepositAddress() {
    return api.get("/wallet/deposit_address");
  },
  withdraw(amount: number, address: string) {
    return api.post("/wallet/withdraw", { amount, address });
  },
  getHistory() {
    return api.get("/wallet/history");
  },
};
