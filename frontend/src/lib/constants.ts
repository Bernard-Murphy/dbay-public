/** DOGE to USD conversion rate. Can be overridden by VITE_DOGE_USD_RATE env. */
export const DOGE_TO_USD =
  typeof import.meta.env.VITE_DOGE_USD_RATE !== "undefined"
    ? Number(import.meta.env.VITE_DOGE_USD_RATE)
    : 0.25;
