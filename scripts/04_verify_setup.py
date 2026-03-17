# scripts/04_verify_setup.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from pymongo import MongoClient
import pandas as pd
from config.db_config import POSTGRES_CONFIG, MONGO_CONFIG

def verify_postgresql():
    """Verify PostgreSQL data"""
    print("\n📊 Verifying PostgreSQL databases...")
    
    databases = {
        'store_catalog': ['products', 'suppliers', 'locations', 'product_locations', 'product_suppliers'],
        'inventory_mgmt': ['inventory', 'orders', 'order_items'],
        'expiry_tracking': ['batches']
    }
    
    for db_name, tables in databases.items():
        print(f"\n🗄️  Database: {db_name}")
        
        try:
            params = POSTGRES_CONFIG.copy()
            params['database'] = db_name
            conn = psycopg2.connect(**params)
            
            for table in tables:
                query = f"SELECT COUNT(*) FROM {table}"
                df = pd.read_sql(query, conn)
                count = df.iloc[0, 0]
                print(f"  ✅ {table}: {count} rows")
            
            conn.close()
            
        except Exception as e:
            print(f"  ❌ Error: {e}")

def verify_mongodb():
    """Verify MongoDB data"""
    print("\n📊 Verifying MongoDB...")
    
    try:
        client = MongoClient(MONGO_CONFIG['uri'], serverSelectionTimeoutMS=5000)
        db = client[MONGO_CONFIG['database']]
        
        collections = ['shipments', 'warehouses']
        
        for collection in collections:
            count = db[collection].count_documents({})
            print(f"  ✅ {collection}: {count} documents")
        
        # Show sample shipment
        print("\n📦 Sample Shipment:")
        sample = db.shipments.find_one()
        if sample:
            print(f"  Shipment ID: {sample['shipment_id']}")
            print(f"  Status: {sample['status']}")
            print(f"  Current Location: {sample['current_location']['city']}")
        
        client.close()
        
    except Exception as e:
        print(f"  ❌ Error: {e}")

def main():
    print("=" * 60)
    print("🔍 VERIFYING DATABASE SETUP")
    print("=" * 60)
    
    verify_postgresql()
    verify_mongodb()
    
    print("\n" + "=" * 60)
    print("✅ VERIFICATION COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()