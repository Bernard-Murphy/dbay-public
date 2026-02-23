"""
Header-based authentication for listing service.

- Production: API Gateway validates the Cognito JWT and sets X-User-ID (and optionally
  X-Cognito-Sub) before forwarding. We trust the header.
- Local dev: Frontend sends X-User-ID when the user is logged in (no gateway).
"""
import logging
import uuid
from rest_framework.authentication import BaseAuthentication

logger = logging.getLogger(__name__)


class AuthenticatedUser:
    """Minimal user object for request.user when using header auth. Listing service has no User model."""
    is_authenticated = True
    is_anonymous = False

    def __init__(self, user_id):
        self.id = user_id  # UUID


class HeaderBasedAuthentication(BaseAuthentication):
    """
    Authenticate using X-User-ID (and optionally X-Cognito-Sub) set by API Gateway after JWT validation,
    or by the frontend in local dev when the user is logged in.
    """
    def authenticate(self, request):
        # Prefer X-User-ID (UUID from user service); gateway or frontend sets it
        raw = request.headers.get('X-User-ID')
        if not raw:
            # Gateway may set X-Cognito-Sub (Cognito subject) instead; we use it as opaque id for dev
            raw = request.headers.get('X-Cognito-Sub')
        if not raw:
            return None
        try:
            user_id = uuid.UUID(str(raw).strip())
        except (ValueError, TypeError):
            return None
        return (AuthenticatedUser(user_id), None)
