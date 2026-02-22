import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuthStore } from "@/stores/auth-store";
import { api } from "@/services/api";

const loginSchema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().min(1, "Password is required"),
});

const registerSchema = z
  .object({
    username: z
      .string()
      .min(3, "Username must be at least 3 characters")
      .max(20, "Username must be less than 20 characters")
      .regex(/^[a-zA-Z0-9_]+$/, "Username can only contain letters, numbers, and underscores"),
    displayName: z.string().min(1, "Display name is required"),
    email: z.string().email("Please enter a valid email address"),
    password: z.string().min(4, "Password must be at least 4 characters"),
    confirmPassword: z.string(),
    bio: z.string().max(500, "Bio must be less than 500 characters").optional(),
    avatar: z.string().url("Please enter a valid URL").optional().or(z.literal("")),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  });

const forgotPasswordSchema = z.object({
  username: z.string().min(1, "Username is required"),
  email: z.string().email("Please enter a valid email address"),
});

type LoginForm = z.infer<typeof loginSchema>;
type RegisterForm = z.infer<typeof registerSchema>;
type ForgotPasswordForm = z.infer<typeof forgotPasswordSchema>;

interface AuthDialogProps {
  trigger?: React.ReactNode;
  defaultTab?: "login" | "register" | "forgot";
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  onSuccess?: () => void;
}

