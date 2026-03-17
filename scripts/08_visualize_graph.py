# scripts/08_visualize_graph.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neo4j import GraphDatabase
from config.neo4j_config import NEO4J_CONFIG

def generate_graph_schema():
    """Generate a visual schema of the knowledge graph"""
    
    driver = GraphDatabase.driver(
        NEO4J_CONFIG['uri'],
        auth=(NEO4J_CONFIG['username'], NEO4J_CONFIG['password'])
    )
    
    print("\n🎨 KNOWLEDGE GRAPH SCHEMA")
    print("="*60)
    
    with driver.session() as session:
        # Get all node labels
        labels_result = session.run("""
            CALL db.labels()
        """)
        labels = [record[0] for record in labels_result]
        
        print(f"\n📦 Node Types ({len(labels)}):")
        for label in labels:
            count = session.run(f"MATCH (n:{label}) RETURN count(n) as count").single()['count']
            print(f"  • {label}: {count} nodes")
        
        # Get all relationship types
        rel_types_result = session.run("""
            CALL db.relationshipTypes()
        """)
        rel_types = [record[0] for record in rel_types_result]
        
        print(f"\n🔗 Relationship Types ({len(rel_types)}):")
        for rel_type in rel_types:
            count = session.run(f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count").single()['count']
            print(f"  • {rel_type}: {count} relationships")
        
        # Show sample paths
        print(f"\n🛤️  Sample Paths:")
        
        paths = [
            "MATCH p=(s:Supplier)<-[:SUPPLIED_BY]-(pr:Product) RETURN p LIMIT 1",
            "MATCH p=(pr:Product)-[:LOCATED_IN]->(l:Location) RETURN p LIMIT 1",
            "MATCH p=(pr:Product)-[:HAS_INVENTORY]->(i:Inventory) RETURN p LIMIT 1",
            "MATCH p=(o:Order)-[:CONTAINS]->(pr:Product) RETURN p LIMIT 1",
            "MATCH p=(sh:Shipment)-[:FULFILLS]->(o:Order) RETURN p LIMIT 1",
        ]
        
        for path_query in paths:
            result = session.run(path_query)
            record = result.single()
            if record:
                path = record['p']
                nodes = [f"{list(n.labels)[0]}:{dict(n).get('name', dict(n).get('product_id', 'N/A'))}" 
                        for n in path.nodes]
                rels = [r.type for r in path.relationships]
                
                path_str = nodes[0]
                for i, rel in enumerate(rels, 1):
                    path_str += f" -[{rel}]-> {nodes[i]}"
                
                print(f"\n  {path_str}")
    
    driver.close()
    
    print("\n" + "="*60)
    print("✅ Schema visualization complete")
    print("\n💡 Open Neo4j Browser to see visual graph:")
    print("   http://localhost:7474")
    print("="*60)

if __name__ == "__main__":
    generate_graph_schema()