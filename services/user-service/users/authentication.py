from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User
import logging

logger = logging.getLogger(__name__)

class CognitoAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # In prod, API Gateway sets these headers after validating the JWT.
        # In dev (local), we might mock them or rely on a simpler auth.
        cognito_sub = request.headers.get('X-Cognito-Sub')
        
        if not cognito_sub:
            return None

        try:
            user, created = User.objects.get_or_create(
                cognito_sub=cognito_sub,
                defaults={
                    'username': request.headers.get('X-Cognito-Username', f'user_{cognito_sub[:8]}'),
                    'email': request.headers.get('X-Cognito-Email', ''),
                }
            )
            return (user, None)
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            raise AuthenticationFailed('Authentication failed')
