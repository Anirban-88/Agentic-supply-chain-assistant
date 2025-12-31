

from agents.base_agent import BaseAgent
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class ProductAgent(BaseAgent):
    """
    Handles product and inventory queries
    """
    
    def __init__(self):
        super().__init__(
            name="Product & Inventory Agent",
            description="Handles queries about products, inventory, locations, and stock levels",
            keywords=['product', 'inventory', 'stock', 'quantity', 'price', 
                     'location', 'aisle', 'rack', 'shelf', 'reorder', 'item']
        )
    
    def process(self, query: str) -> Dict[str, Any]:
        """Process product-related queries"""
        try:
            query_lower = query.lower()
            
            # Detect query type
            if 'low stock' in query_lower or 'reorder' in query_lower:
                return self._get_low_stock_products(query)
            
            elif 'location' in query_lower or 'where' in query_lower:
                return self._get_product_location(query)
            
            elif 'price' in query_lower:
                return self._get_product_price(query)
            
            elif 'inventory' in query_lower or 'stock' in query_lower:
                return self._get_inventory_info(query)
            
            else:
                # General product search
                return self._search_products(query)
        
        except Exception as e:
            logger.error(f"Error in ProductAgent: {e}")
            return self.format_error(str(e), query)
    
    def _get_low_stock_products(self, query: str) -> Dict[str, Any]:
        """Get products with low stock"""
        cypher = """
        MATCH (p:Product)-[:HAS_INVENTORY]->(i:Inventory)
        WHERE i.quantity < i.reorder_level
        RETURN p.product_id, p.name, p.category, p.base_price,
               i.quantity, i.reorder_level
        ORDER BY i.quantity
        LIMIT 20
        """
        
        results = self.execute_cypher(cypher)
        
        if results:
            summary = self.llm.summarize_results(query, results)
            return self.format_response(results, summary, query)
        else:
            return self.format_response(
                [],
                "No products found with low stock. All inventory levels are healthy!",
                query
            )
    
    def _get_product_location(self, query: str) -> Dict[str, Any]:
        """Get product location"""
        # Extract product name
        product_name = self.llm.extract_entity(query, "product name")
        
        cypher = """
        MATCH (p:Product)-[:LOCATED_IN]->(l:Location)
        WHERE toLower(p.name) CONTAINS toLower($product_name)
        RETURN p.product_id, p.name, p.category,
               l.aisle, l.rack, l.shelf, l.section
        LIMIT 5
        """
        
        results = self.execute_cypher(cypher, {'product_name': product_name})
        
        if results:
            summary = self.llm.summarize_results(query, results)
            return self.format_response(results, summary, query)
        else:
            return self.format_error(f"Product '{product_name}' not found in any location", query)
    
    def _get_product_price(self, query: str) -> Dict[str, Any]:
        """Get product price"""
        product_name = self.llm.extract_entity(query, "product name")
        
        cypher = """
        MATCH (p:Product)
        WHERE toLower(p.name) CONTAINS toLower($product_name)
        RETURN p.product_id, p.name, p.brand, p.category, p.base_price
        LIMIT 5
        """
        
        results = self.execute_cypher(cypher, {'product_name': product_name})
        
        if results:
            summary = self.llm.summarize_results(query, results)
            return self.format_response(results, summary, query)
        else:
            return self.format_error(f"Product '{product_name}' not found", query)
    
    def _get_inventory_info(self, query: str) -> Dict[str, Any]:
        """Get inventory information"""
        # Check if asking about specific product
        if any(word in query.lower() for word in ['milk', 'bread', 'juice', 'water']):
            product_name = self.llm.extract_entity(query, "product name")
            
            cypher = """
            MATCH (p:Product)-[:HAS_INVENTORY]->(i:Inventory)
            WHERE toLower(p.name) CONTAINS toLower($product_name)
            RETURN p.product_id, p.name, p.category,
                   i.quantity, i.reorder_level, i.reorder_quantity,
                   i.last_restocked
            LIMIT 5
            """
            
            results = self.execute_cypher(cypher, {'product_name': product_name})
        else:
            # General inventory summary
            cypher = """
            MATCH (p:Product)-[:HAS_INVENTORY]->(i:Inventory)
            WITH p.category as category, 
                 COUNT(p) as product_count,
                 SUM(i.quantity) as total_quantity,
                 SUM(CASE WHEN i.quantity < i.reorder_level THEN 1 ELSE 0 END) as low_stock_count
            RETURN category, product_count, total_quantity, low_stock_count
            ORDER BY total_quantity DESC
            LIMIT 10
            """
            
            results = self.execute_cypher(cypher)
        
        if results:
            summary = self.llm.summarize_results(query, results)
            return self.format_response(results, summary, query)
        else:
            return self.format_error("No inventory information found", query)
    
    def _search_products(self, query: str) -> Dict[str, Any]:
        """General product search"""
        search_term = self.llm.extract_entity(query, "search term")
        
        cypher = """
        MATCH (p:Product)
        WHERE toLower(p.name) CONTAINS toLower($search_term)
           OR toLower(p.category) CONTAINS toLower($search_term)
        RETURN p.product_id, p.name, p.category, p.brand, p.base_price
        LIMIT 10
        """
        
        results = self.execute_cypher(cypher, {'search_term': search_term})
        
        if results:
            summary = self.llm.summarize_results(query, results)
            return self.format_response(results, summary, query)
        else:
            return self.format_error(f"No products found matching '{search_term}'", query)