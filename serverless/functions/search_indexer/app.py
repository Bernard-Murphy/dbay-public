import json
import os
import logging
from elasticsearch import Elasticsearch

logger = logging.getLogger()
logger.setLevel(logging.INFO)

es = Elasticsearch(
    hosts=[os.environ.get('ELASTICSEARCH_URL', 'http://elasticsearch:9200')]
)
INDEX_NAME = 'dbay-listings'

def lambda_handler(event, context):
    try:
        detail = event.get('detail', {})
        detail_type = event.get('detail-type')
        listing_id = detail.get('id')
        
        if not listing_id:
             logger.error("No listing ID in event detail")
             return
             
        if detail_type in ['listing.created', 'listing.updated']:
            # Transform for ES
            doc = {
                'listing_id': listing_id,
                'title': detail.get('title'),
                'description': detail.get('description'),
                'category_id': detail.get('category_id'),
                'current_price': float(detail.get('current_price', 0)),
                'status': detail.get('status'),
                'created_at': detail.get('created_at'),
                # Add other fields as needed
            }
            
            es.index(index=INDEX_NAME, id=listing_id, document=doc)
            logger.info(f"Indexed listing {listing_id}")
            
        elif detail_type == 'listing.deleted':
            es.delete(index=INDEX_NAME, id=listing_id)
            logger.info(f"Deleted listing {listing_id} from index")
            
    except Exception as e:
        logger.error(f"Error indexing listing: {e}")
        raise e
