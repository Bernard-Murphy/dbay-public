import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { ThemeProvider } from "@/components/theme/theme-provider";
import "./styles/globals.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <ThemeProvider defaultTheme="dark" storageKey="dbay-theme">
        <App />
      </ThemeProvider>
    </BrowserRouter>
  </StrictMode>
);
