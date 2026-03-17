# scripts/01_generate_data.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker
import json
from config.db_config import DATA_CONFIG

fake = Faker()

# Use config values
NUM_PRODUCTS = DATA_CONFIG['num_products']
NUM_SUPPLIERS = DATA_CONFIG['num_suppliers']
NUM_LOCATIONS = DATA_CONFIG['num_locations']
NUM_BATCHES = DATA_CONFIG['num_batches']
NUM_SHIPMENTS = DATA_CONFIG['num_shipments']
NUM_ORDERS = DATA_CONFIG['num_orders']

CATEGORIES = [
    'Dairy', 'Beverages', 'Snacks', 'Frozen Foods', 'Fresh Produce',
    'Bakery', 'Meat & Seafood', 'Condiments', 'Personal Care', 'Household'
]

def generate_products(num=NUM_PRODUCTS):
    products = []
    for i in range(1, num + 1):
        product = {
            'product_id': f'P{i:04d}',
            'name': fake.word().capitalize() + ' ' + fake.word().capitalize(),
            'category': random.choice(CATEGORIES),
            'brand': fake.company(),
            'barcode': fake.ean13(),
            'base_price': round(random.uniform(1.99, 99.99), 2),
            'weight_kg': round(random.uniform(0.1, 5.0), 3),
            'description': fake.sentence(),
            'created_at': fake.date_time_between(start_date='-2y', end_date='now')
        }
        products.append(product)
    return pd.DataFrame(products)

def generate_suppliers(num=NUM_SUPPLIERS):
    suppliers = []
    for i in range(1, num + 1):
        supplier = {
            'supplier_id': f'SUP{i:03d}',
            'name': fake.company(),
            'contact_email': fake.company_email(),
            'contact_phone': fake.phone_number(),
            'address': fake.address().replace('\n', ', '),
            'reliability_score': round(random.uniform(0.7, 1.0), 2),
            'average_lead_time_days': random.randint(1, 10)
        }
        suppliers.append(supplier)
    return pd.DataFrame(suppliers)

def generate_locations(num=NUM_LOCATIONS):
    locations = []
    sections = ['Refrigerated', 'Frozen', 'Dry Goods', 'Checkout', 'Storage']
    
    for i in range(1, num + 1):
        location = {
            'location_id': f'LOC{i:03d}',
            'aisle': f'A{random.randint(1, 10)}',
            'rack': f'R{random.randint(1, 20)}',
            'shelf': f'S{random.randint(1, 5)}',
            'section': random.choice(sections),
            'capacity': random.randint(50, 200)
        }
        locations.append(location)
    return pd.DataFrame(locations)

def generate_product_locations(products_df, locations_df):
    mappings = []
    for _, product in products_df.iterrows():
        num_locations = random.randint(1, 3)
        selected_locations = locations_df.sample(n=num_locations)
        
        for _, loc in selected_locations.iterrows():
            mapping = {
                'product_id': product['product_id'],
                'location_id': loc['location_id'],
                'allocated_space': random.randint(10, 50)
            }
            mappings.append(mapping)
    return pd.DataFrame(mappings)

def generate_product_suppliers(products_df, suppliers_df):
    mappings = []
    for _, product in products_df.iterrows():
        num_suppliers = random.randint(1, 2)
        selected_suppliers = suppliers_df.sample(n=num_suppliers)
        
        for _, sup in selected_suppliers.iterrows():
            mapping = {
                'product_id': product['product_id'],
                'supplier_id': sup['supplier_id'],
                'unit_cost': round(product['base_price'] * random.uniform(0.5, 0.8), 2),
                'minimum_order_quantity': random.randint(10, 100)
            }
            mappings.append(mapping)
    return pd.DataFrame(mappings)

def generate_inventory(products_df, locations_df):
    inventory = []
    for _, product in products_df.iterrows():
        location = locations_df.sample(n=1).iloc[0]
        
        inv = {
            'product_id': product['product_id'],
            'location_id': location['location_id'],
            'quantity': random.randint(0, 200),
            'reorder_level': random.randint(10, 30),
            'reorder_quantity': random.randint(50, 150),
            'last_restocked': fake.date_time_between(start_date='-30d', end_date='now'),
            'last_updated': datetime.now()
        }
        inventory.append(inv)
    return pd.DataFrame(inventory)

