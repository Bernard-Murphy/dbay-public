import os

services = {
    'listing-service': ['listings', 'categories', 'questions'],
    'auction-service': ['auctions'],
    'wallet-service': ['wallet'],
    'user-service': ['users', 'feedback'],
    'order-service': ['orders', 'disputes'],
}

for service, apps in services.items():
    for app in apps:
        base_path = f'services/{service}/{app}'
        os.makedirs(base_path, exist_ok=True)
        
        # Create standard Django app files
        files = ['__init__.py', 'models.py', 'serializers.py', 'views.py', 'urls.py', 'apps.py', 'admin.py', 'services.py', 'events.py']
        for file in files:
            with open(f'{base_path}/{file}', 'w') as f:
                if file == 'apps.py':
                    f.write(f"from django.apps import AppConfig\n\nclass {app.capitalize()}Config(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = '{app}'\n")
                elif file == 'models.py':
                    f.write("from django.db import models\n\n# Create your models here.\n")
                elif file == 'views.py':
                    f.write("from django.shortcuts import render\nfrom rest_framework import viewsets\n\n# Create your views here.\n")
                elif file == 'admin.py':
                    f.write("from django.contrib import admin\n\n# Register your models here.\n")
                elif file == 'urls.py':
                    f.write("from django.urls import path, include\nfrom rest_framework.routers import DefaultRouter\n\nrouter = DefaultRouter()\n\nurlpatterns = [\n    path('', include(router.urls)),\n]\n")

print("Django apps structure created.")
