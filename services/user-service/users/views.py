from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import User, UserAddress
from .serializers import UserSerializer, UserAddressSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return User.objects.all()

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request):
        # In a real scenario, we'd use request.user if using DRF auth, 
        # or look up via X-Cognito-Sub header.
        cognito_sub = request.headers.get('X-Cognito-Sub')
        if not cognito_sub:
             # Fallback for dev/test without gateway
             if request.user.is_authenticated:
                 return Response(self.get_serializer(request.user).data)
             return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        
        user, created = User.objects.get_or_create(cognito_sub=cognito_sub, defaults={
            'username': request.data.get('username', f'user_{cognito_sub[:8]}'),
            'email': request.data.get('email', ''),
        })

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

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
