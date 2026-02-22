import os
import random
import uuid
from decimal import Decimal
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from categories.models import Category, CategoryItem
from listings.models import Listing


def path_for(name):
    return name.lower().replace(" ", "_").replace("'", "").replace("&", "and")


CATEGORY_DEFAULT_ICONS = {
    "Automobiles": "car",
    "Men's Apparel": "shirt",
    "Women's Apparel": "shirt",
    "Electronics": "smartphone",
    "Home & Garden": "home",
    "Sports": "circle-dot",
    "Toys & Games": "gamepad-2",
    "Books": "book-open",
    "Collectibles": "star",
    "Jewelry": "gem",
}

CATEGORIES_WITH_ITEMS = [
    ("Automobiles", ["Tesla", "Hyundai", "Honda", "Toyota", "Ford", "BMW", "Mercedes", "Chevrolet", "Other"]),
    ("Men's Apparel", ["T-shirts", "Hoodies", "Shorts", "Jeans", "Jackets", "Sneakers", "Boots", "Accessories", "Other"]),
    ("Women's Apparel", ["Dresses", "Tops", "Pants", "Skirts", "Sweaters", "Shoes", "Bags", "Jewelry", "Other"]),
    ("Electronics", ["Phones", "Laptops", "Tablets", "Cameras", "Headphones", "Gaming", "Smart Home", "Accessories", "Other"]),
    ("Home & Garden", ["Furniture", "Decor", "Kitchen", "Outdoor", "Tools", "Lighting", "Bedding", "Plants", "Other"]),
    ("Sports", ["Cycling", "Running", "Fitness", "Camping", "Water Sports", "Winter Sports", "Team Sports", "Golf", "Other"]),
    ("Toys & Games", ["Board Games", "Video Games", "Action Figures", "Puzzles", "Outdoor Toys", "Educational", "Collectibles", "Card Games", "Other"]),
    ("Books", ["Fiction", "Non-Fiction", "Children's", "Textbooks", "Comics", "Cookbooks", "Art", "Reference", "Other"]),
    ("Collectibles", ["Coins", "Stamps", "Trading Cards", "Memorabilia", "Vintage", "Art", "Antiques", "Figurines", "Other"]),
    ("Jewelry", ["Rings", "Necklaces", "Earrings", "Bracelets", "Watches", "Body Jewelry", "Vintage", "Custom", "Other"]),
]

SEED_USER_IDS = [str(uuid.uuid4()) for _ in range(100)]
SEED_USERNAME_WORDS = [
    "surfer", "skate", "bookworm", "gamer", "travel", "music", "art", "tech",
    "vintage", "craft", "fitness", "chef", "photo", "garden", "motor", "wave",
    "star", "river", "mountain", "ocean", "sunny", "cosmic", "lucky", "bold",
]
def _gen_seed_usernames(n=100):
    seen = set()
    out = []
    while len(out) < n:
        word = random.choice(SEED_USERNAME_WORDS)
        num = random.randint(10, 999)
        u = f"{word}{num}"
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out
SEED_USERNAMES = _gen_seed_usernames(100)
SEED_DOGE_RATE = Decimal("0.10")
PRICE_RANGE_USD = {
    "Automobiles": (30_000, 85_000),
    "Men's Apparel": (15, 200),
    "Women's Apparel": (20, 250),
    "Electronics": (50, 2_500),
    "Home & Garden": (25, 1_500),
    "Sports": (30, 800),
    "Toys & Games": (10, 150),
    "Books": (5, 80),
    "Collectibles": (20, 5_000),
    "Jewelry": (25, 3_000),
}
def _price_doge(cat_name):
    lo, hi = PRICE_RANGE_USD.get(cat_name, (50, 500))
    usd = random.uniform(lo, hi)
    return int(Decimal(str(usd)) / SEED_DOGE_RATE)

