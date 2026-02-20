from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/v1/order/', include('orders.urls')),
    path('api/v1/order/disputes/', include('disputes.urls')),
]
