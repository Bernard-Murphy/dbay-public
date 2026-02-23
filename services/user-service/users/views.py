import os
import uuid
import boto3
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import User, UserAddress
from .serializers import UserSerializer, UserAddressSerializer, PublicUserSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def resolve_cognito_view(request):
    """Internal: resolve cognito_sub to user id. Used by API Gateway authorizer. No auth (internal only)."""
    cognito_sub = request.GET.get('cognito_sub') or request.headers.get('X-Cognito-Sub')
    if not cognito_sub:
        return Response({"error": "cognito_sub required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(cognito_sub=cognito_sub)
        return Response({"user_id": str(user.id)})
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def dev_login_view(request):
    """Dev-only: username/password login without Cognito. Returns user + token for local development."""
    username = request.data.get('username')
    password = request.data.get('password')  # noqa: not validated in dev
    if not username:
        return Response({"error": "username required"}, status=status.HTTP_400_BAD_REQUEST)
    cognito_sub = f"dev-{uuid.uuid4().hex}"
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f"{username}@dev.local",
            'display_name': username,
            'cognito_sub': cognito_sub,
        },
    )
    serializer = UserSerializer(user)
    return Response({"user": serializer.data, "token": "demo-token"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Create a new user. Expects username, email, display_name, password (ignored), bio (ignored).
    Avatar: optional file via request.FILES.get('avatar'), or avatar_url in form data."""
    username = request.data.get('username')
    email = request.data.get('email')
    display_name = request.data.get('display_name') or username
    avatar_file = request.FILES.get('avatar')
    avatar_url = request.data.get('avatar_url') or None
    if not username or not email:
        return Response({"error": "username and email required"}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=email).exists():
        return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)
    if avatar_file:
        ext = os.path.splitext(avatar_file.name)[1] or ".jpg"
        if ext.lower() not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
            return Response({"error": "Invalid image type"}, status=status.HTTP_400_BAD_REQUEST)
    cognito_sub = f"reg-{uuid.uuid4().hex}"
    user = User.objects.create(
        username=username,
        email=email,
        display_name=display_name,
        avatar_url=avatar_url,
        cognito_sub=cognito_sub,
    )
    if avatar_file:
        s3_key = f"avatars/{user.id}/{uuid.uuid4().hex}{ext}"
        bucket = os.environ.get("AWS_S3_BUCKET_NAME", "dbay-listing-images")
        s3 = boto3.client(
            "s3",
            endpoint_url=os.environ.get("AWS_ENDPOINT_URL"),
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
        )
        try:
            s3.upload_fileobj(
                avatar_file, bucket, s3_key,
                ExtraArgs={"ContentType": avatar_file.content_type or "image/jpeg"},
            )
        except Exception as e:
            user.delete()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        base = request.build_absolute_uri("/").rstrip("/")
        user.avatar_s3_key = s3_key
        user.avatar_url = f"{base}/api/v1/user/avatar/{user.id}/"
        user.save(update_fields=["avatar_s3_key", "avatar_url"])
    serializer = UserSerializer(user)
    return Response({"user": serializer.data, "token": "demo-token"}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([AllowAny])
def serve_avatar_view(request, id):
    """Serve avatar image from S3."""
    user = get_object_or_404(User, id=id)
    if not user.avatar_s3_key:
        return HttpResponse(status=404)
    bucket = os.environ.get("AWS_S3_BUCKET_NAME", "dbay-listing-images")
    s3 = boto3.client(
        "s3",
        endpoint_url=os.environ.get("AWS_ENDPOINT_URL"),
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )
    try:
        obj = s3.get_object(Bucket=bucket, Key=user.avatar_s3_key)
        content_type = obj.get("ContentType", "image/jpeg")
        body = obj["Body"].read()
        return HttpResponse(body, content_type=content_type)
    except Exception:
        return HttpResponse(status=404)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PublicUserSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request):
        user = self._get_me_user(request)
        if not user:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def _get_me_user(self, request):
        cognito_sub = request.headers.get("X-Cognito-Sub")
        if cognito_sub:
            username = request.headers.get("X-Cognito-Username") or f"user_{cognito_sub[:8]}"
            email = request.headers.get("X-Cognito-Email") or ""
            user, _ = User.objects.get_or_create(
                cognito_sub=cognito_sub,
                defaults={"username": username, "email": email or f"{username}@placeholder.local", "display_name": username},
            )
            return user
        raw_id = request.headers.get("X-User-ID")
        if raw_id:
            try:
                return User.objects.get(id=raw_id)
            except (User.DoesNotExist, ValueError):
                pass
        if getattr(request, "user", None) and request.user.is_authenticated:
            return request.user
        return None

    @action(detail=False, methods=["post"], url_path="me/avatar")
    def me_avatar(self, request):
        user = self._get_me_user(request)
        if not user:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        file = request.FILES.get("file") or request.FILES.get("avatar")
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        ext = os.path.splitext(file.name)[1] or ".jpg"
        if ext.lower() not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
            return Response({"error": "Invalid image type"}, status=status.HTTP_400_BAD_REQUEST)
        s3_key = f"avatars/{user.id}/{uuid.uuid4().hex}{ext}"
        bucket = os.environ.get("AWS_S3_BUCKET_NAME", "dbay-listing-images")
        s3 = boto3.client(
            "s3",
            endpoint_url=os.environ.get("AWS_ENDPOINT_URL"),
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
        )
        try:
            s3.upload_fileobj(file, bucket, s3_key, ExtraArgs={"ContentType": file.content_type or "image/jpeg"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        user.avatar_s3_key = s3_key
        base = request.build_absolute_uri("/").rstrip("/")
        user.avatar_url = f"{base}/api/v1/user/avatar/{user.id}/"
        user.save(update_fields=["avatar_s3_key", "avatar_url"])
        return Response({"avatar_url": user.avatar_url})

class UserAddressViewSet(viewsets.ModelViewSet):
    queryset = UserAddress.objects.all()
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter by current user
        # This requires resolving the user from the request (header or token)
        # For now, just return all for simplicity in this step, but in prod we filter by user
        return UserAddress.objects.all() 

    def perform_create(self, serializer):
        # Associate with current user
        # serializer.save(user=self.request.user)
        pass
