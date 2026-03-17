# agents/expiry_agent.py

from agents.base_agent import BaseAgent
from typing import Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ExpiryAgent(BaseAgent):
    """
    Handles expiry and batch queries
    """
    
    def __init__(self):
        super().__init__(
            name="Expiry Management Agent",
            description="Handles queries about product expiry, batches, and freshness",
            keywords=['expiry', 'expire', 'expiring', 'batch', 'fresh',
                     'shelf life', 'manufacturing', 'perishable', 'best before']
        )
    
    def process(self, query: str) -> Dict[str, Any]:
        """Process expiry-related queries"""
        try:
            query_lower = query.lower()
            
            if 'expiring soon' in query_lower or 'near expiry' in query_lower:
                return self._get_expiring_soon(query)
            
            elif 'expired' in query_lower:
                return self._get_expired_products(query)
            
            elif 'batch' in query_lower:
                return self._get_batch_info(query)
            
            else:
                # General expiry overview
                return self._get_expiry_summary(query)
        
        except Exception as e:
            logger.error(f"Error in ExpiryAgent: {e}")
            return self.format_error(str(e), query)
    
    def _get_expiring_soon(self, query: str) -> Dict[str, Any]:
        """Get products expiring soon"""
        cypher = """
        MATCH (p:Product)-[:HAS_BATCH]->(b:Batch)
        WHERE b.status IN ['active', 'near_expiry']
          AND b.expiry_date IS NOT NULL
        WITH p, b, 
             duration.between(date(), date(b.expiry_date)).days as days_until_expiry
        WHERE days_until_expiry <= 7 AND days_until_expiry >= 0
        RETURN p.product_id, p.name, p.category,
               b.batch_id, b.expiry_date, b.quantity, b.status,
               days_until_expiry
        ORDER BY days_until_expiry
        LIMIT 20
        """
        
        results = self.execute_cypher(cypher)
        
        if results:
            summary = self.llm.summarize_results(query, results)
            return self.format_response(results, summary, query)
        else:
            return self.format_response(
                [],
                "No products expiring in the next 7 days. All batches are fresh!",
                query
            )
    
    def _get_expired_products(self, query: str) -> Dict[str, Any]:
        """Get expired products"""
        cypher = """
        MATCH (p:Product)-[:HAS_BATCH]->(b:Batch)
        WHERE b.status = 'expired'
        WITH p, b,
             duration.between(date(b.expiry_date), date()).days as days_expired
        RETURN p.product_id, p.name, p.category,
               b.batch_id, b.expiry_date, b.quantity,
               days_expired
        ORDER BY days_expired DESC
        LIMIT 20
        """
        
        results = self.execute_cypher(cypher)
        
        if results:
            summary = self.llm.summarize_results(query, results)
            return self.format_response(results, summary, query)
        else:
            return self.format_response(
                [],
                "No expired products found. Great inventory management!",
                query
            )
    
    def _get_batch_info(self, query: str) -> Dict[str, Any]:
        """Get information about specific batch"""
        batch_id = self.llm.extract_entity(query, "batch ID")
        
        cypher = """
        MATCH (p:Product)-[:HAS_BATCH]->(b:Batch)
        WHERE b.batch_id = $batch_id
        WITH p, b,
             duration.between(date(), date(b.expiry_date)).days as days_until_expiry
        RETURN p.product_id, p.name, p.category,
               b.batch_id, b.manufacturing_date, b.expiry_date,
               b.quantity, b.status, days_until_expiry
        """
        
        results = self.execute_cypher(cypher, {'batch_id': batch_id})
        
        if results:
            summary = self.llm.summarize_results(query, results)
            return self.format_response(results, summary, query)
        else:
            return self.format_error(f"Batch '{batch_id}' not found", query)
    
    def _get_expiry_summary(self, query: str) -> Dict[str, Any]:
        """Get overall expiry statistics"""
        cypher = """
        MATCH (p:Product)-[:HAS_BATCH]->(b:Batch)
        WITH p.category as category,
             COUNT(b) as total_batches,
             SUM(CASE WHEN b.status = 'active' THEN 1 ELSE 0 END) as active,
             SUM(CASE WHEN b.status = 'near_expiry' THEN 1 ELSE 0 END) as near_expiry,
             SUM(CASE WHEN b.status = 'expired' THEN 1 ELSE 0 END) as expired
        RETURN category, total_batches, active, near_expiry, expired
        ORDER BY near_expiry DESC, expired DESC
        """
        
        results = self.execute_cypher(cypher)
        
        if results:
            summary = self.llm.summarize_results(query, results)
            return self.format_response(results, summary, query)
        else:
            return self.format_error("No batch data found", query)