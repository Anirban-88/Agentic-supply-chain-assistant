# scripts/07_test_queries.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neo4j import GraphDatabase
from config.neo4j_config import NEO4J_CONFIG
import json

class QueryTester:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_CONFIG['uri'],
            auth=(NEO4J_CONFIG['username'], NEO4J_CONFIG['password'])
        )
    
    def close(self):
        self.driver.close()
    
    def run_query(self, query, description):
        print(f"\n{'='*60}")
        print(f"🔍 {description}")
        print(f"{'='*60}")
        print(f"\nQuery:\n{query}\n")
        
        with self.driver.session() as session:
            result = session.run(query)
            records = list(result)
            
            if len(records) == 0:
                print("No results found")
            else:
                for i, record in enumerate(records[:10], 1):  # Show first 10
                    print(f"{i}. {dict(record)}")
                
                if len(records) > 10:
                    print(f"\n... and {len(records) - 10} more results")
        
        return records

def main():
    print("\n" + "="*60)
    print("🧪 TESTING KNOWLEDGE GRAPH QUERIES")
    print("="*60)
    
    tester = QueryTester()
    
    try:
        # Query 1: Find all products in a specific category
        tester.run_query("""
            MATCH (p:Product)
            WHERE p.category = 'Dairy'
            RETURN p.product_id, p.name, p.base_price
            LIMIT 5
        """, "Query 1: All Dairy Products")
        
        # Query 2: Find products and their locations
        tester.run_query("""
            MATCH (p:Product)-[:LOCATED_IN]->(l:Location)
            RETURN p.name, l.aisle, l.rack, l.shelf
            LIMIT 5
        """, "Query 2: Products and Their Locations")
        
        # Query 3: Find products with low inventory
        tester.run_query("""
            MATCH (p:Product)-[:HAS_INVENTORY]->(i:Inventory)
            WHERE i.quantity < i.reorder_level
            RETURN p.product_id, p.name, i.quantity, i.reorder_level
            LIMIT 5
        """, "Query 3: Products with Low Inventory")
        
        # Query 4: Find products expiring soon
        tester.run_query("""
            MATCH (p:Product)-[:HAS_BATCH]->(b:Batch)
            WHERE b.status IN ['near_expiry', 'critical']
            RETURN p.name, b.batch_id, b.expiry_date, b.status
            LIMIT 5
        """, "Query 4: Products Expiring Soon")
        
        # Query 5: Find supplier with most products
        tester.run_query("""
            MATCH (p:Product)-[:SUPPLIED_BY]->(s:Supplier)
            RETURN s.name, s.supplier_id, count(p) as product_count
            ORDER BY product_count DESC
            LIMIT 5
        """, "Query 5: Top Suppliers by Product Count")
        
        # Query 6: Track shipment status
        tester.run_query("""
            MATCH (sh:Shipment)-[:FULFILLS]->(o:Order)
            RETURN sh.shipment_id, sh.status, sh.current_city, 
                   sh.estimated_arrival, o.order_id
            LIMIT 5
        """, "Query 6: Active Shipments")
        
        # Query 7: Find products in multiple locations
        tester.run_query("""
            MATCH (p:Product)-[:LOCATED_IN]->(l:Location)
            WITH p, count(l) as location_count
            WHERE location_count > 1
            RETURN p.product_id, p.name, location_count
            ORDER BY location_count DESC
            LIMIT 5
        """, "Query 7: Products in Multiple Locations")
        
        # Query 8: Warehouse inventory levels
        tester.run_query("""
            MATCH (w:Warehouse)-[s:STOCKS]->(p:Product)
            WHERE w.warehouse_id = 'WH001'
            RETURN p.name, s.quantity, s.available, s.reserved
            LIMIT 5
        """, "Query 8: Warehouse Inventory (WH001)")
        
        # Query 9: Complete supply chain path
        tester.run_query("""
            MATCH path = (s:Supplier)<-[:SUPPLIED_BY]-(p:Product)
                         -[:HAS_INVENTORY]->(i:Inventory)
            RETURN s.name as supplier, p.name as product, i.quantity
            LIMIT 5
        """, "Query 9: Supply Chain Path (Supplier to Inventory)")
        
        # Query 10: Orders by status
        tester.run_query("""
            MATCH (o:Order)
            RETURN o.status, count(o) as count
            ORDER BY count DESC
        """, "Query 10: Orders by Status")
        
        print("\n" + "="*60)
        print("✅ QUERY TESTING COMPLETE")
        print("="*60)
        
    finally:
        tester.close()

if __name__ == "__main__":
    main()