from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuctionViewSet

router = DefaultRouter()
router.register(r'auctions', AuctionViewSet, basename='auction')

urlpatterns = [
    path('', include(router.urls)),
]