def _seed_bids(auction_listings):
    try:
        import requests
    except ImportError:
        return
    base = os.environ.get("AUCTION_SERVICE_URL", "http://localhost:8002")
    to_bid = [l for l in auction_listings if random.random() < 0.75]
    for listing in to_bid:
        try:
            start = int(listing.starting_price)
            num_bids = random.randint(1, 10)
            for i in range(num_bids):
                amount = start + (i + 1) * max(1, start // 20)
                bidder_id = random.choice(SEED_USER_IDS)
                r = requests.post(
                    f"{base}/api/v1/auction/auctions/{listing.id}/bid/",
                    json={"amount": amount},
                    headers={"X-User-ID": bidder_id, "Content-Type": "application/json"},
                    timeout=5,
                )
                if r.status_code not in (200, 201):
                    break
        except Exception:
            pass

# Realistic listing titles per (category_name, item_name). Two titles per item.
SEED_LISTING_TITLES = {
    ("Automobiles", "Tesla"): ["2024 Tesla Model X Plaid (20k miles)", "2022 Tesla Model 3 Long Range"],
    ("Automobiles", "Hyundai"): ["2023 Hyundai Ioniq 5 SEL", "Hyundai Tucson Hybrid 2022"],
    ("Automobiles", "Honda"): ["Honda Civic 2021 EX", "Honda CR-V 2023 AWD"],
    ("Automobiles", "Toyota"): ["Toyota Camry 2022 LE", "Toyota RAV4 Hybrid XLE"],
    ("Automobiles", "Ford"): ["Ford F-150 2023 XLT", "Ford Mustang Mach-E"],
    ("Automobiles", "BMW"): ["BMW 330i 2022", "BMW X5 2023"],
    ("Automobiles", "Mercedes"): ["Mercedes C300 2022", "Mercedes EQB 250"],
    ("Automobiles", "Chevrolet"): ["Chevrolet Silverado 1500 2022", "Chevy Bolt EV 2023"],
    ("Electronics", "Laptops"): ["Dell XPS 15 BRAND NEW", "MacBook Pro 14 M3 Pro"],
    ("Electronics", "Phones"): ["iPhone 15 Pro 256GB", "Samsung Galaxy S24 Ultra"],
    ("Electronics", "Tablets"): ["iPad Pro 12.9\" M2", "Samsung Tab S9"],
    ("Electronics", "Cameras"): ["Sony A7 IV Body", "Canon R6 Mark II"],
    ("Electronics", "Headphones"): ["Sony WH-1000XM5", "AirPods Pro 2"],
    ("Electronics", "Gaming"): ["PlayStation 5 Console", "Xbox Series X"],
    ("Electronics", "Smart Home"): ["Nest Learning Thermostat", "Ring Video Doorbell Pro"],
    ("Electronics", "Accessories"): ["Anker 737 Power Bank", "Logitech MX Master 3S"],
    ("Men's Apparel", "T-shirts"): ["Plain White Cotton Tee Pack of 3", "Vintage Band Graphic Tee"],
    ("Men's Apparel", "Hoodies"): ["Champion Reverse Weave Hoodie", "Nike Tech Fleece"],
    ("Men's Apparel", "Jeans"): ["Levi's 501 Original", "Wrangler Authentics Straight"],
    ("Women's Apparel", "Dresses"): ["Summer Floral Midi Dress", "Little Black Dress Size M"],
    ("Women's Apparel", "Shoes"): ["Steve Madden Heels 8", "Birkenstock Arizona Sandals"],
    ("Home & Garden", "Furniture"): ["IKEA KALLAX Shelf Unit", "West Elm Mid-Century Desk"],
    ("Home & Garden", "Kitchen"): ["KitchenAid Stand Mixer", "Ninja Foodi 8-in-1"],
    ("Sports", "Cycling"): ["Trek Domane AL 3", "Garmin Edge 1040"],
    ("Sports", "Running"): ["Nike Pegasus 40", "Garmin Forerunner 265"],
    ("Sports", "Golf"): ["Callaway Rogue Driver", "Titleist Pro V1 Dozen"],
    ("Toys & Games", "Board Games"): ["Catan 5th Edition", "Ticket to Ride Europe"],
    ("Toys & Games", "Video Games"): ["Zelda Tears of the Kingdom", "Elden Ring PS5"],
    ("Books", "Fiction"): ["Project Hail Mary Hardcover", "Fourth Wing First Edition"],
    ("Books", "Non-Fiction"): ["Atomic Habits James Clear", "Sapiens Yuval Harari"],
    ("Collectibles", "Trading Cards"): ["Charizard Holo PSA 9", "Michael Jordan Rookie Card"],
    ("Jewelry", "Watches"): ["Seiko 5 Automatic", "Casio G-Shock DW5600"],
    ("Jewelry", "Rings"): ["Sterling Silver Band", "Moissanite Solitaire"],
}


def get_seed_titles(cat_name, item_name, n):
    """Return realistic title for (cat_name, item_name) index n, or fallback."""
    key = (cat_name, item_name)
    if key in SEED_LISTING_TITLES:
        titles = SEED_LISTING_TITLES[key]
        if n < len(titles):
            return titles[n]
    return f"{item_name} — {cat_name} listing {n + 1}"


class Command(BaseCommand):
    help = "Seed categories, category items, and sample listings."

    def handle(self, *args, **options):
        with transaction.atomic():
            for idx, (cat_name, items) in enumerate(CATEGORIES_WITH_ITEMS):
                slug = path_for(cat_name)
                path = slug
                cat, _ = Category.objects.get_or_create(
                    path=path,
                    defaults={
                        "name": cat_name,
                        "slug": slug,
                        "sort_order": idx,
                        "default_icon": CATEGORY_DEFAULT_ICONS.get(cat_name, ""),
                    },
                )
                if not cat.default_icon and cat_name in CATEGORY_DEFAULT_ICONS:
                    cat.default_icon = CATEGORY_DEFAULT_ICONS[cat_name]
                    cat.save()
                for i, item_name in enumerate(items):
                    CategoryItem.objects.get_or_create(
                        category=cat,
                        name=item_name,
                        defaults={"sort_order": i},
                    )

            now = timezone.now()
            end_time = now + timedelta(days=14)
            created_auction_listings = []
            for cat_name, items in CATEGORIES_WITH_ITEMS:
                cat = Category.objects.get(slug=path_for(cat_name))
                for item_name in items:
                    if item_name == "Other":
                        continue
                    count = random.randint(20, 30)
                    for n in range(count):
                        title = get_seed_titles(cat_name, item_name, n)
                        if Listing.objects.filter(title=title, category=cat).exists():
                            continue
                        price_doge = _price_doge(cat_name)
                        seller_id = random.choice(SEED_USER_IDS)
                        is_auction = n % 2 == 0
                        start_price = max(1, price_doge - random.randint(0, min(price_doge // 10, 1000)))
                        listing = Listing.objects.create(
                            seller_id=seller_id,
                            category=cat,
                            title=title,
                            description=f"Great {item_name} listing. Category: {cat_name}.",
                            condition="GOOD",
                            listing_type="AUCTION" if is_auction else "BUY_IT_NOW",
                            starting_price=Decimal(str(start_price)),
                            current_price=Decimal(str(start_price)),
                            buy_it_now_price=Decimal(str(price_doge)) if not is_auction else None,
                            status="ACTIVE",
                            shipping_from_country="US",
                            start_time=now,
                            end_time=end_time,
                        )
                        if is_auction:
                            created_auction_listings.append(listing)
        self.stdout.write(self.style.SUCCESS("Seed complete: categories, items, and sample listings created."))
        _seed_bids(created_auction_listings)
