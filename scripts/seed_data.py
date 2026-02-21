#!/usr/bin/env python3
"""
Seed categories, category items, and sample listings for dBay.

Run from repo root:
  python scripts/seed_data.py

Or from listing-service (recommended):
  cd services/listing-service && python manage.py seed_data
"""

import os
import sys

# Add listing-service to path and set up Django when run as standalone script
_script_dir = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.abspath(os.path.join(_script_dir, ".."))
_listing_service = os.path.join(_repo_root, "services", "listing-service")
if os.path.isdir(_listing_service):
    sys.path.insert(0, _listing_service)
    os.chdir(_listing_service)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()

from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from categories.models import Category, CategoryItem
from listings.models import Listing

# ltree path for root categories
def path_for(name):
    slug = name.lower().replace(" ", "_").replace("'", "").replace("&", "and")
    return slug

CATEGORIES_WITH_ITEMS = [
    ("Automobiles", [
        "Tesla", "Hyundai", "Honda", "Toyota", "Ford", "BMW", "Mercedes", "Chevrolet",
    ]),
    ("Men's Apparel", [
        "T-shirts", "Hoodies", "Shorts", "Jeans", "Jackets", "Sneakers", "Boots", "Accessories",
    ]),
    ("Women's Apparel", [
        "Dresses", "Tops", "Pants", "Skirts", "Sweaters", "Shoes", "Bags", "Jewelry",
    ]),
    ("Electronics", [
        "Phones", "Laptops", "Tablets", "Cameras", "Headphones", "Gaming", "Smart Home", "Accessories",
    ]),
    ("Home & Garden", [
        "Furniture", "Decor", "Kitchen", "Outdoor", "Tools", "Lighting", "Bedding", "Plants",
    ]),
    ("Sports", [
        "Cycling", "Running", "Fitness", "Camping", "Water Sports", "Winter Sports", "Team Sports", "Golf",
    ]),
    ("Toys & Games", [
        "Board Games", "Video Games", "Action Figures", "Puzzles", "Outdoor Toys", "Educational", "Collectibles", "Card Games",
    ]),
    ("Books", [
        "Fiction", "Non-Fiction", "Children's", "Textbooks", "Comics", "Cookbooks", "Art", "Reference",
    ]),
    ("Collectibles", [
        "Coins", "Stamps", "Trading Cards", "Memorabilia", "Vintage", "Art", "Antiques", "Figurines",
    ]),
    ("Jewelry", [
        "Rings", "Necklaces", "Earrings", "Bracelets", "Watches", "Body Jewelry", "Vintage", "Custom",
    ]),
]

# Fake seller UUID for seed listings
SEED_SELLER_ID = "11111111-1111-1111-1111-111111111111"


def run():
    from django.db import transaction

    with transaction.atomic():
        for idx, (cat_name, items) in enumerate(CATEGORIES_WITH_ITEMS):
            slug = path_for(cat_name)
            path = slug
            cat, _ = Category.objects.get_or_create(
                path=path,
                defaults={"name": cat_name, "slug": slug, "sort_order": idx},
            )
            for i, item_name in enumerate(items):
                CategoryItem.objects.get_or_create(
                    category=cat,
                    name=item_name,
                    defaults={"sort_order": i},
                )

        # Create 1-3 listings per category item
        for cat_name, items in CATEGORIES_WITH_ITEMS:
            cat = Category.objects.get(slug=path_for(cat_name))
            for item_name in items:
                item = CategoryItem.objects.get(category=cat, name=item_name)
                count = 2  # 2 listings per item (plan said 1-3)
                for n in range(count):
                    title = f"{item_name} - Sample Listing {n+1}"
                    if Listing.objects.filter(title=title, category=cat).exists():
                        continue
                    end_time = timezone.now() + timedelta(days=7)
                    Listing.objects.create(
                        seller_id=SEED_SELLER_ID,
                        category=cat,
                        title=title,
                        description=f"Great {item_name} listing. Category: {cat_name}.",
                        condition="GOOD",
                        listing_type="AUCTION" if n % 2 == 0 else "BUY_IT_NOW",
                        starting_price=Decimal("10.00"),
                        current_price=Decimal("10.00"),
                        buy_it_now_price=Decimal("50.00") if n % 2 == 1 else None,
                        status="ACTIVE",
                        shipping_from_country="US",
                        end_time=end_time,
                    )
    print("Seed complete: categories, items, and sample listings created.")


if __name__ == "__main__":
    if "DJANGO_SETTINGS_MODULE" not in os.environ and not os.path.isdir(_listing_service):
        print("Run from repo root: python scripts/seed_data.py")
        print("Or from listing-service: python manage.py seed_data")
        sys.exit(1)
    run()