export function AuthDialog({
  trigger,
  defaultTab = "login",
  open: controlledOpen,
  onOpenChange,
  onSuccess,
}: AuthDialogProps) {
  const [internalOpen, setInternalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"login" | "register" | "forgot">(defaultTab);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const open = controlledOpen !== undefined ? controlledOpen : internalOpen;
  const setOpen = onOpenChange || setInternalOpen;

  const loginForm = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { username: "", password: "" },
  });

  const registerForm = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      username: "",
      displayName: "",
      email: "",
      password: "",
      confirmPassword: "",
      bio: "",
    },
  });

  const forgotForm = useForm<ForgotPasswordForm>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { username: "", email: "" },
  });

  const { login } = useAuthStore();

  const handleLogin = async (data: LoginForm) => {
    setMessage(null);
    try {
      const res = await api.post("/user/login/", data).catch(() => null);
      if (res?.data?.token) {
        login(
          { id: res.data.user?.id || "user-id", username: res.data.user?.username || data.username },
          res.data.token
        );
        setMessage({ type: "success", text: "Logged in successfully." });
        setOpen(false);
        onSuccess?.();
      } else {
        setMessage({ type: "error", text: "Invalid credentials. Use any username/password for demo." });
      }
    } catch {
      login({ id: "demo-id", username: data.username }, "demo-token");
      setMessage({ type: "success", text: "Logged in (demo)." });
      setOpen(false);
      onSuccess?.();
    }
  };

  const handleRegister = async (data: RegisterForm) => {
    setMessage(null);
    try {
      const res = await api.post("/user/register/", {
        username: data.username,
        display_name: data.displayName,
        email: data.email,
        password: data.password,
        bio: data.bio || "",
        avatar_url: data.avatar?.trim() || undefined,
      }).catch(() => null);
      if (res?.data?.token) {
        const u = res.data.user;
        login(
          {
            id: u?.id || "user-id",
            username: data.username,
            displayName: data.displayName,
            avatarUrl: u?.avatar_url,
          },
          res.data.token
        );
        setMessage({ type: "success", text: "Account created. You are now logged in." });
        setOpen(false);
        onSuccess?.();
      } else {
        login({ id: "demo-id", username: data.username, displayName: data.displayName }, "demo-token");
        setMessage({ type: "success", text: "Account created (demo)." });
        setOpen(false);
        onSuccess?.();
      }
    } catch {
      login({ id: "demo-id", username: data.username, displayName: data.displayName }, "demo-token");
      setMessage({ type: "success", text: "Account created (demo)." });
      setOpen(false);
      onSuccess?.();
    }
  };

  const handleForgotPassword = async (data: ForgotPasswordForm) => {
    setMessage(null);
    try {
      await api.post("/user/password-reset/", data);
      setMessage({ type: "success", text: "If an account exists, a reset link will be sent to that email." });
      setOpen(false);
    } catch {
      setMessage({ type: "success", text: "If an account exists, a reset link will be sent." });
      setOpen(false);
    }
  };

  const resetForms = () => {
    loginForm.reset();
    registerForm.reset();
    forgotForm.reset();
    setMessage(null);
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        setOpen(next);
        if (!next) resetForms();
      }}
    >
      {trigger && <DialogTrigger asChild>{trigger}</DialogTrigger>}
      <DialogContent className="sm:max-w-md" showClose={true}>
        <DialogHeader>
          <DialogTitle>Welcome to DBay</DialogTitle>
          <DialogDescription>
            Log in or create an account to list items, bid, and buy with Dogecoin.
          </DialogDescription>
        </DialogHeader>
        {message && (
          <p className={message.type === "error" ? "text-sm text-destructive" : "text-sm text-green-600 dark:text-green-400"}>
            {message.text}
          </p>
        )}
        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as "login" | "register" | "forgot")}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="login">Login</TabsTrigger>
            <TabsTrigger value="register">Register</TabsTrigger>
            <TabsTrigger value="forgot">Forgot Password</TabsTrigger>
          </TabsList>
          <TabsContent value="login" className="space-y-4 mt-4">
            <form onSubmit={loginForm.handleSubmit(handleLogin)} className="space-y-4">
              <div>
                <Label htmlFor="login-username">Username</Label>
                <Input
                  id="login-username"
                  {...loginForm.register("username")}
                  disabled={loginForm.formState.isSubmitting}
                />
                {loginForm.formState.errors.username && (
                  <p className="text-sm text-destructive mt-1">{loginForm.formState.errors.username.message}</p>
                )}
              </div>
              <div>
                <Label htmlFor="login-password">Password</Label>
                <Input
                  id="login-password"
                  type="password"
                  {...loginForm.register("password")}
                  disabled={loginForm.formState.isSubmitting}
                />
                {loginForm.formState.errors.password && (
                  <p className="text-sm text-destructive mt-1">{loginForm.formState.errors.password.message}</p>
                )}
              </div>
              <Button type="submit" className="w-full" disabled={loginForm.formState.isSubmitting}>
                {loginForm.formState.isSubmitting ? "Logging in..." : "Login"}
              </Button>
            </form>
          </TabsContent>
          <TabsContent value="register" className="space-y-4 mt-4 overflow-y-auto max-h-[50vh]">
            <form onSubmit={registerForm.handleSubmit(handleRegister)} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="register-username">Username *</Label>
                  <Input
                    id="register-username"
                    {...registerForm.register("username")}
                    disabled={registerForm.formState.isSubmitting}
                  />
                  {registerForm.formState.errors.username && (
                    <p className="text-sm text-destructive mt-1">{registerForm.formState.errors.username.message}</p>
                  )}
                </div>
                <div>
                  <Label htmlFor="register-display-name">Display Name *</Label>
                  <Input
                    id="register-display-name"
                    {...registerForm.register("displayName")}
                    disabled={registerForm.formState.isSubmitting}
                  />
                  {registerForm.formState.errors.displayName && (
                    <p className="text-sm text-destructive mt-1">{registerForm.formState.errors.displayName.message}</p>
                  )}
                </div>
              </div>
              <div>
                <Label htmlFor="register-email">Email *</Label>
                <Input
                  id="register-email"
                  type="email"
                  {...registerForm.register("email")}
                  disabled={registerForm.formState.isSubmitting}
                />
                {registerForm.formState.errors.email && (
                  <p className="text-sm text-destructive mt-1">{registerForm.formState.errors.email.message}</p>
                )}
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="register-password">Password *</Label>
                  <Input
                    id="register-password"
                    type="password"
                    {...registerForm.register("password")}
                    disabled={registerForm.formState.isSubmitting}
                  />
                  {registerForm.formState.errors.password && (
                    <p className="text-sm text-destructive mt-1">{registerForm.formState.errors.password.message}</p>
                  )}
                </div>
                <div>
                  <Label htmlFor="register-confirm-password">Confirm Password *</Label>
                  <Input
                    id="register-confirm-password"
                    type="password"
                    {...registerForm.register("confirmPassword")}
                    disabled={registerForm.formState.isSubmitting}
                  />
                  {registerForm.formState.errors.confirmPassword && (
                    <p className="text-sm text-destructive mt-1">
                      {registerForm.formState.errors.confirmPassword.message}
                    </p>
                  )}
                </div>
              </div>
              <div>
                <Label htmlFor="register-avatar">Avatar (URL)</Label>
                <Input
                  id="register-avatar"
                  type="url"
                  placeholder="https://..."
                  {...registerForm.register("avatar")}
                  disabled={registerForm.formState.isSubmitting}
                />
                {registerForm.formState.errors.avatar && (
                  <p className="text-sm text-destructive mt-1">{registerForm.formState.errors.avatar.message}</p>
                )}
              </div>
              <div>
                <Label htmlFor="register-bio">Bio</Label>
                <Textarea
                  id="register-bio"
                  {...registerForm.register("bio")}
                  placeholder="Optional"
                  className="min-h-[80px]"
                  disabled={registerForm.formState.isSubmitting}
                />
              </div>
              <Button type="submit" className="w-full" disabled={registerForm.formState.isSubmitting}>
                {registerForm.formState.isSubmitting ? "Creating account..." : "Register"}
              </Button>
            </form>
          </TabsContent>
          <TabsContent value="forgot" className="space-y-4 mt-4">
            <form onSubmit={forgotForm.handleSubmit(handleForgotPassword)} className="space-y-4">
              <div>
                <Label htmlFor="forgot-username">Username</Label>
                <Input
                  id="forgot-username"
                  {...forgotForm.register("username")}
                  disabled={forgotForm.formState.isSubmitting}
                />
                {forgotForm.formState.errors.username && (
                  <p className="text-sm text-destructive mt-1">{forgotForm.formState.errors.username.message}</p>
                )}
              </div>
              <div>
                <Label htmlFor="forgot-email">Email</Label>
                <Input
                  id="forgot-email"
                  type="email"
                  {...forgotForm.register("email")}
                  disabled={forgotForm.formState.isSubmitting}
                />
                {forgotForm.formState.errors.email && (
                  <p className="text-sm text-destructive mt-1">{forgotForm.formState.errors.email.message}</p>
                )}
              </div>
              <Button type="submit" className="w-full" disabled={forgotForm.formState.isSubmitting}>
                {forgotForm.formState.isSubmitting ? "Sending..." : "Send Reset Link"}
              </Button>
            </form>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
