import { createRouter, createWebHistory } from "vue-router";
import HomePage from "@/views/HomePage.vue";
import ListingDetailPage from "@/views/ListingDetailPage.vue";
import CreateListingPage from "@/views/CreateListingPage.vue";
import SearchResultsPage from "@/views/SearchResultsPage.vue";
import WalletPage from "@/views/WalletPage.vue";
import OrdersPage from "@/views/OrdersPage.vue";
import AdminDashboardPage from "@/views/admin/AdminDashboardPage.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomePage,
    },
    {
      path: "/listings/create",
      name: "create-listing",
      component: CreateListingPage,
    },
    {
      path: "/listings/:id",
      name: "listing-detail",
      component: ListingDetailPage,
    },
    {
      path: "/search",
      name: "search",
      component: SearchResultsPage,
    },
    {
      path: "/wallet",
      name: "wallet",
      component: WalletPage,
    },
    {
      path: "/orders",
      name: "orders",
      component: OrdersPage,
    },
    {
      path: "/admin",
      name: "admin",
      component: AdminDashboardPage,
    },
  ],
});

export default router;
