import os
import pymongo
from elasticsearch import Elasticsearch
from bson import ObjectId
from datetime import datetime

class SearchService:
    def __init__(self):
        self.es = Elasticsearch(
            hosts=[os.environ.get('ELASTICSEARCH_URL', 'http://elasticsearch:9200')]
        )
        self.index_name = 'dbay-listings'
        
        self.mongo_uri = os.environ.get('MONGO_URI', 'mongodb://dbay_mongo_user:dbay_mongo_password@mongodb:27017/dbay?authSource=admin')
        self.mongo_client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.mongo_client.get_database()
        self.saved_searches = self.db.saved_searches

    def search(self, query_params):
        """
        Build and execute ES query based on params:
        q, category, price_min, price_max, sort, from, size
        """
        q = query_params.get('q')
        category_id = query_params.get('category_id')
        price_min = query_params.get('price_min')
        price_max = query_params.get('price_max')
        sort = query_params.get('sort', 'created_at:desc')
        from_ = int(query_params.get('from', 0))
        size = int(query_params.get('size', 20))

        must = []
        if q:
            must.append({
                "multi_match": {
                    "query": q,
                    "fields": ["title^3", "description", "tags"],
                    "fuzziness": "AUTO"
                }
            })
        else:
            must.append({"match_all": {}})

        filter_ = [{"term": {"status": "ACTIVE"}}]
        
        if category_id:
            filter_.append({"term": {"category_id": category_id}})
            
        if price_min or price_max:
            range_query = {"current_price": {}}
            if price_min:
                range_query["current_price"]["gte"] = float(price_min)
            if price_max:
                range_query["current_price"]["lte"] = float(price_max)
            filter_.append({"range": range_query})

        sort_field, sort_order = sort.split(':') if ':' in sort else ('created_at', 'desc')
        
        body = {
            "query": {
                "bool": {
                    "must": must,
                    "filter": filter_
                }
            },
            "sort": [{sort_field: {"order": sort_order}}],
            "from": from_,
            "size": size,
            "aggs": {
                "categories": {
                    "terms": {"field": "category_id", "size": 20}
                },
                "price_ranges": {
                     "histogram": {
                         "field": "current_price",
                         "interval": 50
                     }
                }
            }
        }

        return self.es.search(index=self.index_name, body=body)

    def save_search(self, user_id, name, query_params):
        doc = {
            "user_id": user_id,
            "name": name,
            "query": query_params,
            "created_at": datetime.utcnow()
        }
        result = self.saved_searches.insert_one(doc)
        return str(result.inserted_id)

    def get_saved_searches(self, user_id):
        cursor = self.saved_searches.find({"user_id": user_id}).sort("created_at", -1)
        results = []
        for doc in cursor:
            doc['id'] = str(doc.pop('_id'))
            results.append(doc)
        return results

    def delete_saved_search(self, search_id, user_id):
        self.saved_searches.delete_one({"_id": ObjectId(search_id), "user_id": user_id})

search_service = SearchService()
