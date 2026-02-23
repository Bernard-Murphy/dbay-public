import axios from "axios";
import { useAuthStore } from "@/stores/auth-store";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export const api = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const { token, user } = useAuthStore.getState();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  // Header-based auth: gateway sets in prod; frontend sets in dev for listing/create and other services
  if (user?.id) config.headers["X-User-ID"] = user.id;
  return config;
});
