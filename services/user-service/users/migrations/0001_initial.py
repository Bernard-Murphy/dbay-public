# Initial migration: User, UserAddress, SellerRating

import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("username", models.CharField(max_length=150, unique=True)),
                ("display_name", models.CharField(blank=True, max_length=150)),
                ("avatar_url", models.URLField(blank=True, null=True)),
                ("cognito_sub", models.CharField(max_length=255, unique=True)),
                ("seller_verified", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="UserAddress",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("street", models.CharField(max_length=255)),
                ("city", models.CharField(max_length=100)),
                ("state", models.CharField(max_length=100)),
                ("zip_code", models.CharField(max_length=20)),
                ("country", models.CharField(max_length=100)),
                ("is_default", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="addresses", to="users.user")),
            ],
        ),
        migrations.CreateModel(
            name="SellerRating",
            fields=[
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name="seller_rating", serialize=False, to="users.user")),
                ("positive_count", models.IntegerField(default=0)),
                ("neutral_count", models.IntegerField(default=0)),
                ("negative_count", models.IntegerField(default=0)),
                ("score", models.DecimalField(decimal_places=2, default=0.00, max_digits=5)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
