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
    'password': os.getenv('REDIS_PASSWORD', None),
    'decode_responses': True
}

# Redis Key Patterns
REDIS_KEYS = {
    'batch_prefix': 'batch:',
    'expiry_sorted_set': 'expiry:sorted',
    'category_prefix': 'category:',
    'location_prefix': 'location:',
    'alerts_list': 'alerts:expiry'
}

# Redis TTL (Time To Live) in seconds
REDIS_TTL = {
    'batch_data': 86400,  # 24 hours
    'category_index': 3600,  # 1 hour
    'location_index': 3600,  # 1 hour
}

print(f"✅ Redis configuration loaded")
print(f"   Host: {REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
