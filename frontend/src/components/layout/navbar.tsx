import { Link } from "react-router-dom";
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

export function Navbar() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const { theme, setTheme, resolvedTheme } = useTheme();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center justify-between px-4">
        <div className="flex items-center gap-6">
          <Link to="/" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-md bg-primary flex items-center justify-center text-primary-foreground font-bold text-sm">
              d
            </div>
            <span className="font-semibold">dBay</span>
          </Link>
          <Link to="/listings/create">
            <Button variant="ghost" size="sm" className="gap-2">
              <PlusCircle className="h-4 w-4" />
              Create Listing
            </Button>
          </Link>
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

          {isAuthenticated && user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                  <Avatar className="h-10 w-10">
                    <AvatarFallback className="bg-primary text-primary-foreground">
                      {(user.username || user.displayName || "U").charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuItem asChild>
                  <Link to="/profile">Profile</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link to="/wallet">Wallet</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link to="/orders">Orders</Link>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => logout()}>
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <AuthDialog
              trigger={
                <Button variant="default" size="sm" className="gap-2">
                  <LogIn className="h-4 w-4" />
                  Login / Register
                </Button>
              }
            />
          )}
        </div>
      </div>
    </header>
  );
}
