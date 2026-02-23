import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Moon, Sun, LogIn, PlusCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useAuthStore } from "@/stores/auth-store";
import { useTheme } from "@/components/theme/theme-provider";
import { AuthDialog } from "@/components/auth/auth-dialog";
import { isCognitoEnabled } from "@/config/auth";
import { cognitoSignOut } from "@/services/auth-service";
import dogeLogo from "@/assets/dogecoin-logo.png";
import { motion, AnimatePresence } from "framer-motion";
import { fade_out, normalize, fade_out_scale_1, transition_fast } from "@/lib/transitions";

export function Navbar() {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuthStore();

  const handleLogout = () => {
    if (isCognitoEnabled()) cognitoSignOut().finally(() => logout());
    else logout();
  };
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [authOpen, setAuthOpen] = useState(false);
  const [pendingCreateListing, setPendingCreateListing] = useState(false);

  const handleCreateListingClick = () => {
    if (isAuthenticated) {
      navigate("/listings/create");
    } else {
      setPendingCreateListing(true);
      setAuthOpen(true);
    }
  };

  const handleAuthSuccess = () => {
    if (pendingCreateListing) {
      setPendingCreateListing(false);
      navigate("/listings/create");
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center justify-between px-4 mx-auto">
        <div className="flex items-center gap-6">
          <Button asChild variant="ghost">
            <Link to="/" className="flex items-center gap-2">
              <img src={dogeLogo} alt="Dogecoin Logo" className="h-8 w-8" />
            </Link>
          </Button>
          {isAuthenticated ? (
            <Link to="/listings/create">
              <Button variant="ghost" size="sm" className="gap-2">
                <PlusCircle className="h-4 w-4" />
                Create Listing
              </Button>
            </Link>
          ) : (
            <Button variant="ghost" size="sm" className="gap-2" onClick={handleCreateListingClick}>
              <PlusCircle className="h-4 w-4" />
              Create Listing
            </Button>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
            aria-label="Toggle theme"
          >
            <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          </Button>

          <AnimatePresence mode="wait">
            <motion.div key={isAuthenticated && user ? "authenticated" : "unauthenticated"} initial={fade_out} animate={normalize} exit={fade_out_scale_1} transition={transition_fast}>
              {isAuthenticated && user ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild className="static">
                    <Button variant="ghost" className="h-10 w-10 rounded-full">
                      <Avatar className="h-10 w-10">
                        <AvatarFallback className="bg-primary text-primary-foreground">
                          {(user.username || user.displayName || "U").charAt(0).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-56">
                    <DropdownMenuItem asChild>
                      <Link to="/dashboard?tab=profile">Profile</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/dashboard?tab=wallet">Wallet</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/dashboard?tab=orders">Orders</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={handleLogout}>
                      Log out
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <AuthDialog
                  open={authOpen}
                  onOpenChange={(open) => {
                    setAuthOpen(open);
                    if (!open) setPendingCreateListing(false);
                  }}
                  onSuccess={handleAuthSuccess}
                  trigger={
                    <Button variant="default" size="sm" className="gap-2">
                      <LogIn className="h-4 w-4" />
                      Login / Register
                    </Button>
                  }
                />
              )}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </header>
  );
}
