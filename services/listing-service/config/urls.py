from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('api/v1/listings/', include('listings.urls')),
    path('api/v1/categories/', include('categories.urls')),
    path('api/v1/questions/', include('questions.urls')),
]
