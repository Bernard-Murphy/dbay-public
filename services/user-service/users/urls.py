from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    UserAddressViewSet,
    register_view,
    dev_login_view,
    resolve_cognito_view,
    serve_avatar_view,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'addresses', UserAddressViewSet)

urlpatterns = [
    path('register/', register_view),
    path('login/', dev_login_view),
    path('internal/resolve/', resolve_cognito_view),
    path('avatar/<uuid:id>/', serve_avatar_view),
    path('', include(router.urls)),
]
