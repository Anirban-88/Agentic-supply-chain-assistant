# config/redis_config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Redis Configuration
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'db': int(os.getenv('REDIS_DB', 0)),
    'password': os.getenv('REDIS_PASSWORD', 'redis123'),
    'decode_responses': True
}

# Redis Key Patterns
REDIS_KEYS = {
    # Batch information
    'batch_info': 'batch:{batch_id}',
    'batch_prefix': 'batch:',
    
    # Expiry tracking
    'expiry_product': 'expiry:product:{product_id}',
    'expiry_near': 'expiry:near:{days}d',
    'expiry_sorted_set': 'expiry:sorted',
    
    # Freshness scores
    'freshness': 'freshness:{product_id}:{batch_id}',
    
    # Alerts
    'alert_cache': 'alert:{product_id}',
    'alerts_list': 'alerts:expiry',
    
    # Category and location indexes
    'category_products': 'category:{category_name}:products',
    'category_prefix': 'category:',
    'location_prefix': 'location:',
    'location_batches': 'location:{location_id}:batches'
}

# Redis TTL (Time To Live) in seconds
REDIS_TTL = {
    'batch_info': 86400,        # 24 hours
    'expiry_data': 86400,       # 24 hours
    'freshness_score': 3600,    # 1 hour
    'alert_cache': 3600,        # 1 hour
    'category_cache': 3600,     # 1 hour
    'location_cache': 3600,     # 1 hour
    'batch_data': 86400,        # 24 hours
    'category_index': 3600,     # 1 hour
    'location_index': 3600      # 1 hour
}

print(f"✅ Redis configuration loaded")
print(f"   Host: {REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
