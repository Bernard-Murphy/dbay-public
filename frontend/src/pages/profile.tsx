import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/services/api";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

export function ProfilePage() {
  const { user, isAuthenticated, setUser } = useAuthStore();
  const [avatarUrl, setAvatarUrl] = useState(user?.avatarUrl ?? "");
  const [saving, setSaving] = useState(false);
  const [profileUser, setProfileUser] = useState<{ avatar_url?: string; username?: string; display_name?: string } | null>(null);

  useEffect(() => {
    if (user?.avatarUrl) setAvatarUrl(user.avatarUrl);
  }, [user?.avatarUrl]);

  useEffect(() => {
    if (!isAuthenticated) return;
    api.get("/user/users/me/").then((res) => {
      const data = res.data as { avatar_url?: string; username?: string; display_name?: string };
      setProfileUser(data);
      if (data.avatar_url) setAvatarUrl(data.avatar_url);
    }).catch(() => setProfileUser(null));
  }, [isAuthenticated]);

  const displayUser = profileUser ?? user;
  const handleSaveAvatar = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await api.patch("/user/users/me/", { avatar_url: avatarUrl || null });
      const data = res.data as { avatar_url?: string };
      setUser({ ...user!, avatarUrl: data.avatar_url });
      setProfileUser((p) => (p ? { ...p, avatar_url: data.avatar_url } : null));
    } finally {
      setSaving(false);
    }
  };

  if (!isAuthenticated || !user) {
    return (
      <div className="container max-w-md mx-auto px-4 py-12 text-center">
        <p className="text-muted-foreground">Please log in to view your profile.</p>
      </div>
    );
  }

  const avatarSrc =
    avatarUrl?.trim() ||
    (displayUser && "avatarUrl" in displayUser ? displayUser.avatarUrl : (displayUser as { avatar_url?: string })?.avatar_url);

  return (
    <div className="container max-w-md mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Profile</h1>
      <div className="rounded-lg border bg-card p-6 space-y-4">
        <div className="flex items-center gap-4">
          <Avatar className="h-16 w-16">
            <AvatarImage src={avatarSrc} alt="" />
            <AvatarFallback className="text-lg">{(user.displayName || user.username || "?")[0]}</AvatarFallback>
          </Avatar>
          <div>
            <p><span className="text-muted-foreground">Username:</span> {displayUser?.username ?? user.username ?? "—"}</p>
            <p><span className="text-muted-foreground">Display name:</span> {(displayUser as { display_name?: string })?.display_name ?? user.displayName ?? "—"}</p>
          </div>
        </div>
        <form onSubmit={handleSaveAvatar} className="space-y-2">
          <Label htmlFor="profile-avatar">Avatar (URL)</Label>
          <div className="flex gap-2">
            <Input
              id="profile-avatar"
              type="url"
              placeholder="https://..."
              value={avatarUrl}
              onChange={(e) => setAvatarUrl(e.target.value)}
            />
            <Button type="submit" size="sm" disabled={saving}>{saving ? "Saving..." : "Save"}</Button>
          </div>
        </form>
        <div className="pt-4 flex gap-2">
          <Button asChild variant="outline" size="sm"><Link to="/dashboard?tab=wallet">Wallet</Link></Button>
          <Button asChild variant="outline" size="sm"><Link to="/dashboard?tab=orders">Orders</Link></Button>
        </div>
      </div>
    </div>
  );
}
