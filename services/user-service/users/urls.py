from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserAddressViewSet, register_view

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'addresses', UserAddressViewSet)

urlpatterns = [
    path('register/', register_view),
    path('', include(router.urls)),
]
