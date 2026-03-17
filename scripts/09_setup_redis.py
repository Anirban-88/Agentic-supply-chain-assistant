import sys
import os
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.redis_client import RedisClient
from database.postgres_client import PostgreSQLClient
from config.redis_config import REDIS_CONFIG, REDIS_KEYS, REDIS_TTL
from config.db_config import POSTGRES_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

class RedisSetup:
    """Setup Redis with initial data for expiry tracking"""
    
    def __init__(self):
        """Initialize Redis and PostgreSQL clients"""
        self.redis_client = RedisClient(REDIS_CONFIG)
        self.postgres_client = PostgreSQLClient(POSTGRES_CONFIG, 'expiry_tracking')
        self.store_catalog_db = PostgreSQLClient(POSTGRES_CONFIG, 'store_catalog')
    
    def initialize(self):
        """Initialize database connections"""
        logger.info("Initializing database connections...")
        self.redis_client.initialize()
        self.postgres_client.initialize()
        self.store_catalog_db.initialize()
        logger.info("Database connections initialized")
    
    def close(self):
        """Close database connections"""
        self.redis_client.close()
        self.postgres_client.close()
        self.store_catalog_db.close()
        logger.info("Database connections closed")
    
    def setup_redis(self):
        """Main setup function"""
        try:
            logger.info("Starting Redis setup...")
            
            # Clear existing data
            self._clear_existing_data()
            
            # Load batch data from PostgreSQL
            batches = self._load_batch_data()
            logger.info(f"Loaded {len(batches)} batches from PostgreSQL")
            
            # Setup expiry tracking data
            self._setup_expiry_tracking(batches)
            
            # Setup category indexes
            self._setup_category_indexes()
            
            # Setup location indexes
            self._setup_location_indexes()
            
            logger.info("Redis setup completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error setting up Redis: {e}")
            return False
    
    def _clear_existing_data(self):
        """Clear existing Redis data"""
        logger.info("Clearing existing Redis data...")
        
        # Get keys matching patterns
        patterns = [
            'expiry:*',
            'freshness:*',
            'batch:*',
            'alert:*',
            'category:*',
            'location:*'
        ]
        
        for pattern in patterns:
            keys = self.redis_client.client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Deleted {len(keys)} keys matching '{pattern}'")
    
    def _load_batch_data(self) -> List[Dict[str, Any]]:
        """Load batch data from PostgreSQL"""
        # Get batches from expiry_tracking database
        batch_query = """
            SELECT *
            FROM batches
            WHERE status = 'active'
        """
        batches = self.postgres_client.execute_query(batch_query)
        
        # Get product info from store_catalog database
        product_query = """
            SELECT product_id, name, category
            FROM products
        """
        products = self.store_catalog_db.execute_query(product_query)
        
        # Create product lookup dict
        product_lookup = {p['product_id']: p for p in products}
        
        # Enrich batches with product info
        enriched_batches = []
        for batch in batches:
            product_id = batch['product_id']
            if product_id in product_lookup:
                batch['product_name'] = product_lookup[product_id]['name']
                batch['category'] = product_lookup[product_id]['category']
                enriched_batches.append(batch)
        
        return enriched_batches
    
    def _setup_expiry_tracking(self, batches: List[Dict[str, Any]]):
        """Setup expiry tracking data in Redis"""
        logger.info("Setting up expiry tracking data...")
        
        pipe = self.redis_client.pipeline()
        now = datetime.now().date()  # Use date for comparison
        
        # Process each batch
        for batch in batches:
            # Convert dates to date objects if they're datetime
            expiry_date = batch['expiry_date']
            if isinstance(expiry_date, datetime):
                expiry_date = expiry_date.date()
            
            manufacturing_date = batch['manufacturing_date']
            if isinstance(manufacturing_date, datetime):
                manufacturing_date = manufacturing_date.date()
            
            # Calculate days until expiry
            days_until_expiry = (expiry_date - now).days
            
            # Skip expired batches
            if days_until_expiry < 0:
                continue
            
            # 1. Store batch info
            batch_key = REDIS_KEYS['batch_info'].format(batch_id=batch['batch_id'])
            pipe.hset(batch_key, mapping={
                'product_id': batch['product_id'],
                'product_name': batch['product_name'],
                'manufacturing_date': manufacturing_date.isoformat(),
                'expiry_date': expiry_date.isoformat(),
                'quantity': str(batch['quantity']),
                'location_id': batch['location_id'],
                'status': batch['status']
            })
            pipe.expire(batch_key, REDIS_TTL['batch_info'])
            
            # 2. Store product expiry info
            product_key = REDIS_KEYS['expiry_product'].format(product_id=batch['product_id'])
            pipe.hset(product_key, mapping={
                'batch_id': batch['batch_id'],
                'expiry_date': expiry_date.isoformat(),
                'quantity': str(batch['quantity']),
                'location_id': batch['location_id'],
                'status': batch['status']
            })
            pipe.expire(product_key, REDIS_TTL['expiry_data'])
            
            # 3. Add to near-expiry sorted sets
            for days in [7, 14, 30]:
                if days_until_expiry <= days:
                    near_expiry_key = REDIS_KEYS['expiry_near'].format(days=days)
                    member = f"{batch['product_id']}:{batch['batch_id']}"
                    # Convert date to datetime for timestamp
                    score = datetime.combine(expiry_date, datetime.min.time()).timestamp()
                    pipe.zadd(near_expiry_key, {member: score})
            
            # 4. Calculate and store freshness score
            total_shelf_life = (expiry_date - manufacturing_date).days
            if total_shelf_life > 0:
                freshness_score = min(100, (days_until_expiry / total_shelf_life) * 100)
                freshness_key = REDIS_KEYS['freshness'].format(
                    product_id=batch['product_id'],
                    batch_id=batch['batch_id']
                )
                pipe.set(freshness_key, freshness_score, ex=REDIS_TTL['freshness_score'])
            
            # 5. Create alerts for items expiring soon
            if days_until_expiry <= 7:
                alert_level = (
                    'critical' if days_until_expiry <= 3
                    else 'warning' if days_until_expiry <= 5
                    else 'info'
                )
                
                alert_data = {
                    'batch_id': batch['batch_id'],
                    'product_id': batch['product_id'],
                    'product_name': batch['product_name'],
                    'days_until_expiry': days_until_expiry,
                    'alert_level': alert_level,
                    'created_at': now.isoformat()
                }
                
                alert_key = REDIS_KEYS['alert_cache'].format(product_id=batch['product_id'])
                pipe.lpush(alert_key, json.dumps(alert_data))
                pipe.ltrim(alert_key, 0, 9)  # Keep last 10 alerts
                pipe.expire(alert_key, REDIS_TTL['alert_cache'])
        
        # Execute all commands
        pipe.execute()
        logger.info("Expiry tracking data setup completed")
    
    def _setup_category_indexes(self):
        """Setup category indexes"""
        logger.info("Setting up category indexes...")
        
        # Get products by category
        query = """
            SELECT product_id, category
            FROM products
            WHERE category IS NOT NULL
        """
        products = self.store_catalog_db.execute_query(query)
        
        # Group by category
        categories = {}
        for product in products:
            category = product['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(product['product_id'])
        
        # Store in Redis
        pipe = self.redis_client.pipeline()
        for category, product_ids in categories.items():
            key = REDIS_KEYS['category_products'].format(category_name=category)
            pipe.delete(key)  # Clear existing
            if product_ids:
                pipe.sadd(key, *product_ids)
                pipe.expire(key, REDIS_TTL['category_cache'])
        
        pipe.execute()
        logger.info(f"Set up {len(categories)} category indexes")
    
    def _setup_location_indexes(self):
        """Setup location indexes"""
        logger.info("Setting up location indexes...")
        
        # Get batches by location
        query = """
            SELECT location_id, batch_id
            FROM batches
            WHERE status = 'active'
        """
        batches = self.postgres_client.execute_query(query)
        
        # Group by location
        locations = {}
        for batch in batches:
            location_id = batch['location_id']
            if location_id not in locations:
                locations[location_id] = []
            locations[location_id].append(batch['batch_id'])
        
        # Store in Redis
        pipe = self.redis_client.pipeline()
        for location_id, batch_ids in locations.items():
            key = f"location:{location_id}:batches"
            pipe.delete(key)  # Clear existing
            if batch_ids:
                pipe.sadd(key, *batch_ids)
                pipe.expire(key, REDIS_TTL['batch_info'])
        
        pipe.execute()
        logger.info(f"Set up {len(locations)} location indexes")


def main():
    """Main function"""
    setup = RedisSetup()
    
    try:
        setup.initialize()
        success = setup.setup_redis()
        
        if success:
            logger.info("Redis setup completed successfully")
        else:
            logger.error("Redis setup failed")
            sys.exit(1)
    finally:
        setup.close()


if __name__ == "__main__":
    main()