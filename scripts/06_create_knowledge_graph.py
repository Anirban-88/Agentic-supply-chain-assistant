# scripts/06_create_knowledge_graph.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neo4j import GraphDatabase
import psycopg2
from pymongo import MongoClient
import pandas as pd
from config.db_config import POSTGRES_CONFIG, MONGO_CONFIG
from config.neo4j_config import NEO4J_CONFIG

class KnowledgeGraphBuilder:
    def __init__(self):
        self.neo4j_driver = GraphDatabase.driver(
            NEO4J_CONFIG['uri'],
            auth=(NEO4J_CONFIG['username'], NEO4J_CONFIG['password'])
        )
        print("✅ Connected to Neo4j")
    
    def close(self):
        self.neo4j_driver.close()
    
    def clear_database(self):
        """Clear all nodes and relationships"""
        print("\n🗑️  Clearing existing graph...")
        with self.neo4j_driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("✅ Graph cleared")
    
    def create_constraints(self):
        """Create uniqueness constraints"""
        print("\n🔒 Creating constraints...")
        
        constraints = [
            "CREATE CONSTRAINT product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.product_id IS UNIQUE",
            "CREATE CONSTRAINT supplier_id IF NOT EXISTS FOR (s:Supplier) REQUIRE s.supplier_id IS UNIQUE",
            "CREATE CONSTRAINT location_id IF NOT EXISTS FOR (l:Location) REQUIRE l.location_id IS UNIQUE",
            "CREATE CONSTRAINT batch_id IF NOT EXISTS FOR (b:Batch) REQUIRE b.batch_id IS UNIQUE",
            "CREATE CONSTRAINT order_id IF NOT EXISTS FOR (o:Order) REQUIRE o.order_id IS UNIQUE",
            "CREATE CONSTRAINT shipment_id IF NOT EXISTS FOR (sh:Shipment) REQUIRE sh.shipment_id IS UNIQUE",
            "CREATE CONSTRAINT warehouse_id IF NOT EXISTS FOR (w:Warehouse) REQUIRE w.warehouse_id IS UNIQUE",
        ]
        
        with self.neo4j_driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    if "already exists" not in str(e):
                        print(f"⚠️  {e}")
        
        print("✅ Constraints created")
    
    def load_products(self):
        """Load products from PostgreSQL"""
        print("\n📦 Loading Products...")
        
        params = POSTGRES_CONFIG.copy()
        params['database'] = 'store_catalog'
        conn = psycopg2.connect(**params)
        
        df = pd.read_sql("SELECT * FROM products", conn)
        conn.close()
        
        with self.neo4j_driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    CREATE (p:Product {
                        product_id: $product_id,
                        name: $name,
                        category: $category,
                        brand: $brand,
                        barcode: $barcode,
                        base_price: $base_price,
                        weight_kg: $weight_kg,
                        description: $description
                    })
                """, **row.to_dict())
        
        print(f"✅ Loaded {len(df)} products")
    
    def load_suppliers(self):
        """Load suppliers from PostgreSQL"""
        print("\n🏭 Loading Suppliers...")
        
        params = POSTGRES_CONFIG.copy()
        params['database'] = 'store_catalog'
        conn = psycopg2.connect(**params)
        
        df = pd.read_sql("SELECT * FROM suppliers", conn)
        conn.close()
        
        with self.neo4j_driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    CREATE (s:Supplier {
                        supplier_id: $supplier_id,
                        name: $name,
                        contact_email: $contact_email,
                        contact_phone: $contact_phone,
                        address: $address,
                        reliability_score: $reliability_score,
                        average_lead_time_days: $average_lead_time_days
                    })
                """, **row.to_dict())
        
        print(f"✅ Loaded {len(df)} suppliers")
    
    def load_locations(self):
        """Load locations from PostgreSQL"""
        print("\n📍 Loading Locations...")
        
        params = POSTGRES_CONFIG.copy()
        params['database'] = 'store_catalog'
        conn = psycopg2.connect(**params)
        
        df = pd.read_sql("SELECT * FROM locations", conn)
        conn.close()
        
        with self.neo4j_driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    CREATE (l:Location {
                        location_id: $location_id,
                        aisle: $aisle,
                        rack: $rack,
                        shelf: $shelf,
                        section: $section,
                        capacity: $capacity
                    })
                """, **row.to_dict())
        
        print(f"✅ Loaded {len(df)} locations")
    
    def create_product_location_relationships(self):
        """Create relationships between products and locations"""
        print("\n🔗 Creating Product-Location relationships...")
        
        params = POSTGRES_CONFIG.copy()
        params['database'] = 'store_catalog'
        conn = psycopg2.connect(**params)
        
        df = pd.read_sql("SELECT * FROM product_locations", conn)
        conn.close()
        
        with self.neo4j_driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MATCH (p:Product {product_id: $product_id})
                    MATCH (l:Location {location_id: $location_id})
                    CREATE (p)-[:LOCATED_IN {allocated_space: $allocated_space}]->(l)
                """, **row.to_dict())
        
        print(f"✅ Created {len(df)} product-location relationships")
    
    def create_product_supplier_relationships(self):
        """Create relationships between products and suppliers"""
        print("\n🔗 Creating Product-Supplier relationships...")
        
        params = POSTGRES_CONFIG.copy()
        params['database'] = 'store_catalog'
        conn = psycopg2.connect(**params)
        
        df = pd.read_sql("SELECT * FROM product_suppliers", conn)
        conn.close()
        
        with self.neo4j_driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MATCH (p:Product {product_id: $product_id})
                    MATCH (s:Supplier {supplier_id: $supplier_id})
                    CREATE (p)-[:SUPPLIED_BY {
                        unit_cost: $unit_cost,
                        minimum_order_quantity: $minimum_order_quantity
                    }]->(s)
                """, **row.to_dict())
        
        print(f"✅ Created {len(df)} product-supplier relationships")
    
    def load_inventory(self):
        """Load inventory data"""
        print("\n📊 Loading Inventory...")
        
        params = POSTGRES_CONFIG.copy()
        params['database'] = 'inventory_mgmt'
        conn = psycopg2.connect(**params)
        
        df = pd.read_sql("SELECT * FROM inventory", conn)
        conn.close()
        
        with self.neo4j_driver.session() as session:
            for _, row in df.iterrows():
                row_dict = row.to_dict()
                # Convert timestamps to strings
                if pd.notna(row_dict.get('last_restocked')):
                    row_dict['last_restocked'] = str(row_dict['last_restocked'])
                if pd.notna(row_dict.get('last_updated')):
                    row_dict['last_updated'] = str(row_dict['last_updated'])
                
                session.run("""
                    MATCH (p:Product {product_id: $product_id})
                    CREATE (i:Inventory {
                        inventory_id: $inventory_id,
                        quantity: $quantity,
                        reorder_level: $reorder_level,
                        reorder_quantity: $reorder_quantity,
                        last_restocked: $last_restocked,
                        last_updated: $last_updated
                    })
                    CREATE (p)-[:HAS_INVENTORY]->(i)
                """, **row_dict)
        
        print(f"✅ Loaded {len(df)} inventory records")
    
    def load_batches(self):
        """Load batch/expiry data"""
        print("\n🏷️  Loading Batches...")
        
        params = POSTGRES_CONFIG.copy()
        params['database'] = 'expiry_tracking'
        conn = psycopg2.connect(**params)
        
        df = pd.read_sql("SELECT * FROM batches", conn)
        conn.close()
        
        with self.neo4j_driver.session() as session:
            for _, row in df.iterrows():
                row_dict = row.to_dict()
                # Convert dates to strings
                if pd.notna(row_dict.get('manufacturing_date')):
                    row_dict['manufacturing_date'] = str(row_dict['manufacturing_date'])
                if pd.notna(row_dict.get('expiry_date')):
                    row_dict['expiry_date'] = str(row_dict['expiry_date'])
                if pd.notna(row_dict.get('received_date')):
                    row_dict['received_date'] = str(row_dict['received_date'])
                
                session.run("""
                    MATCH (p:Product {product_id: $product_id})
                    CREATE (b:Batch {
                        batch_id: $batch_id,
                        manufacturing_date: $manufacturing_date,
                        expiry_date: $expiry_date,
                        quantity: $quantity,
                        received_date: $received_date,
                        status: $status
                    })
                    CREATE (p)-[:HAS_BATCH]->(b)
                """, **row_dict)
        
        print(f"✅ Loaded {len(df)} batches")
    
    def load_orders(self):
        """Load orders"""
        print("\n📋 Loading Orders...")
        
        params = POSTGRES_CONFIG.copy()
        params['database'] = 'inventory_mgmt'
        conn = psycopg2.connect(**params)
        
        df = pd.read_sql("SELECT * FROM orders", conn)
        conn.close()
        
        with self.neo4j_driver.session() as session:
            for _, row in df.iterrows():
                row_dict = row.to_dict()
                # Convert timestamps to strings
                if pd.notna(row_dict.get('order_date')):
                    row_dict['order_date'] = str(row_dict['order_date'])
                if pd.notna(row_dict.get('expected_delivery_date')):
                    row_dict['expected_delivery_date'] = str(row_dict['expected_delivery_date'])
                
                session.run("""
                    MATCH (s:Supplier {supplier_id: $supplier_id})
                    CREATE (o:Order {
                        order_id: $order_id,
                        order_date: $order_date,
                        expected_delivery_date: $expected_delivery_date,
                        status: $status,
                        total_amount: $total_amount
                    })
                    CREATE (o)-[:PLACED_WITH]->(s)
                """, **row_dict)
        
        print(f"✅ Loaded {len(df)} orders")
    
    def create_order_item_relationships(self):
        """Create order item relationships"""
        print("\n🔗 Creating Order-Product relationships...")
        
        params = POSTGRES_CONFIG.copy()
        params['database'] = 'inventory_mgmt'
        conn = psycopg2.connect(**params)
        
        df = pd.read_sql("SELECT * FROM order_items", conn)
        conn.close()
        
        with self.neo4j_driver.session() as session:
            for _, row in df.iterrows():
                session.run("""
                    MATCH (o:Order {order_id: $order_id})
                    MATCH (p:Product {product_id: $product_id})
                    CREATE (o)-[:CONTAINS {
                        quantity: $quantity,
                        unit_price: $unit_price
                    }]->(p)
                """, **row.to_dict())
        
        print(f"✅ Created {len(df)} order-product relationships")
    
    def load_warehouses(self):
        """Load warehouses from MongoDB"""
        print("\n🏢 Loading Warehouses...")
        
        client = MongoClient(MONGO_CONFIG['uri'])
        db = client[MONGO_CONFIG['database']]
        
        warehouses = list(db.warehouses.find())
        
        with self.neo4j_driver.session() as session:
            for warehouse in warehouses:
                session.run("""
                    CREATE (w:Warehouse {
                        warehouse_id: $warehouse_id,
                        name: $name,
                        location: $location
                    })
                """, 
                    warehouse_id=warehouse['warehouse_id'],
                    name=warehouse['name'],
                    location=warehouse['location']
                )
                
                # Create warehouse-product relationships
                for product in warehouse['products']:
                    session.run("""
                        MATCH (w:Warehouse {warehouse_id: $warehouse_id})
                        MATCH (p:Product {product_id: $product_id})
                        CREATE (w)-[:STOCKS {
                            quantity: $quantity,
                            reserved: $reserved,
                            available: $available
                        }]->(p)
                    """,
                        warehouse_id=warehouse['warehouse_id'],
                        product_id=product['product_id'],
                        quantity=product['quantity'],
                        reserved=product['reserved'],
                        available=product['available']
                    )
        
        client.close()
        print(f"✅ Loaded {len(warehouses)} warehouses")
    
    def load_shipments(self):
        """Load shipments from MongoDB"""
        print("\n🚚 Loading Shipments...")
        
        client = MongoClient(MONGO_CONFIG['uri'])
        db = client[MONGO_CONFIG['database']]
        
        shipments = list(db.shipments.find())
        
        with self.neo4j_driver.session() as session:
            for shipment in shipments:
                # Create shipment node
                session.run("""
                    CREATE (sh:Shipment {
                        shipment_id: $shipment_id,
                        tracking_number: $tracking_number,
                        carrier: $carrier,
                        status: $status,
                        origin_location: $origin_location,
                        destination_location: $destination_location,
                        current_city: $current_city,
                        estimated_arrival: $estimated_arrival
                    })
                """,
                    shipment_id=shipment['shipment_id'],
                    tracking_number=shipment['tracking_number'],
                    carrier=shipment['carrier'],
                    status=shipment['status'],
                    origin_location=shipment['origin']['location'],
                    destination_location=shipment['destination']['location'],
                    current_city=shipment['current_location']['city'],
                    estimated_arrival=shipment['destination']['estimated_arrival']
                )
                
                # Link shipment to order
                session.run("""
                    MATCH (sh:Shipment {shipment_id: $shipment_id})
                    MATCH (o:Order {order_id: $order_id})
                    CREATE (sh)-[:FULFILLS]->(o)
                """,
                    shipment_id=shipment['shipment_id'],
                    order_id=shipment['order_id']
                )
                
                # Link shipment to warehouse
                session.run("""
                    MATCH (sh:Shipment {shipment_id: $shipment_id})
                    MATCH (w:Warehouse {warehouse_id: $warehouse_id})
                    CREATE (sh)-[:SHIPS_FROM]->(w)
                """,
                    shipment_id=shipment['shipment_id'],
                    warehouse_id=shipment['origin']['warehouse_id']
                )
        
        client.close()
        print(f"✅ Loaded {len(shipments)} shipments")
    
    def create_indexes(self):
        """Create indexes for better query performance"""
        print("\n🔍 Creating indexes...")
        
        indexes = [
            "CREATE INDEX product_category IF NOT EXISTS FOR (p:Product) ON (p.category)",
            "CREATE INDEX product_name IF NOT EXISTS FOR (p:Product) ON (p.name)",
            "CREATE INDEX location_section IF NOT EXISTS FOR (l:Location) ON (l.section)",
            "CREATE INDEX order_status IF NOT EXISTS FOR (o:Order) ON (o.status)",
            "CREATE INDEX shipment_status IF NOT EXISTS FOR (sh:Shipment) ON (sh.status)",
            "CREATE INDEX batch_status IF NOT EXISTS FOR (b:Batch) ON (b.status)",
        ]
        
        with self.neo4j_driver.session() as session:
            for index in indexes:
                try:
                    session.run(index)
                except Exception as e:
                    if "already exists" not in str(e):
                        print(f"⚠️  {e}")
        
        print("✅ Indexes created")
    
    def print_statistics(self):
        """Print graph statistics"""
        print("\n📊 Knowledge Graph Statistics:")
        print("=" * 60)
        
        with self.neo4j_driver.session() as session:
            # Count nodes by label
            node_counts = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(n) as count
                ORDER BY count DESC
            """)
            
            print("\n📦 Nodes:")
            for record in node_counts:
                print(f"  {record['label']}: {record['count']}")
            
            # Count relationships by type
            rel_counts = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
                ORDER BY count DESC
            """)
            
            print("\n🔗 Relationships:")
            for record in rel_counts:
                print(f"  {record['type']}: {record['count']}")
            
            # Total counts
            total_nodes = session.run("MATCH (n) RETURN count(n) as count").single()['count']
            total_rels = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()['count']
            
            print("\n" + "=" * 60)
            print(f"Total Nodes: {total_nodes}")
            print(f"Total Relationships: {total_rels}")
            print("=" * 60)

def main():
    print("\n" + "="*60)
    print("🌐 CREATING KNOWLEDGE GRAPH IN NEO4J")
    print("="*60)
    
    builder = KnowledgeGraphBuilder()
    
    try:
        # Clear existing data
        builder.clear_database()
        
        # Create constraints and indexes
        builder.create_constraints()
        
        # Load nodes
        builder.load_products()
        builder.load_suppliers()
        builder.load_locations()
        builder.load_warehouses()
        
        # Create relationships from PostgreSQL
        builder.create_product_location_relationships()
        builder.create_product_supplier_relationships()
        builder.load_inventory()
        builder.load_batches()
        builder.load_orders()
        builder.create_order_item_relationships()
        
        # Load from MongoDB
        builder.load_shipments()
        
        # Create indexes
        builder.create_indexes()
        
        # Print statistics
        builder.print_statistics()
        
        print("\n✅ Knowledge Graph created successfully!")
        print("\n🌐 Access Neo4j Browser at: http://localhost:7474")
        print("   Username: neo4j")
        print("   Password: storechain123")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        builder.close()

if __name__ == "__main__":
    main()