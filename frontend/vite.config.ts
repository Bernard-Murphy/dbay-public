import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// When frontend runs in Docker, proxy must target service names. Set in docker-compose.
const listing = process.env.VITE_PROXY_LISTING ?? "http://localhost:8001";
const auction = process.env.VITE_PROXY_AUCTION ?? "http://localhost:8002";
const wallet = process.env.VITE_PROXY_WALLET ?? "http://localhost:8003";
const user = process.env.VITE_PROXY_USER ?? "http://localhost:8004";
const order = process.env.VITE_PROXY_ORDER ?? "http://localhost:8005";
const search = process.env.VITE_PROXY_SEARCH ?? "http://localhost:8011";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3000,
    proxy: {
      "/api/v1/listings": { target: listing, changeOrigin: true },
      "/api/v1/categories": { target: listing, changeOrigin: true },
      "/api/v1/questions": { target: listing, changeOrigin: true },
      "/api/v1/auction": { target: auction, changeOrigin: true },
      "/api/v1/wallet": { target: wallet, changeOrigin: true },
      "/api/v1/user": { target: user, changeOrigin: true },
      "/api/v1/order": { target: order, changeOrigin: true },
      "/api/v1/search": { target: search, changeOrigin: true },
    },
  },
});
