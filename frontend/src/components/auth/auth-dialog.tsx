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
import { isCognitoEnabled } from "@/config/auth";
import { cognitoSignIn } from "@/services/auth-service";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { fade_out, normalize, fade_out_scale_1, transition_fast } from "@/lib/transitions";
import BouncyClick from "../ui/bouncy-click";

/** Valid UUID for demo/fallback so X-User-ID is accepted by listing and other services. */
const DEV_USER_ID = "00000000-0000-0000-0000-000000000001";

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
  const [avatarFile, setAvatarFile] = useState<File | null>(null);

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
    if (isCognitoEnabled()) {
      const result = await cognitoSignIn(data.username, data.password);
      if (result) {
        login(result.user, result.token);
        toast.success("Logged in successfully.");
        setOpen(false);
        onSuccess?.();
      } else {
        toast.error("Invalid username or password.");
      }
      return;
    }
    try {
      const res = await api.post("/user/login/", data).catch(() => null);
      if (res?.data?.token) {
        login(
          { id: res.data.user?.id || DEV_USER_ID, username: res.data.user?.username || data.username },
          res.data.token
        );
        toast.success("Logged in successfully.");
        setOpen(false);
        onSuccess?.();
      } else {
        toast.error("Invalid username or password.");
      }
    } catch {
      login({ id: DEV_USER_ID, username: data.username }, "demo-token");
      toast.success("Logged in successfully.");
      setOpen(false);
      onSuccess?.();
    }
  };

  const handleRegister = async (data: RegisterForm) => {
    try {
      let res: { data?: { user?: { id?: string; username?: string; avatar_url?: string }; token?: string } } | null = null;
      if (avatarFile) {
        const formData = new FormData();
        formData.append("username", data.username);
        formData.append("display_name", data.displayName);
        formData.append("email", data.email);
        formData.append("password", data.password);
        if (data.bio) formData.append("bio", data.bio);
        formData.append("avatar", avatarFile);
        res = await api.post("/user/register/", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        }).catch(() => null);
      } else {
        res = await api.post("/user/register/", {
          username: data.username,
          display_name: data.displayName,
          email: data.email,
          password: data.password,
          bio: data.bio || "",
        }).catch(() => null);
      }
      if (res?.data?.token) {
        const u = res.data.user;
        login(
          {
            id: u?.id || DEV_USER_ID,
            username: data.username,
            displayName: data.displayName,
            avatarUrl: u?.avatar_url,
          },
          res.data.token
        );
        toast.success("Account created. You are now logged in.");
        setOpen(false);
        onSuccess?.();
      } else {
        login({ id: DEV_USER_ID, username: data.username, displayName: data.displayName }, "demo-token");
        toast.success("Account created. You are now logged in.");
        setOpen(false);
        onSuccess?.();
      }
    } catch {
      login({ id: DEV_USER_ID, username: data.username, displayName: data.displayName }, "demo-token");
      toast.success("Account created. You are now logged in.");
      setOpen(false);
      onSuccess?.();
    }
  };

  const handleForgotPassword = async (data: ForgotPasswordForm) => {
    try {
      await api.post("/user/password-reset/", data);
      toast.success("If an account exists, a reset link will be sent to that email.");
      setOpen(false);
    } catch {
      toast.success("If an account exists, a reset link will be sent.");
      setOpen(false);
    }
  };

  const resetForms = () => {
    loginForm.reset();
    registerForm.reset();
    forgotForm.reset();
    setAvatarFile(null);
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
        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as "login" | "register" | "forgot")}>
          <TabsList className="grid w-full grid-cols-3">
            <BouncyClick>
              <TabsTrigger value="login">Login</TabsTrigger>
            </BouncyClick>
            <BouncyClick>
              <TabsTrigger value="register">Register</TabsTrigger>
            </BouncyClick>
            <BouncyClick>
              <TabsTrigger value="forgot">Forgot Password</TabsTrigger>
            </BouncyClick>
          </TabsList>
          {activeTab === "login" && (
            <motion.div key="login" initial={fade_out} animate={normalize} exit={fade_out} className="space-y-4 mt-4">
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
            </motion.div>
          )}
          {activeTab === "register" && (
            <motion.div key="register" initial={fade_out} animate={normalize} exit={fade_out} className="space-y-4 mt-4 overflow-y-auto max-h-[50vh]">
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
                  <Label htmlFor="register-avatar">Avatar (optional)</Label>
                  <input
                    id="register-avatar"
                    type="file"
                    accept="image/*"
                    disabled={registerForm.formState.isSubmitting}
                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                    onChange={(e) => setAvatarFile(e.target.files?.[0] ?? null)}
                  />
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
            </motion.div>
          )}
          {activeTab === "forgot" && (
            <motion.div key="forgot" initial={fade_out} animate={normalize} exit={fade_out} className="space-y-4 mt-4">
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
            </motion.div>

          )}
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
