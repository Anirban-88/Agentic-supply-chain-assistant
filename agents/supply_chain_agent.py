from agents.base_agent import BaseAgent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SupplyChainAgent(BaseAgent):
    """
    Handles supply chain and shipment queries
    """
    
    def __init__(self):
        super().__init__(
            name="Supply Chain Agent",
            description="Handles queries about shipments, warehouses, and deliveries",
            keywords=['shipment', 'delivery', 'warehouse', 'tracking', 'eta',
                     'transit', 'shipped', 'carrier', 'arriving', 'dispatch']
        )
    
    def process(self, query: str) -> Dict[str, Any]:
        """Process supply chain queries"""
        try:
            query_lower = query.lower()
            
            if 'active' in query_lower or 'in transit' in query_lower:
                return self._get_active_shipments(query)
            
            elif 'warehouse' in query_lower:
                return self._get_warehouse_info(query)
            
            elif 'tracking' in query_lower or 'track' in query_lower:
                return self._track_shipment(query)
            
            else:
                # General shipment overview
                return self._get_shipment_summary(query)
        
        except Exception as e:
            logger.error(f"Error in SupplyChainAgent: {e}")
            return self.format_error(str(e), query)
    
    def _get_active_shipments(self, query: str) -> Dict[str, Any]:
        """Get active shipments"""
        cypher = """
        MATCH (sh:Shipment)
        WHERE sh.status IN ['in_transit', 'out_for_delivery', 'picked_up']
        RETURN sh.shipment_id, sh.tracking_number, sh.status, 
               sh.carrier, sh.current_city, sh.estimated_arrival
        ORDER BY sh.estimated_arrival
        LIMIT 20
        """
        
        results = self.execute_cypher(cypher)
        
        if results:
            summary = self.llm.summarize_results(query, results)
            return self.format_response(results, summary, query)
        else:
            return self.format_response(
                [],
                "No active shipments found. All deliveries have been completed!",
                query
            )
    
    def _get_warehouse_info(self, query: str) -> Dict[str, Any]:
        """Get warehouse information"""
        cypher = """
        MATCH (w:Warehouse)-[s:STOCKS]->(p:Product)
        WITH w, COUNT(p) as product_count, SUM(s.quantity) as total_stock
        RETURN w.warehouse_id, w.name, w.location, 
               product_count, total_stock
        ORDER BY total_stock DESC
        """
        
        results = self.execute_cypher(cypher)
        
        if results:
            summary = self.llm.summarize_results(query, results)
            return self.format_response(results, summary, query)
        else:
            return self.format_error("No warehouse information found", query)
    
    def _track_shipment(self, query: str) -> Dict[str, Any]:
        """Track specific shipment"""
        shipment_id = self.llm.extract_entity(query, "shipment ID or tracking number")
        
        cypher = """
        MATCH (sh:Shipment)
        WHERE sh.shipment_id = $shipment_id 
           OR sh.tracking_number = $shipment_id
        OPTIONAL MATCH (sh)-[:FULFILLS]->(o:Order)
        RETURN sh.shipment_id, sh.tracking_number, sh.status,
               sh.carrier, sh.current_city, sh.origin_location,
               sh.destination_location, sh.estimated_arrival,
               o.order_id
        LIMIT 1
        """
        
        results = self.execute_cypher(cypher, {'shipment_id': shipment_id})
        
        if results:
            summary = self.llm.summarize_results(query, results)
            return self.format_response(results, summary, query)
        else:
            return self.format_error(f"Shipment '{shipment_id}' not found", query)
    
    def _get_shipment_summary(self, query: str) -> Dict[str, Any]:
        """Get overall shipment statistics"""
        cypher = """
        MATCH (sh:Shipment)
        WITH sh.status as status, COUNT(*) as count
        RETURN status, count
        ORDER BY count DESC
        """
        
        results = self.execute_cypher(cypher)
        
        if results:
            summary = self.llm.summarize_results(query, results)
            return self.format_response(results, summary, query)
        else:
            return self.format_error("No shipment data found", query)