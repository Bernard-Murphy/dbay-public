import os
import pymongo
from datetime import datetime
from bson import ObjectId

class MessagingService:
    def __init__(self):
        self.mongo_uri = os.environ.get('MONGO_URI', 'mongodb://dbay_mongo_user:dbay_mongo_password@mongodb:27017/dbay?authSource=admin')
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client.get_database()
        self.threads = self.db.message_threads

    def create_thread(self, participants, listing_id=None, order_id=None):
        # Check if thread exists
        participants.sort()
        query = {"participants": participants}
        if listing_id:
            query["listing_id"] = listing_id
            
        existing = self.threads.find_one(query)
        if existing:
            return str(existing['_id'])
            
        doc = {
            "participants": participants,
            "listing_id": listing_id,
            "order_id": order_id,
            "messages": [],
            "last_message_at": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        result = self.threads.insert_one(doc)
        return str(result.inserted_id)

    def send_message(self, thread_id, sender_id, body):
        message = {
            "sender_id": sender_id,
            "body": body,
            "read": False,
            "created_at": datetime.utcnow()
        }
        
        self.threads.update_one(
            {"_id": ObjectId(thread_id)},
            {
                "$push": {"messages": message},
                "$set": {"last_message_at": datetime.utcnow()}
            }
        )
        return message

    def get_threads(self, user_id):
        cursor = self.threads.find(
            {"participants": user_id},
            {"messages": {"$slice": -1}} # Only get last message for preview
        ).sort("last_message_at", -1)
        
        results = []
        for doc in cursor:
            doc['id'] = str(doc.pop('_id'))
            results.append(doc)
        return results

    def get_messages(self, thread_id):
        doc = self.threads.find_one({"_id": ObjectId(thread_id)})
        if not doc:
            return None
        doc['id'] = str(doc.pop('_id'))
        return doc

messaging_service = MessagingService()
