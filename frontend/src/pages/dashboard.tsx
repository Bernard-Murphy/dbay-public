import { useSearchParams } from "react-router-dom";
import { useEffect } from "react";
import { AccountLayout, type DashboardTab } from "@/components/layout/account-layout";
import { OrdersPage } from "@/pages/orders";
import { WalletPage } from "@/pages/wallet";
import { ProfilePage } from "@/pages/profile";

const VALID_TABS: DashboardTab[] = ["orders", "wallet", "profile"];
const DEFAULT_TAB: DashboardTab = "orders";

function isValidTab(tab: string | null): tab is DashboardTab {
  return tab !== null && VALID_TABS.includes(tab as DashboardTab);
}

export function DashboardPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const tab = searchParams.get("tab");

  useEffect(() => {
    if (!isValidTab(tab)) {
      setSearchParams({ tab: DEFAULT_TAB }, { replace: true });
    }
  }, [tab, setSearchParams]);

  const activeTab: DashboardTab = isValidTab(tab) ? tab : DEFAULT_TAB;

  const content =
    activeTab === "orders" ? (
      <OrdersPage />
    ) : activeTab === "wallet" ? (
      <WalletPage />
    ) : (
      <ProfilePage />
    );

  return <AccountLayout activeTab={activeTab}>{content}</AccountLayout>;
}
