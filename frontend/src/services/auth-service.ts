import { Amplify } from "aws-amplify";
import {
  signIn,
  signOut as amplifySignOut,
  fetchAuthSession,
} from "aws-amplify/auth";
import { authConfig, isCognitoEnabled } from "@/config/auth";
import type { User } from "@/stores/auth-store";
import { api } from "@/services/api";

let configured = false;

export function configureCognito(): void {
  if (!isCognitoEnabled() || configured) return;
  const { userPoolId, userPoolWebClientId } = authConfig.cognito;
  Amplify.configure({
    Auth: {
      Cognito: {
        userPoolId,
        userPoolClientId: userPoolWebClientId,
      },
    },
  });
  configured = true;
}

function ensureConfigured(): void {
  if (!configured && isCognitoEnabled()) {
    configureCognito();
  }
}

export async function cognitoSignIn(
  username: string,
  password: string,
): Promise<{ token: string; user: User } | null> {
  ensureConfigured();
  try {
    await signIn({ username, password });
    const session = await fetchAuthSession({ forceRefresh: true });
    const token = session.tokens?.idToken?.toString();
    if (!token) return null;
    const user = await fetchMeWithToken(token);
    return user ? { token, user } : null;
  } catch {
    return null;
  }
}

export async function getCognitoSession(): Promise<{
  token: string;
  user: User;
} | null> {
  if (!isCognitoEnabled()) return null;
  ensureConfigured();
  try {
    const session = await fetchAuthSession({ forceRefresh: false });
    const token = session.tokens?.idToken?.toString();
    if (!token) return null;
    const user = await fetchMeWithToken(token);
    return user ? { token, user } : null;
  } catch {
    return null;
  }
}

export async function cognitoSignOut(): Promise<void> {
  if (!isCognitoEnabled()) return;
  ensureConfigured();
  await amplifySignOut();
}

async function fetchMeWithToken(token: string): Promise<User | null> {
  const res = await api
    .get<{
      id: string;
      username?: string;
      display_name?: string;
      avatar_url?: string;
    }>("/user/users/me/", {
      headers: { Authorization: `Bearer ${token}` },
    })
    .catch(() => null);
  const data = res?.data;
  if (!data?.id) return null;
  return {
    id: data.id,
    username: data.username,
    displayName: data.display_name,
    avatarUrl: data.avatar_url ?? undefined,
  };
}
