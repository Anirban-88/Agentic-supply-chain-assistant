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


def apply_schema_fixes(db_name):
    """Apply schema migrations/fixes to existing databases"""
    print(f"🔧 Applying schema fixes to {db_name}...")
    params = POSTGRES_CONFIG.copy()
    params['database'] = db_name

    conn = psycopg2.connect(**params)
    cursor = conn.cursor()

    try:
        if db_name == 'store_catalog':
            # Allow longer phone numbers / extensions in suppliers
            cursor.execute("ALTER TABLE suppliers ALTER COLUMN contact_phone TYPE VARCHAR(50);")
        conn.commit()
        print(f"✅ Applied schema fixes to {db_name}")
    except Exception as e:
        print(f"⚠️  Warning applying schema fixes to {db_name}: {e}")
    finally:
        cursor.close()
        conn.close()

def load_csv_to_postgres(db_name, table_name, csv_file):
    """Load CSV data into PostgreSQL table"""
    params = POSTGRES_CONFIG.copy()
    params['database'] = db_name
    
    df = pd.read_csv(csv_file)
    
    conn = psycopg2.connect(**params)
    cursor = conn.cursor()
    
    columns = ', '.join(df.columns)
    placeholders = ', '.join(['%s'] * len(df.columns))
    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    
    for idx, row in df.iterrows():
        try:
            cursor.execute(insert_sql, tuple(row))
        except psycopg2.DataError as e:
            conn.rollback()
            print(f"⚠️  Data error on row {idx} inserting into {db_name}.{table_name}: {e}")
            print(f"Row data: {tuple(row)}")
            raise
        except psycopg2.IntegrityError as e:
            conn.rollback()
            print(f"⚠️  Integrity error on row {idx} inserting into {db_name}.{table_name}: {e}")
            print(f"Row data: {tuple(row)}")
            raise
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ Loaded {len(df)} rows into {db_name}.{table_name}")

def clear_existing_data(db_name):
    """Clear all data from tables before loading new data"""
    print(f"🗑️  Clearing existing data from {db_name}...")
    
    params = POSTGRES_CONFIG.copy()
    params['database'] = db_name
    
    conn = psycopg2.connect(**params)
    cursor = conn.cursor()
    
    try:
        if db_name == 'store_catalog':
            cursor.execute("TRUNCATE TABLE product_suppliers, product_locations, products, suppliers, locations CASCADE;")
        elif db_name == 'inventory_mgmt':
            cursor.execute("TRUNCATE TABLE order_items, orders, inventory CASCADE;")
        elif db_name == 'expiry_tracking':
            cursor.execute("TRUNCATE TABLE batches CASCADE;")
        
        conn.commit()
        print(f"✅ Cleared existing data from {db_name}")
    except Exception as e:
        print(f"⚠️  Warning: {e}")
    finally:
        cursor.close()
        conn.close()    

def setup_postgresql():
    """Main setup function for PostgreSQL"""
    print("🚀 Starting PostgreSQL setup...")
    
    # Create databases
    create_databases()
    
    # Execute schemas
    execute_schema('store_catalog', 'schemas/store_catalog_schema.sql')
    # Apply any necessary schema migrations/fixes for existing DBs
    apply_schema_fixes('store_catalog')
    execute_schema('inventory_mgmt', 'schemas/inventory_mgmt_schema.sql')
    execute_schema('expiry_tracking', 'schemas/expiry_tracking_schema.sql')
    
    # Load data
    data_dir = 'synthetic_data'
    
    print("\n🔄 Loading data into databases...")
    
    # Clear existing data to make setup idempotent
    clear_existing_data('store_catalog')
    clear_existing_data('inventory_mgmt')
    clear_existing_data('expiry_tracking')
    
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