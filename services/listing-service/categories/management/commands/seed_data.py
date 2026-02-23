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

# Deterministic IDs and usernames (must match user-service seed_users)
SEED_USERNAME_WORDS = [
    "surfer", "skate", "bookworm", "gamer", "travel", "music", "art", "tech",
    "vintage", "craft", "fitness", "chef", "photo", "garden", "motor", "wave",
    "star", "river", "mountain", "ocean", "sunny", "cosmic", "lucky", "bold",
]
SEED_USER_IDS = [str(uuid.uuid5(uuid.NAMESPACE_DNS, f"dbay.seed.user.{i}")) for i in range(100)]
SEED_USERNAMES = [f"{SEED_USERNAME_WORDS[i % len(SEED_USERNAME_WORDS)]}{10 + i}" for i in range(100)]
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
    for listing in auction_listings:
        try:
            start = int(listing.starting_price)
            num_bids = random.randint(0, 5)
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

# Realistic listing titles per (category_name, item_name). Extended for 20-30 listings per item.
SEED_LISTING_TITLES = {
    ("Automobiles", "Tesla"): ["2024 Tesla Model X Plaid (20k miles)", "2022 Tesla Model 3 Long Range", "2023 Tesla Model Y AWD", "Tesla Model S Plaid 2023", "2021 Tesla Model 3 SR+"],
    ("Automobiles", "Hyundai"): ["2023 Hyundai Ioniq 5 SEL", "Hyundai Tucson Hybrid 2022", "Hyundai Kona Electric 2024", "Hyundai Santa Fe 2023"],
    ("Automobiles", "Honda"): ["Honda Civic 2021 EX", "Honda CR-V 2023 AWD", "Honda Accord 2022 Touring", "Honda Pilot 2023"],
    ("Automobiles", "Toyota"): ["Toyota Camry 2022 LE", "Toyota RAV4 Hybrid XLE", "Toyota Highlander 2023", "Toyota 4Runner TRD Off-Road"],
    ("Automobiles", "Ford"): ["Ford F-150 2023 XLT", "Ford Mustang Mach-E", "Ford Bronco Sport 2022", "Ford Explorer ST 2023"],
    ("Automobiles", "BMW"): ["BMW 330i 2022", "BMW X5 2023", "BMW i4 eDrive40 2024", "BMW M3 Competition"],
    ("Automobiles", "Mercedes"): ["Mercedes C300 2022", "Mercedes EQB 250", "Mercedes E-Class 2023", "Mercedes GLC 300"],
    ("Automobiles", "Chevrolet"): ["Chevrolet Silverado 1500 2022", "Chevy Bolt EV 2023", "Chevrolet Tahoe 2023", "Camaro 2SS 2022"],
    ("Electronics", "Laptops"): ["Dell XPS 15 BRAND NEW", "MacBook Pro 14 M3 Pro", "Lenovo ThinkPad X1 Carbon", "ASUS ROG Zephyrus G14"],
    ("Electronics", "Phones"): ["iPhone 15 Pro 256GB", "Samsung Galaxy S24 Ultra", "Google Pixel 8 Pro", "OnePlus 12 256GB"],
    ("Electronics", "Tablets"): ["iPad Pro 12.9\" M2", "Samsung Tab S9", "Microsoft Surface Pro 9", "iPad Air 5th Gen"],
    ("Electronics", "Cameras"): ["Sony A7 IV Body", "Canon R6 Mark II", "Nikon Z8", "Fujifilm X-T5"],
    ("Electronics", "Headphones"): ["Sony WH-1000XM5", "AirPods Pro 2", "Bose QuietComfort Ultra", "Sennheiser HD 660S"],
    ("Electronics", "Gaming"): ["PlayStation 5 Console", "Xbox Series X", "Nintendo Switch OLED", "Steam Deck 256GB"],
    ("Electronics", "Smart Home"): ["Nest Learning Thermostat", "Ring Video Doorbell Pro", "Echo Dot 5th Gen", "Philips Hue Starter Kit"],
    ("Electronics", "Accessories"): ["Anker 737 Power Bank", "Logitech MX Master 3S", "Samsung T7 1TB SSD", "Apple Magic Keyboard"],
    ("Men's Apparel", "T-shirts"): ["Plain White Cotton Tee Pack of 3", "Vintage Band Graphic Tee", "Nike Dri-FIT Training Tee", "Carhartt Pocket T-Shirt"],
    ("Men's Apparel", "Hoodies"): ["Champion Reverse Weave Hoodie", "Nike Tech Fleece", "Carhartt Midweight Hoodie", "Patagonia Better Sweater"],
    ("Men's Apparel", "Shorts"): ["Nike Dri-FIT Running Shorts", "Chubbies Classic 5.5\"", "Patagonia Baggies"],
    ("Men's Apparel", "Jeans"): ["Levi's 501 Original", "Wrangler Authentics Straight", "Wrangler Relaxed Fit", "Lee Regular Fit"],
    ("Men's Apparel", "Jackets"): ["Carhartt Active Jacket", "Patagonia Nano Puff", "North Face Denali 2"],
    ("Men's Apparel", "Sneakers"): ["Nike Air Max 90", "Adidas Ultraboost 22", "New Balance 574"],
    ("Men's Apparel", "Boots"): ["Timberland 6\" Premium", "Red Wing Iron Ranger", "Wolverine 1000 Mile"],
    ("Men's Apparel", "Accessories"): ["Leather Belt Brown", "Casio Watch", "Ray-Ban Aviator"],
    ("Women's Apparel", "Dresses"): ["Summer Floral Midi Dress", "Little Black Dress Size M", "Anthropologie Maxi Dress", "Reformation Silk Dress"],
    ("Women's Apparel", "Tops"): ["Silk Blouse White", "Free People Off Shoulder", "Zara Linen Button-Up"],
    ("Women's Apparel", "Pants"): ["High-Waist Wide Leg", "Lululemon Align 25\"", "Levi's 721 High Rise"],
    ("Women's Apparel", "Skirts"): ["Pleated Midi Skirt", "Denim Mini Skirt", "A-Line Wool Skirt"],
    ("Women's Apparel", "Sweaters"): ["Cashmere Crewneck Gray", "Oversized Cardigan", "Turtleneck Sweater"],
    ("Women's Apparel", "Shoes"): ["Steve Madden Heels 8", "Birkenstock Arizona Sandals", "Dr. Martens 1460", "UGG Classic Short"],
    ("Women's Apparel", "Bags"): ["Leather Crossbody Bag", "Longchamp Tote", "Vintage Coach Bag"],
    ("Women's Apparel", "Jewelry"): ["Gold Hoop Earrings", "Pearl Necklace", "Stackable Rings Set"],
    ("Home & Garden", "Furniture"): ["IKEA KALLAX Shelf Unit", "West Elm Mid-Century Desk", "Article Sven Charme Sofa", "CB2 Acorn Coffee Table"],
    ("Home & Garden", "Decor"): ["Ceramic Vase Set", "Framed Abstract Art", "Throw Pillow Set"],
    ("Home & Garden", "Kitchen"): ["KitchenAid Stand Mixer", "Ninja Foodi 8-in-1", "Vitamix 5200", "Le Creuset Dutch Oven"],
    ("Home & Garden", "Outdoor"): ["Weber Spirit Grill", "Patio Dining Set", "String Lights 48ft"],
    ("Home & Garden", "Tools"): ["DeWalt 20V Drill", "Craftsman Tool Set", "Milwaukee M18 Impact"],
    ("Home & Garden", "Lighting"): ["Philips Hue Bridge", "Table Lamp Ceramic", "LED Strip Lights"],
    ("Home & Garden", "Bedding"): ["Brooklinen Sheet Set Queen", "Down Comforter King", "Memory Foam Pillow"],
    ("Home & Garden", "Plants"): ["Monstera Deliciosa Potted", "Snake Plant Large", "Pothos Hanging Basket"],
    ("Sports", "Cycling"): ["Trek Domane AL 3", "Garmin Edge 1040", "Specialized Sirrus 2.0", "Peloton Bike"],
    ("Sports", "Running"): ["Nike Pegasus 40", "Garmin Forerunner 265", "Brooks Ghost 15", "Apple Watch Ultra"],
    ("Sports", "Fitness"): ["Bowflex SelectTech Dumbbells", "Yoga Mat Manduka", "Resistance Bands Set"],
    ("Sports", "Camping"): ["REI Half Dome Tent", "Yeti Tundra 45", "Petzl Headlamp"],
    ("Sports", "Water Sports"): ["Oru Kayak Beach LT", "Body Glove Paddle Board", "Snorkel Set"],
    ("Sports", "Winter Sports"): ["Burton Custom Snowboard", "K2 Skis 170cm", "Smith Helmet"],
    ("Sports", "Team Sports"): ["Wilson Football", "Spalding Basketball", "Franklin Bat"],
    ("Sports", "Golf"): ["Callaway Rogue Driver", "Titleist Pro V1 Dozen", "TaylorMade Stealth Irons", "Nike Golf Shoes"],
    ("Toys & Games", "Board Games"): ["Catan 5th Edition", "Ticket to Ride Europe", "Wingspan", "Azul"],
    ("Toys & Games", "Video Games"): ["Zelda Tears of the Kingdom", "Elden Ring PS5", "Mario Kart 8 Deluxe", "Spider-Man 2 PS5"],
    ("Toys & Games", "Action Figures"): ["Star Wars Black Series", "Marvel Legends", "Funko Pop Set"],
    ("Toys & Games", "Puzzles"): ["Ravensburger 1000pc", "Liberty Puzzle Wooden", "Eurographics Map"],
    ("Toys & Games", "Card Games"): ["Pokemon Booster Box", "MTG Commander Deck", "Uno Flip"],
    ("Books", "Fiction"): ["Project Hail Mary Hardcover", "Fourth Wing First Edition", "The Midnight Library", "Where the Crawdads Sing"],
    ("Books", "Non-Fiction"): ["Atomic Habits James Clear", "Sapiens Yuval Harari", "Educated Tara Westover", "Thinking Fast and Slow"],
    ("Books", "Children's"): ["Goodnight Moon Board Book", "The Very Hungry Caterpillar", "Brown Bear Set"],
    ("Books", "Textbooks"): ["Calculus Early Transcendentals", "Organic Chemistry 3rd Ed", "Principles of Economics"],
    ("Books", "Comics"): ["Watchmen Graphic Novel", "Sandman Omnibus", "Maus Complete"],
    ("Collectibles", "Trading Cards"): ["Charizard Holo PSA 9", "Michael Jordan Rookie Card", "Mickey Mantle 1952", "Pikachu Illustrator"],
    ("Collectibles", "Coins"): ["American Silver Eagle", "Morgan Dollar 1889", "Gold Maple Leaf 1oz"],
    ("Collectibles", "Stamps"): ["Inverted Jenny", "British Guiana 1c", "Stamp Collection Album"],
    ("Jewelry", "Watches"): ["Seiko 5 Automatic", "Casio G-Shock DW5600", "Citizen Eco-Drive", "Tissot PRX"],
    ("Jewelry", "Rings"): ["Sterling Silver Band", "Moissanite Solitaire", "Vintage Signet Ring", "Tungsten Wedding Band"],
    ("Jewelry", "Necklaces"): ["Gold Chain 18in", "Sapphire Pendant", "Layered Necklace Set"],
    ("Jewelry", "Earrings"): ["Diamond Studs", "Hoop Earrings Gold", "Pearl Studs"],
    ("Jewelry", "Bracelets"): ["Tennis Bracelet", "Beaded Bracelet", "Leather Wrap"],
}


_TITLE_VARIANTS = ["excellent condition", "low miles", "like new", "well maintained", "recent model", "great shape", "clean", "minor wear"]


def get_seed_titles(cat_name, item_name, n):
    """Return realistic title for (cat_name, item_name) index n."""
    key = (cat_name, item_name)
    if key in SEED_LISTING_TITLES:
        titles = SEED_LISTING_TITLES[key]
        if n < len(titles):
            return titles[n]
        base = titles[-1] if titles else item_name
        return f"{base} ({_TITLE_VARIANTS[n % len(_TITLE_VARIANTS)]})"
    return f"{item_name} #{n + 1}"


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
                        defaults={
                            "sort_order": i,
                            "image_url": "https://feednana.com/random",
                        },
                    )

            now = timezone.now()
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
                        end_time = now + timedelta(days=random.randint(1, 14))
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
