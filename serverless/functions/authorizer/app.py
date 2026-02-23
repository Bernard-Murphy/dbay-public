"""
Lambda authorizer for API Gateway HTTP API.
Validates Cognito JWT (id or access token), extracts sub/username/email,
optionally resolves cognito_sub to app user_id via User service, and returns
context for header injection: cognito_sub, cognito_username, cognito_email, user_id.
"""
import json
import os
import urllib.request
import logging
from typing import Any, Optional

import jwt
from jwt import PyJWKClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Env (set by SAM)
USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
USER_POOL_REGION = os.environ.get("AWS_REGION", "us-east-1")
USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "")


def _jwks_url() -> str:
    return f"https://cognito-idp.{USER_POOL_REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"


def _get_token(event: dict) -> Optional[str]:
    """Extract Bearer token from Authorization header or identitySource."""
    headers = event.get("headers") or {}
    auth = headers.get("authorization") or headers.get("Authorization") or ""
    if auth.startswith("Bearer "):
        return auth[7:].strip()
    identity = event.get("identitySource") or []
    if identity and isinstance(identity[0], str):
        return identity[0].replace("Bearer ", "").strip()
    return None


def _resolve_user_id(cognito_sub: str) -> Optional[str]:
    """Call User service internal resolve to get app user_id from cognito_sub."""
    if not USER_SERVICE_URL or not cognito_sub:
        return None
    url = f"{USER_SERVICE_URL.rstrip('/')}/api/v1/user/internal/resolve/?cognito_sub={cognito_sub}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode())
                return data.get("user_id")
    except Exception as e:
        logger.warning("Resolve user_id failed: %s", e)
    return None


def lambda_handler(event: dict, context: Any) -> dict:
    """
    HTTP API Lambda authorizer payload format 2.0.
    Returns simple response: { "isAuthorized": bool, "context": { "key": "value" } }.
    API Gateway maps context to request headers (e.g. X-Cognito-Sub, X-User-ID).
    """
    token = _get_token(event)
    if not token:
        return {"isAuthorized": False}

    if not USER_POOL_ID:
        logger.warning("COGNITO_USER_POOL_ID not set; denying")
        return {"isAuthorized": False}

    issuer = f"https://cognito-idp.{USER_POOL_REGION}.amazonaws.com/{USER_POOL_ID}"
    try:
        jwks_client = PyJWKClient(_jwks_url())
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False, "verify_exp": True},
            issuer=issuer,
        )
    except Exception as e:
        logger.warning("JWT validation failed: %s", e)
        return {"isAuthorized": False}

    cognito_sub = payload.get("sub")
    if not cognito_sub:
        return {"isAuthorized": False}

    username = payload.get("cognito:username") or payload.get("username") or ""
    email = payload.get("email") or ""

    ctx = {
        "cognito_sub": cognito_sub,
        "cognito_username": username,
        "cognito_email": email,
    }
    user_id = _resolve_user_id(cognito_sub)
    if user_id:
        ctx["user_id"] = user_id

    return {"isAuthorized": True, "context": ctx}
