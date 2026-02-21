import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

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
      "/api/v1/listings": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },
      "/api/v1/categories": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },
      "/api/v1/questions": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },
      "/api/v1/auction": {
        target: "http://localhost:8002",
        changeOrigin: true,
      },
      "/api/v1/wallet": { target: "http://localhost:8003", changeOrigin: true },
      "/api/v1/user": { target: "http://localhost:8004", changeOrigin: true },
      "/api/v1/order": { target: "http://localhost:8005", changeOrigin: true },
      "/api/v1/search": { target: "http://localhost:8011", changeOrigin: true },
    },
  },
});
