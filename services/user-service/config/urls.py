from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/v1/user/', include('users.urls')),
    path('api/v1/user/feedback/', include('feedback.urls')),
]