def generate_batches(products_df, locations_df, num=NUM_BATCHES):
    batches = []
    perishable_categories = ['Dairy', 'Fresh Produce', 'Meat & Seafood', 'Bakery', 'Frozen Foods']
    
    perishable_products = products_df[products_df['category'].isin(perishable_categories)]
    
    for i in range(1, num + 1):
        product = perishable_products.sample(n=1).iloc[0]
        location = locations_df.sample(n=1).iloc[0]
        
        mfg_date = fake.date_between(start_date='-60d', end_date='-1d')
        
        if product['category'] in ['Dairy', 'Meat & Seafood']:
            shelf_life = random.randint(5, 15)
        elif product['category'] == 'Fresh Produce':
            shelf_life = random.randint(3, 10)
        elif product['category'] == 'Bakery':
            shelf_life = random.randint(2, 7)
        else:
            shelf_life = random.randint(90, 365)
        
        exp_date = mfg_date + timedelta(days=shelf_life)
        days_left = (exp_date - datetime.now().date()).days
        
        if days_left < 0:
            status = 'expired'
        elif days_left <= 3:
            status = 'near_expiry'
        else:
            status = 'active'
        
        batch = {
            'batch_id': f'BATCH{i:05d}',
            'product_id': product['product_id'],
            'manufacturing_date': mfg_date,
            'expiry_date': exp_date,
            'quantity': random.randint(20, 100),
            'received_date': fake.date_time_between(start_date=mfg_date, end_date='now'),
            'location_id': location['location_id'],
            'status': status
        }
        batches.append(batch)
    
    return pd.DataFrame(batches)

def generate_orders(suppliers_df, num=NUM_ORDERS):
    orders = []
    statuses = ['pending', 'confirmed', 'shipped', 'delivered']
    
    for i in range(1, num + 1):
        supplier = suppliers_df.sample(n=1).iloc[0]
        order_date = fake.date_time_between(start_date='-30d', end_date='now')
        
        order = {
            'order_id': f'ORD{i:04d}',
            'supplier_id': supplier['supplier_id'],
            'order_date': order_date,
            'expected_delivery_date': order_date.date() + timedelta(days=int(supplier['average_lead_time_days'])),
            'status': random.choice(statuses),
            'total_amount': round(random.uniform(500, 10000), 2)
        }
        orders.append(order)
    
    return pd.DataFrame(orders)

def generate_order_items(orders_df, products_df, product_suppliers_df):
    order_items = []
    item_id = 1
    
    for _, order in orders_df.iterrows():
        num_items = random.randint(2, 8)
        
        supplier_products = product_suppliers_df[
            product_suppliers_df['supplier_id'] == order['supplier_id']
        ]['product_id'].tolist()
        
        if len(supplier_products) < num_items:
            num_items = len(supplier_products)
        
        if len(supplier_products) == 0:
            continue
            
        selected_products = random.sample(supplier_products, num_items)
        
        for prod_id in selected_products:
            prod_supplier = product_suppliers_df[
                (product_suppliers_df['product_id'] == prod_id) &
                (product_suppliers_df['supplier_id'] == order['supplier_id'])
            ].iloc[0]
            
            item = {
                'order_item_id': item_id,
                'order_id': order['order_id'],
                'product_id': prod_id,
                'quantity': random.randint(10, 100),
                'unit_price': prod_supplier['unit_cost']
            }
            order_items.append(item)
            item_id += 1
    
    return pd.DataFrame(order_items)

