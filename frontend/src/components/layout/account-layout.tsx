import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Wallet, ShoppingBag, User } from "lucide-react";
import { Button } from "../ui/button";

export type DashboardTab = "orders" | "wallet" | "profile";

interface AccountLayoutProps {
  activeTab: DashboardTab;
  children: React.ReactNode;
}

export function AccountLayout({ activeTab, children }: AccountLayoutProps) {
  return (
    <div className="flex h-[calc(100vh-4rem)]">
      <aside className="w-full md:w-64 border-r bg-background p-4 space-y-2 flex-shrink-0">
        <nav className="flex flex-col gap-1">
          <Button variant="ghost" asChild className="justify-start">
            <Link
              to="/dashboard?tab=orders"
              className={cn(
                "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors w-full",
                activeTab === "orders"
                  ? "bg-primary/10 text-primary hover:bg-primary/20"
                  : "hover:bg-muted hover:text-foreground"
              )}
            >
              <ShoppingBag className="h-4 w-4" />
              Orders
            </Link>
          </Button>
          <Button variant="ghost" asChild className="justify-start">
            <Link
              to="/dashboard?tab=wallet"
              className={cn(
                "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors w-full",
                activeTab === "wallet"
                  ? "bg-primary/10 text-primary hover:bg-primary/20"
                  : "hover:bg-muted hover:text-foreground"
              )}
            >
              <Wallet className="h-4 w-4" />
              Wallet
            </Link>
          </Button>
          <Button variant="ghost" asChild className="justify-start">
            <Link
              to="/dashboard?tab=profile"
              className={cn(
                "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors w-full",
                activeTab === "profile"
                  ? "bg-primary/10 text-primary hover:bg-primary/20"
                  : "hover:bg-muted hover:text-foreground"
              )}
            >
              <User className="h-4 w-4" />
              Profile
            </Link>
          </Button>


        </nav>
      </aside>
      <div className="flex-1 overflow-auto">
        {children}
      </div>
    </div>
  );
}
