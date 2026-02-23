import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuthStore } from "@/stores/auth-store";
import { api } from "@/services/api";

interface AdminGuardProps {
  children: React.ReactNode;
}

/** Renders children only if current user is staff; otherwise redirects to home. */
export function AdminGuard({ children }: AdminGuardProps) {
  const { user, isAuthenticated, setUser } = useAuthStore();
  const [checked, setChecked] = useState(false);
  const [isStaff, setIsStaff] = useState(false);

  useEffect(() => {
    if (!isAuthenticated || !user) {
      setChecked(true);
      setIsStaff(false);
      return;
    }
    if (user.is_staff === true) {
      setChecked(true);
      setIsStaff(true);
      return;
    }
    api
      .get("/user/users/me/")
      .then((res) => {
        const data = res.data as { is_staff?: boolean };
        setIsStaff(!!data.is_staff);
        setUser({ ...user, is_staff: !!data.is_staff });
      })
      .catch(() => setIsStaff(false))
      .finally(() => setChecked(true));
  }, [isAuthenticated, user, setUser]);

  if (!checked) return <div className="container py-20 text-center">Checking access...</div>;
  if (!isAuthenticated || !isStaff) return <Navigate to="/" replace />;
  return <>{children}</>;
}