def generate_shipments(orders_df, num=NUM_SHIPMENTS):
    shipments = []
    statuses = ['pending', 'picked_up', 'in_transit', 'out_for_delivery', 'delivered']
    cities = ['Mumbai', 'Pune', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata']
    
    shipped_orders = orders_df[orders_df['status'].isin(['shipped', 'delivered'])]
    
    if len(shipped_orders) == 0:
        shipped_orders = orders_df.sample(n=min(num, len(orders_df)))
    else:
        shipped_orders = shipped_orders.sample(n=min(num, len(shipped_orders)))
    
    for i, (_, order) in enumerate(shipped_orders.iterrows(), 1):
        origin_city = random.choice(cities)
        dest_city = random.choice([c for c in cities if c != origin_city])
        
        departed = fake.date_time_between(start_date=order['order_date'], end_date='now')
        
        shipment = {
            'shipment_id': f'SH{datetime.now().year}{i:05d}',
            'order_id': order['order_id'],
            'supplier_id': order['supplier_id'],
            'carrier': random.choice(['FastShip Logistics', 'QuickDeliver', 'ExpressTransport']),
            'tracking_number': f'TRACK{random.randint(100000, 999999)}',
            'status': random.choice(statuses),
            'origin': {
                'warehouse_id': f'WH{random.randint(1, 5):03d}',
                'location': origin_city,
                'departed_at': departed.isoformat()
            },
            'destination': {
                'store_id': 'STORE001',
                'location': dest_city,
                'estimated_arrival': (departed + timedelta(days=random.randint(2, 5))).isoformat()
            },
            'items': [
                {
                    'product_id': f'P{random.randint(1, NUM_PRODUCTS):04d}',
                    'quantity': random.randint(20, 100),
                    'batch_id': f'BATCH{random.randint(1, NUM_BATCHES):05d}'
                }
                for _ in range(random.randint(1, 5))
            ],
            'current_location': {
                'city': random.choice(cities),
                'coordinates': [round(random.uniform(72, 78), 4), round(random.uniform(18, 29), 4)],
                'updated_at': datetime.now().isoformat()
            },
            'last_updated': datetime.now().isoformat()
        }
        shipments.append(shipment)
    
    return shipments

def generate_warehouse_inventory(products_df):
    warehouses = []
    cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata']
    
    for i in range(1, 6):
        warehouse = {
            'warehouse_id': f'WH{i:03d}',
            'name': f'{cities[i-1]} Distribution Center',
            'location': cities[i-1],
            'products': []
        }
        
        num_products = random.randint(50, NUM_PRODUCTS)
        selected_products = products_df.sample(n=num_products)
        
        for _, prod in selected_products.iterrows():
            quantity = random.randint(1000, 10000)
            reserved = random.randint(0, int(quantity * 0.2))
            
            warehouse['products'].append({
                'product_id': prod['product_id'],
                'quantity': quantity,
                'reserved': reserved,
                'available': quantity - reserved,
                'last_updated': datetime.now().isoformat()
            })
        
        warehouse['last_updated'] = datetime.now().isoformat()
        warehouses.append(warehouse)
    
    return warehouses

def generate_all_data():
    print("🔄 Generating synthetic data...")
    
    print("  📦 Generating products...")
    products_df = generate_products()
    
    print("  🏭 Generating suppliers...")
    suppliers_df = generate_suppliers()
    
    print("  📍 Generating locations...")
    locations_df = generate_locations()
    
    print("  🔗 Generating product-location mappings...")
    product_locations_df = generate_product_locations(products_df, locations_df)
    
    print("  🔗 Generating product-supplier mappings...")
    product_suppliers_df = generate_product_suppliers(products_df, suppliers_df)
    
    print("  📊 Generating inventory...")
    inventory_df = generate_inventory(products_df, locations_df)
    
    print("  🏷️  Generating batches...")
    batches_df = generate_batches(products_df, locations_df)
    
    print("  📋 Generating orders...")
    orders_df = generate_orders(suppliers_df)
    
    print("  📋 Generating order items...")
    order_items_df = generate_order_items(orders_df, products_df, product_suppliers_df)
    
    print("  🚚 Generating shipments...")
    shipments = generate_shipments(orders_df)
    
    print("  🏢 Generating warehouse inventory...")
    warehouses = generate_warehouse_inventory(products_df)
    
    print("✅ Data generation complete!")
    
    return {
        'products': products_df,
        'suppliers': suppliers_df,
        'locations': locations_df,
        'product_locations': product_locations_df,
        'product_suppliers': product_suppliers_df,
        'inventory': inventory_df,
        'batches': batches_df,
        'orders': orders_df,
        'order_items': order_items_df,
        'shipments': shipments,
        'warehouses': warehouses
    }

def save_data(data_dict, output_dir='synthetic_data'):
    os.makedirs(output_dir, exist_ok=True)
    
    csv_tables = ['products', 'suppliers', 'locations', 'product_locations', 
                  'product_suppliers', 'inventory', 'batches', 'orders', 'order_items']
    
    for table in csv_tables:
        filepath = os.path.join(output_dir, f'{table}.csv')
        data_dict[table].to_csv(filepath, index=False)
        print(f"💾 Saved {filepath}")
    
    with open(os.path.join(output_dir, 'shipments.json'), 'w') as f:
        json.dump(data_dict['shipments'], f, indent=2)
    print(f"💾 Saved {os.path.join(output_dir, 'shipments.json')}")
    
    with open(os.path.join(output_dir, 'warehouses.json'), 'w') as f:
        json.dump(data_dict['warehouses'], f, indent=2)
    print(f"💾 Saved {os.path.join(output_dir, 'warehouses.json')}")

if __name__ == "__main__":
    data = generate_all_data()
    save_data(data)
    
    print("\n📊 Data Summary:")
    print(f"  Products: {len(data['products'])}")
    print(f"  Suppliers: {len(data['suppliers'])}")
    print(f"  Locations: {len(data['locations'])}")
    print(f"  Inventory Records: {len(data['inventory'])}")
    print(f"  Batches: {len(data['batches'])}")
    print(f"  Orders: {len(data['orders'])}")
    print(f"  Shipments: {len(data['shipments'])}")
    print(f"  Warehouses: {len(data['warehouses'])}")