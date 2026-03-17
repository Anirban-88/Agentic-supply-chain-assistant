# database/redis_client.py

import redis
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client wrapper for managing cache and expiry tracking"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Redis client
        
        Args:
            config: Redis connection configuration
        """
        self.config = config
        self.client: Optional[redis.Redis] = None
    
    def initialize(self):
        """Initialize Redis connection"""
        try:
            # Get password from config
            password = self.config.get('password')
            
            # Create Redis connection
            connection_params = {
                'host': self.config['host'],
                'port': self.config['port'],
                'db': self.config.get('db', 0),
                'decode_responses': self.config.get('decode_responses', True)
            }
            
            # Only add password if it's not None or empty
            if password:
                connection_params['password'] = password
            
            self.client = redis.Redis(**connection_params)
            
            # Test connection
            self.client.ping()
            logger.info(f"Connected to Redis at {self.config['host']}:{self.config['port']}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def close(self):
        """Close Redis connection"""
        if self.client:
            self.client.close()
            logger.info("Redis connection closed")
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set a key-value pair with optional expiration"""
        try:
            return self.client.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"Error setting key {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Error getting key {key}: {e}")
            return None
    
    def hset(self, name: str, key: Optional[str] = None, value: Optional[str] = None, 
             mapping: Optional[Dict] = None) -> int:
        """Set hash field"""
        try:
            return self.client.hset(name, key=key, value=value, mapping=mapping)
        except Exception as e:
            logger.error(f"Error setting hash {name}: {e}")
            return 0
    
    def hget(self, name: str, key: str) -> Optional[str]:
        """Get hash field value"""
        try:
            return self.client.hget(name, key)
        except Exception as e:
            logger.error(f"Error getting hash field {name}:{key}: {e}")
            return None
    
    def hgetall(self, name: str) -> Dict:
        """Get all hash fields"""
        try:
            return self.client.hgetall(name)
        except Exception as e:
            logger.error(f"Error getting all hash fields {name}: {e}")
            return {}
    
    def delete(self, *keys: str) -> int:
        """Delete one or more keys"""
        try:
            return self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Error deleting keys: {e}")
            return 0
    
    def expire(self, name: str, time: int) -> bool:
        """Set expiration time on a key"""
        try:
            return self.client.expire(name, time)
        except Exception as e:
            logger.error(f"Error setting expiration on {name}: {e}")
            return False
    
    def zadd(self, name: str, mapping: Dict[str, float]) -> int:
        """Add members to sorted set"""
        try:
            return self.client.zadd(name, mapping)
        except Exception as e:
            logger.error(f"Error adding to sorted set {name}: {e}")
            return 0
    
    def zrange(self, name: str, start: int, end: int, withscores: bool = False) -> List:
        """Get range from sorted set"""
        try:
            return self.client.zrange(name, start, end, withscores=withscores)
        except Exception as e:
            logger.error(f"Error getting range from sorted set {name}: {e}")
            return []
    
    def sadd(self, name: str, *values: str) -> int:
        """Add members to set"""
        try:
            return self.client.sadd(name, *values)
        except Exception as e:
            logger.error(f"Error adding to set {name}: {e}")
            return 0
    
    def smembers(self, name: str) -> set:
        """Get all members from set"""
        try:
            return self.client.smembers(name)
        except Exception as e:
            logger.error(f"Error getting members from set {name}: {e}")
            return set()
    
    def lpush(self, name: str, *values: str) -> int:
        """Push values to list"""
        try:
            return self.client.lpush(name, *values)
        except Exception as e:
            logger.error(f"Error pushing to list {name}: {e}")
            return 0
    
    def lrange(self, name: str, start: int, end: int) -> List[str]:
        """Get range from list"""
        try:
            return self.client.lrange(name, start, end)
        except Exception as e:
            logger.error(f"Error getting range from list {name}: {e}")
            return []
    
    def ltrim(self, name: str, start: int, end: int) -> bool:
        """Trim list to specified range"""
        try:
            return self.client.ltrim(name, start, end)
        except Exception as e:
            logger.error(f"Error trimming list {name}: {e}")
            return False
    
    def pipeline(self):
        """Create a pipeline for batch operations"""
        return self.client.pipeline()
    
    def keys(self, pattern: str = '*') -> List[str]:
        """Get keys matching pattern"""
        try:
            return self.client.keys(pattern)
        except Exception as e:
            logger.error(f"Error getting keys with pattern {pattern}: {e}")
            return []
