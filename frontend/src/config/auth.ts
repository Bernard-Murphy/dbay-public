/**
 * Auth configuration. When VITE_USE_COGNITO is true, use Cognito (Amplify);
 * otherwise use dev login (POST /user/login/) and X-User-ID header.
 */
export const authConfig = {
  useCognito: import.meta.env.VITE_USE_COGNITO === "true",
  cognito: {
    userPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID ?? "",
    userPoolWebClientId: import.meta.env.VITE_COGNITO_CLIENT_ID ?? "",
    region: import.meta.env.VITE_AWS_REGION ?? "us-east-1",
  },
};

export function isCognitoEnabled(): boolean {
  return (
    authConfig.useCognito &&
    !!authConfig.cognito.userPoolId &&
    !!authConfig.cognito.userPoolWebClientId
  );
}
