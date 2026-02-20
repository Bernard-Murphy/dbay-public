from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, WatchlistViewSet

router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'watchlist', WatchlistViewSet, basename='watchlist')

urlpatterns = [
    path('', include(router.urls)),
]
