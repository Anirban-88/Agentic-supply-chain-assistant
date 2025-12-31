

from agents.base_agent import BaseAgent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class GraphAgent(BaseAgent):
    """
    Handles complex knowledge graph queries
    """
    
    def __init__(self):
        super().__init__(
            name="Knowledge Graph Agent",
            description="Handles complex cross-database queries and relationships",
            keywords=['relationship', 'connected', 'supplier', 'supply chain',
                     'path', 'network', 'everything', 'complete', 'related', 'all']
        )
    
    def process(self, query: str) -> Dict[str, Any]:
        """Process knowledge graph queries"""
        try:
            query_lower = query.lower()
            
            if 'supplier' in query_lower and 'product' in query_lower:
                return self._get_product_suppliers(query)
            
            elif 'supply chain' in query_lower or 'path' in query_lower:
                return self._get_supply_chain_path(query)
            
            elif 'everything' in query_lower or 'complete' in query_lower or 'all about' in query_lower:
                return self._get_complete_info(query)
            
            else:
                # Try to generate dynamic Cypher
                return self._dynamic_query(query)
        
        except Exception as e:
            logger.error(f"Error in GraphAgent: {e}")
            return self.format_error(str(e), query)
    
    def _get_product_suppliers(self, query: str) -> Dict[str, Any]:
        """Get suppliers for a product"""
        product_name = self.llm.extract_entity(query, "product name")
        
        cypher = """
        MATCH (p:Product)-[r:SUPPLIED_BY]->(s:Supplier)
        WHERE toLower(p.name) CONTAINS toLower($product_name)
        RETURN p.product_id, p.name, p.category,
               s.supplier_id, s.name as supplier_name,
               s.reliability_score, s.average_lead_time_days,
               r.unit_cost, r.minimum_order_quantity
        LIMIT 10
        """
        
        results = self.execute_cypher(cypher, {'product_name': product_name})
        
        if results:
            summary = self.llm.summarize_results(query, results)
            return self.format_response(results, summary, query)
        else:
            return self.format_error(f"No suppliers found for '{product_name}'", query)
    
    def _get_supply_chain_path(self, query: str) -> Dict[str, Any]:
        """Get supply chain paths"""
        cypher = """
        MATCH path = (s:Supplier)<-[:SUPPLIED_BY]-(p:Product)-[:HAS_INVENTORY]->(i:Inventory)
        WHERE i.quantity < i.reorder_level
        RETURN s.name as supplier,
               p.name as product,
               p.category,
               i.quantity as current_stock,
               i.reorder_level,
               s.average_lead_time_days as lead_time
        LIMIT 15
        """
        
        results = self.execute_cypher(cypher)
        
        if results:
            summary = self.llm.summarize_results(query, results)
            return self.format_response(results, summary, query)
        else:
            return self.format_error("No supply chain data found", query)
    
    def _get_complete_info(self, query: str) -> Dict[str, Any]:
        """Get complete information about an entity"""
        entity = self.llm.extract_entity(query, "product or entity name")
        
        cypher = """
        MATCH (p:Product)
        WHERE toLower(p.name) CONTAINS toLower($entity)
        
        OPTIONAL MATCH (p)-[:LOCATED_IN]->(l:Location)
        OPTIONAL MATCH (p)-[:SUPPLIED_BY]->(s:Supplier)
        OPTIONAL MATCH (p)-[:HAS_INVENTORY]->(i:Inventory)
        OPTIONAL MATCH (p)-[:HAS_BATCH]->(b:Batch)
        WHERE b.status IN ['active', 'near_expiry']
        
        RETURN p.product_id, p.name, p.category, p.brand, p.base_price,
               collect(DISTINCT {aisle: l.aisle, rack: l.rack, shelf: l.shelf}) as locations,
               collect(DISTINCT {name: s.name, reliability: s.reliability_score}) as suppliers,
               i.quantity as stock,
               i.reorder_level,
               count(DISTINCT b) as active_batches
        LIMIT 1
        """
        
        results = self.execute_cypher(cypher, {'entity': entity})
        
        if results:
            summary = self.llm.summarize_results(query, results)
            return self.format_response(results, summary, query)
        else:
            return self.format_error(f"No information found for '{entity}'", query)
    
    def _dynamic_query(self, query: str) -> Dict[str, Any]:
        """Generate and execute Cypher dynamically"""
        try:
            # Get schema
            schema = self.neo4j.get_schema()
            
            # Generate Cypher using LLM
            cypher = self.llm.generate_cypher(query, schema)
            
            logger.info(f"Generated Cypher: {cypher}")
            
            # Execute
            results = self.execute_cypher(cypher)
            
            if results:
                summary = self.llm.summarize_results(query, results)
                return self.format_response(results, summary, query)
            else:
                return self.format_error("Query executed but returned no results", query)
        
        except Exception as e:
            logger.error(f"Error in dynamic query: {e}")
            return self.format_error(f"Could not process query: {str(e)}", query)