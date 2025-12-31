

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
import json
from config.db_config import MONGO_CONFIG

def setup_mongodb():
    """Setup MongoDB and load data"""
    print("🚀 Starting MongoDB setup...")
    
    try:
        client = MongoClient(MONGO_CONFIG['uri'], serverSelectionTimeoutMS=5000)
        # Test connection
        client.server_info()
        print("✅ Connected to MongoDB")
        
    except Exception as e:
        print(f"❌ Cannot connect to MongoDB: {e}")
        print("\nPlease make sure MongoDB is running:")
        print("  - Windows: Check MongoDB service in Services")
        print("  - Mac: brew services list")
        print("  - Linux: sudo systemctl status mongod")
        return
    
    db = client[MONGO_CONFIG['database']]
    
    # Load shipments
    print("\n🚚 Loading shipments...")
    with open('synthetic_data/shipments.json', 'r') as f:
        shipments = json.load(f)
    
    db.shipments.drop()
    db.shipments.insert_many(shipments)
    print(f"✅ Loaded {len(shipments)} shipments")
    
    # Load warehouses
    print("\n🏢 Loading warehouses...")
    with open('synthetic_data/warehouses.json', 'r') as f:
        warehouses = json.load(f)
    
    db.warehouses.drop()
    db.warehouses.insert_many(warehouses)
    print(f"✅ Loaded {len(warehouses)} warehouses")
    
    # Create indexes
    print("\n🔍 Creating indexes...")
    db.shipments.create_index("shipment_id")
    db.shipments.create_index("status")
    db.shipments.create_index("last_updated")
    db.warehouses.create_index("warehouse_id")
    print("✅ Indexes created")
    
    print("\n✅ MongoDB setup complete!")
    
    client.close()

if __name__ == "__main__":
    setup_mongodb()