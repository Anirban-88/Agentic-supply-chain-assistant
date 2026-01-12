from abc import ABC, abstractmethod
from typing import Dict, Any, List
from llm.llama_client import get_llama_client
from database.neo4j_connector import get_neo4j_connector
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Base class for all agents
    """
    
    def __init__(self, name: str, description: str, keywords: List[str]):
        self.name = name
        self.description = description
        self.keywords = keywords
        self.llm = get_llama_client()
        self.neo4j = get_neo4j_connector()
        
        logger.info(f"✅ Initialized {self.name}")
    
    def can_handle(self, query: str) -> float:
        """
        Determine if this agent can handle the query
        Returns confidence score (0.0 to 1.0)
        """
        query_lower = query.lower()
        
        # Count keyword matches
        matches = sum(1 for keyword in self.keywords if keyword in query_lower)
        
        if matches == 0:
            return 0.0
        
        # Calculate confidence based on matches
        confidence = min(matches / 3.0, 1.0)  # Cap at 1.0
        
        return confidence
    
    @abstractmethod
    def process(self, query: str) -> Dict[str, Any]:
        """
        Process the query and return results
        Must be implemented by subclasses
        """
        pass
    
    def format_response(self, data: Any, summary: str, query: str) -> Dict[str, Any]:
        """Format successful response"""
        return {
            'agent': self.name,
            'query': query,
            'status': 'success',
            'data': data,
            'summary': summary,
            'record_count': len(data) if isinstance(data, list) else 1
        }
    
    def format_error(self, error: str, query: str) -> Dict[str, Any]:
        """Format error response"""
        return {
            'agent': self.name,
            'query': query,
            'status': 'error',
            'error': error
        }
    
    def execute_cypher(self, cypher: str, parameters: Dict = None) -> List[Dict]:
        """Execute Cypher query via Neo4j"""
        try:
            logger.info(f"{self.name} executing Cypher with params: {parameters}")
            results = self.neo4j.execute_query(cypher, parameters)
            logger.info(f"{self.name} got {len(results) if results else 0} results")
            return results
        except Exception as e:
            logger.error(f"Cypher execution error in {self.name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []