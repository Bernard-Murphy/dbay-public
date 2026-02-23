import { Navigate } from "react-router-dom";
import { useAuthStore } from "@/stores/auth-store";

interface RequireAuthProps {
  children: React.ReactNode;
}

/** Renders children only if the user is logged in; otherwise redirects to home. */
export function RequireAuth({ children }: RequireAuthProps) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (!isAuthenticated) return <Navigate to="/" replace />;
  return <>{children}</>;
}
