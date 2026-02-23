var _a, _b, _c, _d, _e, _f;
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
// When frontend runs in Docker, proxy targets come from docker-compose (VITE_PROXY_*).
// Defaults match docker-compose host port mapping: listing 8001, auction 8002, wallet 8003, user 8004, order 8005, search 8011.
var listing =
  (_a = process.env.VITE_PROXY_LISTING) !== null && _a !== void 0
    ? _a
    : "http://localhost:8001";
var auction =
  (_b = process.env.VITE_PROXY_AUCTION) !== null && _b !== void 0
    ? _b
    : "http://localhost:8002";
var wallet =
  (_c = process.env.VITE_PROXY_WALLET) !== null && _c !== void 0
    ? _c
    : "http://localhost:8003";
var user =
  (_d = process.env.VITE_PROXY_USER) !== null && _d !== void 0
    ? _d
    : "http://localhost:8004";
var order =
  (_e = process.env.VITE_PROXY_ORDER) !== null && _e !== void 0
    ? _e
    : "http://localhost:8005";
var search =
  (_f = process.env.VITE_PROXY_SEARCH) !== null && _f !== void 0
    ? _f
    : "http://localhost:8011";
var devPort = parseInt(
  process.env.VITE_DEV_PORT !== null && process.env.VITE_DEV_PORT !== void 0
    ? process.env.VITE_DEV_PORT
    : "6251",
  10,
);
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: devPort,
    allowedHosts: ["dbay.lol", "localhost"],
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
