import { useEffect } from "react";
import { Routes, Route, useLocation, Navigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { fade_out, normalize, fade_out_scale_1, transition_fast } from "@/lib/transitions";
import { Navbar } from "@/components/layout/navbar";
import { HomePage } from "@/pages/home";
import { SearchPage } from "@/pages/search";
import { ListingDetailPage } from "@/pages/listing-detail";
import { CreateListingPage } from "@/pages/create-listing";
import { DashboardPage } from "@/pages/dashboard";
import { AdminDashboardPage } from "@/pages/admin/dashboard";
import { useDogeRateStore } from "@/stores/doge-rate-store";

function App() {
  const location = useLocation();
  const fetchRate = useDogeRateStore((s) => s.fetchRate);
  useEffect(() => {
    fetchRate();
  }, [fetchRate]);
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Navbar />
      <main>
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={fade_out}
            animate={normalize}
            exit={fade_out_scale_1}
            transition={transition_fast}
          >
            <Routes location={location}>
              <Route path="/" element={<HomePage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/listings/create" element={<CreateListingPage />} />
              <Route path="/listings/:id" element={<ListingDetailPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/orders" element={<Navigate to="/dashboard?tab=orders" replace />} />
              <Route path="/wallet" element={<Navigate to="/dashboard?tab=wallet" replace />} />
              <Route path="/profile" element={<Navigate to="/dashboard?tab=profile" replace />} />
              <Route path="/admin" element={<AdminDashboardPage />} />
            </Routes>
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;
