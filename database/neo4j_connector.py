from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
from config.neo4j_config import NEO4J_CONFIG
import logging

logger = logging.getLogger(__name__)

class Neo4jConnector:
    """
    Simplified Neo4j connector for agent queries
    """
    
    def __init__(self):
        self.uri = NEO4J_CONFIG['uri']
        self.username = NEO4J_CONFIG['username']
        self.password = NEO4J_CONFIG['password']
        self.driver = None
    
    def connect(self):
        """Establish connection to Neo4j"""
        if not self.driver:
            try:
                self.driver = GraphDatabase.driver(
                    self.uri,
                    auth=(self.username, self.password)
                )
                logger.info("✅ Connected to Neo4j")
            except Exception as e:
                logger.error(f"❌ Failed to connect to Neo4j: {e}")
                raise
        return self.driver
    
    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Execute Cypher query and return results
        """
        if not self.driver:
            self.connect()
        
        logger.info(f"Executing Cypher query with parameters: {parameters}")
        logger.debug(f"Query: {query}")
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                records = [dict(record) for record in result]
                logger.info(f"Query returned {len(records)} records")
                if records:
                    logger.debug(f"First record: {records[0]}")
                return records
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameters: {parameters}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def execute_read(self, query: str, parameters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Execute read query (alias for execute_query)
        """
        return self.execute_query(query, parameters)
    
    def get_schema(self) -> str:
        """
        Get a simplified schema description
        """
        schema = """
Neo4j Knowledge Graph Schema:

Node Types:
- Product: product_id, name, category, brand, base_price
- Supplier: supplier_id, name, reliability_score
- Location: location_id, aisle, rack, shelf, section
- Inventory: quantity, reorder_level, reorder_quantity
- Batch: batch_id, expiry_date, manufacturing_date, status
- Order: order_id, order_date, status, total_amount
- Warehouse: warehouse_id, name, location
- Shipment: shipment_id, status, tracking_number, carrier

Relationships:
- (Product)-[:LOCATED_IN]->(Location)
- (Product)-[:SUPPLIED_BY]->(Supplier)
- (Product)-[:HAS_INVENTORY]->(Inventory)
- (Product)-[:HAS_BATCH]->(Batch)
- (Order)-[:CONTAINS]->(Product)
- (Order)-[:PLACED_WITH]->(Supplier)
- (Warehouse)-[:STOCKS]->(Product)
- (Shipment)-[:FULFILLS]->(Order)
- (Shipment)-[:SHIPS_FROM]->(Warehouse)
"""
        return schema
    
    def close(self):
        """Close connection"""
        if self.driver:
            self.driver.close()
            self.driver = None
            logger.info("Neo4j connection closed")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Singleton instance
_neo4j_connector = None

def get_neo4j_connector() -> Neo4jConnector:
    """Get or create Neo4j connector singleton"""
    global _neo4j_connector
    if _neo4j_connector is None:
        _neo4j_connector = Neo4jConnector()
        _neo4j_connector.connect()
    return _neo4j_connector