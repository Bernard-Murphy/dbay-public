from decimal import Decimal
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from categories.models import Category, CategoryItem
from listings.models import Listing


def path_for(name):
    return name.lower().replace(" ", "_").replace("'", "").replace("&", "and")


CATEGORIES_WITH_ITEMS = [
    ("Automobiles", ["Tesla", "Hyundai", "Honda", "Toyota", "Ford", "BMW", "Mercedes", "Chevrolet"]),
    ("Men's Apparel", ["T-shirts", "Hoodies", "Shorts", "Jeans", "Jackets", "Sneakers", "Boots", "Accessories"]),
    ("Women's Apparel", ["Dresses", "Tops", "Pants", "Skirts", "Sweaters", "Shoes", "Bags", "Jewelry"]),
    ("Electronics", ["Phones", "Laptops", "Tablets", "Cameras", "Headphones", "Gaming", "Smart Home", "Accessories"]),
    ("Home & Garden", ["Furniture", "Decor", "Kitchen", "Outdoor", "Tools", "Lighting", "Bedding", "Plants"]),
    ("Sports", ["Cycling", "Running", "Fitness", "Camping", "Water Sports", "Winter Sports", "Team Sports", "Golf"]),
    ("Toys & Games", ["Board Games", "Video Games", "Action Figures", "Puzzles", "Outdoor Toys", "Educational", "Collectibles", "Card Games"]),
    ("Books", ["Fiction", "Non-Fiction", "Children's", "Textbooks", "Comics", "Cookbooks", "Art", "Reference"]),
    ("Collectibles", ["Coins", "Stamps", "Trading Cards", "Memorabilia", "Vintage", "Art", "Antiques", "Figurines"]),
    ("Jewelry", ["Rings", "Necklaces", "Earrings", "Bracelets", "Watches", "Body Jewelry", "Vintage", "Custom"]),
]

SEED_SELLER_ID = "11111111-1111-1111-1111-111111111111"


class Command(BaseCommand):
    help = "Seed categories, category items, and sample listings."

    def handle(self, *args, **options):
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

            for cat_name, items in CATEGORIES_WITH_ITEMS:
                cat = Category.objects.get(slug=path_for(cat_name))
                for item_name in items:
                    count = 2
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
        self.stdout.write(self.style.SUCCESS("Seed complete: categories, items, and sample listings created."))
