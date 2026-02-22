import os
from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch

from listings.models import Listing


INDEX_NAME = "dbay-listings"


def listing_to_doc(listing: Listing) -> dict:
    """Build ES document in the same shape as the search_indexer Lambda."""
    images = []
    for img in listing.images.all().order_by("sort_order"):
        images.append({
            "url_thumb": img.url_thumb,
            "url_medium": img.url_medium,
            "url_large": img.url_large,
        })
    return {
        "listing_id": str(listing.id),
        "title": listing.title,
        "description": listing.description or "",
        "category_id": str(listing.category_id),
        "listing_type": listing.listing_type,
        "current_price": float(listing.current_price or 0),
        "status": listing.status,
        "created_at": listing.created_at.isoformat() if listing.created_at else None,
        "end_time": listing.end_time.isoformat() if listing.end_time else None,
        "images": images,
    }


class Command(BaseCommand):
    help = "Backfill Elasticsearch index dbay-listings with ACTIVE listings from the database."

    def handle(self, *args, **options):
        es_url = os.environ.get("ELASTICSEARCH_URL", "http://elasticsearch:9200")
        es = Elasticsearch(hosts=[es_url])

        qs = Listing.objects.filter(status="ACTIVE").select_related("category").prefetch_related("images")
        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("No ACTIVE listings found. Nothing to index."))
            return

        indexed = 0
        for listing in qs:
            doc = listing_to_doc(listing)
            es.index(index=INDEX_NAME, id=str(listing.id), document=doc)
            indexed += 1

        self.stdout.write(self.style.SUCCESS(f"Indexed {indexed} listing(s) into {INDEX_NAME}."))
