import os
import pymongo
from urllib.parse import urlparse

class MongoService:
    def __init__(self):
        self.mongo_uri = os.environ.get('MONGO_URI', 'mongodb://dbay_mongo_user:dbay_mongo_password@mongodb:27017/dbay?authSource=admin')
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client.get_database()

    def get_collection(self, collection_name):
        return self.db[collection_name]

mongo = MongoService()
