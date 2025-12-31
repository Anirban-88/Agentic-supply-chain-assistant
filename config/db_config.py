# config/db_config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# PostgreSQL Configuration
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
}

# MongoDB Configuration
MONGO_CONFIG = {
    'uri': os.getenv('MONGO_URI', 'mongodb://localhost:27017/'),
    'database': os.getenv('MONGO_DATABASE', 'supply_chain_logistics')
}

# Data Generation Configuration
DATA_CONFIG = {
    'num_products': 100,
    'num_suppliers': 15,
    'num_locations': 30,
    'num_batches': 200,
    'num_shipments': 50,
    'num_orders': 40,
    'num_warehouses': 5,
}

print(f"✅ Database configurations loaded")
print(f"   PostgreSQL: {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}")
print(f"   MongoDB: {MONGO_CONFIG['uri']}")
