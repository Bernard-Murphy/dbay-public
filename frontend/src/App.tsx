import { Routes, Route } from "react-router-dom";
import { Navbar } from "@/components/layout/navbar";
import { HomePage } from "@/pages/home";
import { SearchPage } from "@/pages/search";
import { ListingDetailPage } from "@/pages/listing-detail";
import { CreateListingPage } from "@/pages/create-listing";
import { WalletPage } from "@/pages/wallet";
import { OrdersPage } from "@/pages/orders";
import { AdminDashboardPage } from "@/pages/admin/dashboard";
import { ProfilePage } from "@/pages/profile";

function App() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/listings/create" element={<CreateListingPage />} />
          <Route path="/listings/:id" element={<ListingDetailPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/wallet" element={<WalletPage />} />
          <Route path="/orders" element={<OrdersPage />} />
          <Route path="/admin" element={<AdminDashboardPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
