# Generated migration for Listing, ListingImage, Watchlist

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("categories", "0002_categoryitem"),
    ]

    operations = [
        migrations.CreateModel(
            name="Listing",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("seller_id", models.UUIDField()),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("condition", models.CharField(choices=[("NEW", "New"), ("LIKE_NEW", "Like New"), ("GOOD", "Good"), ("FAIR", "Fair"), ("POOR", "Poor")], max_length=20)),
                ("listing_type", models.CharField(choices=[("AUCTION", "Auction"), ("BUY_IT_NOW", "Buy It Now"), ("BOTH", "Both")], max_length=20)),
                ("buy_it_now_price", models.DecimalField(blank=True, decimal_places=8, max_digits=20, null=True)),
                ("starting_price", models.DecimalField(blank=True, decimal_places=8, max_digits=20, null=True)),
                ("reserve_price", models.DecimalField(blank=True, decimal_places=8, max_digits=20, null=True)),
                ("current_price", models.DecimalField(decimal_places=8, default=0.0, max_digits=20)),
                ("quantity", models.IntegerField(default=1)),
                ("quantity_sold", models.IntegerField(default=0)),
                ("start_time", models.DateTimeField(blank=True, null=True)),
                ("end_time", models.DateTimeField(blank=True, null=True)),
                ("status", models.CharField(choices=[("DRAFT", "Draft"), ("ACTIVE", "Active"), ("ENDED", "Ended"), ("SOLD", "Sold"), ("CANCELLED", "Cancelled")], default="DRAFT", max_length=20)),
                ("view_count", models.IntegerField(default=0)),
                ("watch_count", models.IntegerField(default=0)),
                ("shipping_cost", models.DecimalField(decimal_places=8, default=0.0, max_digits=20)),
                ("shipping_from_country", models.CharField(max_length=100)),
                ("returns_accepted", models.BooleanField(default=False)),
                ("return_period_days", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="listings", to="categories.category")),
            ],
        ),
        migrations.CreateModel(
            name="ListingImage",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("s3_key", models.CharField(max_length=1024)),
                ("url_thumb", models.URLField(blank=True, null=True)),
                ("url_medium", models.URLField(blank=True, null=True)),
                ("url_large", models.URLField(blank=True, null=True)),
                ("sort_order", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("listing", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="images", to="listings.listing")),
            ],
            options={
                "ordering": ["sort_order"],
            },
        ),
        migrations.CreateModel(
            name="Watchlist",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_id", models.UUIDField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("listing", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="watchers", to="listings.listing")),
            ],
            options={
                "unique_together": {("user_id", "listing")},
            },
        ),
    ]
