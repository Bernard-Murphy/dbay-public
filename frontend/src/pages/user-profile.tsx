import { useParams, Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { api } from "@/services/api";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { format } from "date-fns";
import { BadgeCheck } from "lucide-react";

interface PublicUser {
  id: string;
  username: string;
  display_name: string;
  avatar_url: string | null;
  seller_verified: boolean;
  created_at: string;
}

export function UserProfilePage() {
  const { id } = useParams<{ id: string }>();
  const [user, setUser] = useState<PublicUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    api
      .get<PublicUser>(`/user/users/${id}/`)
      .then((res) => setUser(res.data))
      .catch(() => setError("User not found"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="container max-w-md mx-auto px-4 py-12 text-center">Loading...</div>;
  if (error || !user) return <div className="container max-w-md mx-auto px-4 py-12 text-center text-muted-foreground">{error ?? "User not found."}</div>;

  return (
    <div className="container max-w-md mx-auto px-4 py-8">
      <div className="rounded-lg border bg-card p-6 space-y-4">
        <div className="flex items-center gap-4">
          <Avatar className="h-20 w-20">
            <AvatarImage src={user.avatar_url ?? undefined} alt="" />
            <AvatarFallback className="text-2xl">{(user.display_name || user.username || "?")[0]}</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <h1 className="text-xl font-bold truncate">{user.display_name || user.username}</h1>
            <p className="text-muted-foreground truncate">@{user.username}</p>
            {user.seller_verified && (
              <p className="flex items-center gap-1 text-sm text-primary mt-1">
                <BadgeCheck className="h-4 w-4" /> Verified seller
              </p>
            )}
          </div>
        </div>
        <p className="text-sm text-muted-foreground">Member since {format(new Date(user.created_at), "MMMM yyyy")}</p>
        <Button asChild variant="outline" size="sm">
          <Link to="/search">View listings</Link>
        </Button>
      </div>
    </div>
  );
}
