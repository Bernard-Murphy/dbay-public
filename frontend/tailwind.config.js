/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        doge: "#C2A633", // Dogecoin yellow-ish
      },
    },
  },
  plugins: [],
};
