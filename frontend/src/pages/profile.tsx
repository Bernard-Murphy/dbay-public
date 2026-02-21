import { Link } from "react-router-dom";
import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/button";

export function ProfilePage() {
  const { user, isAuthenticated } = useAuthStore();

  if (!isAuthenticated || !user) {
    return (
      <div className="container max-w-md mx-auto px-4 py-12 text-center">
        <p className="text-muted-foreground">Please log in to view your profile.</p>
      </div>
    );
  }

  return (
    <div className="container max-w-md mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Profile</h1>
      <div className="rounded-lg border bg-card p-6 space-y-4">
        <p><span className="text-muted-foreground">Username:</span> {user.username ?? "—"}</p>
        <p><span className="text-muted-foreground">Display name:</span> {user.displayName ?? "—"}</p>
        <div className="pt-4 flex gap-2">
          <Button asChild variant="outline" size="sm"><Link to="/wallet">Wallet</Link></Button>
          <Button asChild variant="outline" size="sm"><Link to="/orders">Orders</Link></Button>
        </div>
      </div>
    </div>
  );
}
