import os
import redis
from pymemcache.client.base import Client as MemcachedClient
import logging
import json

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        # Redis connection (for distributed locks, rate limits, auction state)
        self.redis_url = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
        self.redis = redis.from_url(self.redis_url, decode_responses=True)

        # Memcached connection (for read-heavy caching)
        memcached_url = os.environ.get('MEMCACHED_URL', 'memcached:11211')
        host, port = memcached_url.split(':')
        self.memcached = MemcachedClient((host, int(port)))

    def get_redis_client(self):
        return self.redis

    def get_memcached_client(self):
        return self.memcached

    def set_json(self, key, value, ttl=None, use_redis=True):
        """Set a value as JSON"""
        try:
            data = json.dumps(value)
            if use_redis:
                self.redis.set(key, data, ex=ttl)
            else:
                self.memcached.set(key, data, expire=ttl or 0)
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")

    def get_json(self, key, use_redis=True):
        """Get a value as JSON"""
        try:
            if use_redis:
                data = self.redis.get(key)
            else:
                data = self.memcached.get(key)
                if data:
                    data = data.decode('utf-8')
            
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None

    def delete(self, key, use_redis=True):
        try:
            if use_redis:
                self.redis.delete(key)
            else:
                self.memcached.delete(key)
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")

cache = CacheService()
