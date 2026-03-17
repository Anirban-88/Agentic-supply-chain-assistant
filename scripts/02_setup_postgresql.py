# scripts/02_setup_postgresql.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from psycopg2 import sql
import pandas as pd
from config.db_config import POSTGRES_CONFIG

def create_databases():
    """Create the three PostgreSQL databases"""
    print("🔄 Creating PostgreSQL databases...")
    
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    conn.autocommit = True
    cursor = conn.cursor()
    
    databases = ['store_catalog', 'inventory_mgmt', 'expiry_tracking']
    
    for db in databases:
        try:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db)))
            print(f"✅ Created database: {db}")
        except psycopg2.errors.DuplicateDatabase:
            print(f"ℹ️  Database {db} already exists")
    
    cursor.close()
    conn.close()

def execute_schema(db_name, schema_file):
    """Execute SQL schema file on a database"""
    print(f"🔄 Executing schema on {db_name}...")
    
    params = POSTGRES_CONFIG.copy()
    params['database'] = db_name
    
    conn = psycopg2.connect(**params)
    cursor = conn.cursor()
    
    with open(schema_file, 'r') as f:
        schema_sql = f.read()
    
    cursor.execute(schema_sql)
    conn.commit()
    
    cursor.close()
    conn.close()
    print(f"✅ Schema executed on {db_name}")

def truncate_table(db_name, table_name):
    """Truncate a table to remove all existing data"""
    params = POSTGRES_CONFIG.copy()
    params['database'] = db_name
    
    conn = psycopg2.connect(**params)
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
        conn.commit()
    except Exception as e:
        print(f"⚠️  Could not truncate {table_name}: {e}")
    
    cursor.close()
    conn.close()

def load_csv_to_postgres(db_name, table_name, csv_file, truncate=True):
    """Load CSV data into PostgreSQL table"""
    params = POSTGRES_CONFIG.copy()
    params['database'] = db_name
    
    df = pd.read_csv(csv_file)
    
    conn = psycopg2.connect(**params)
    cursor = conn.cursor()
    
    # Truncate table first if requested
    if truncate:
        try:
            cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
            conn.commit()
        except Exception as e:
            print(f"⚠️  Could not truncate {table_name}: {e}")
    
    columns = ', '.join(df.columns)
    placeholders = ', '.join(['%s'] * len(df.columns))
    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    
    for _, row in df.iterrows():
        try:
            cursor.execute(insert_sql, tuple(row))
        except psycopg2.errors.UniqueViolation:
            # Skip duplicates
            conn.rollback()
            continue
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ Loaded {len(df)} rows into {db_name}.{table_name}")

def setup_postgresql():
    """Main setup function for PostgreSQL"""
    print("🚀 Starting PostgreSQL setup...")
    
    # Create databases
    create_databases()
    
    # Execute schemas
    execute_schema('store_catalog', 'schemas/store_catalog_schema.sql')
    execute_schema('inventory_mgmt', 'schemas/inventory_mgmt_schema.sql')
    execute_schema('expiry_tracking', 'schemas/expiry_tracking_schema.sql')
    
    # Load data
    data_dir = 'synthetic_data'
    
    print("\n🔄 Loading data into databases...")
    
    # Store Catalog DB
    print("\n📚 Loading Store Catalog...")
    load_csv_to_postgres('store_catalog', 'products', f'{data_dir}/products.csv')
    load_csv_to_postgres('store_catalog', 'locations', f'{data_dir}/locations.csv')
    load_csv_to_postgres('store_catalog', 'suppliers', f'{data_dir}/suppliers.csv')
    load_csv_to_postgres('store_catalog', 'product_locations', f'{data_dir}/product_locations.csv')
    load_csv_to_postgres('store_catalog', 'product_suppliers', f'{data_dir}/product_suppliers.csv')
    
    # Inventory Management DB
    print("\n📦 Loading Inventory Management...")
    load_csv_to_postgres('inventory_mgmt', 'inventory', f'{data_dir}/inventory.csv')
    load_csv_to_postgres('inventory_mgmt', 'orders', f'{data_dir}/orders.csv')
    load_csv_to_postgres('inventory_mgmt', 'order_items', f'{data_dir}/order_items.csv')
    
    # Expiry Tracking DB
    print("\n⏰ Loading Expiry Tracking...")
    load_csv_to_postgres('expiry_tracking', 'batches', f'{data_dir}/batches.csv')
    
    print("\n✅ PostgreSQL setup complete!")

if __name__ == "__main__":
    try:
        setup_postgresql()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPlease make sure:")
        print("1. PostgreSQL is running")
        print("2. Your password in config/db_config.py is correct")
        print("3. You have necessary permissions")