from typing import List, Dict, Any
from agents.product_agent import ProductAgent
from agents.supply_chain_agent import SupplyChainAgent
from agents.expiry_agent import ExpiryAgent
from agents.graph_agent import GraphAgent
from llm.llama_client import get_llama_client
from config.agent_config import ORCHESTRATOR_CONFIG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Master coordinator that routes queries to appropriate agents
    """
    
    def __init__(self):
        logger.info("🎯 Initializing Orchestrator...")
        
        # Initialize all agents
        self.agents = [
            ProductAgent(),
            SupplyChainAgent(),
            ExpiryAgent(),
            GraphAgent()
        ]
        
        self.llm = get_llama_client()
        self.max_agents = ORCHESTRATOR_CONFIG['max_agents_per_query']
        self.confidence_threshold = ORCHESTRATOR_CONFIG['confidence_threshold']
        
        logger.info(f"✅ Orchestrator initialized with {len(self.agents)} agents")
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Main entry point: Process user query through appropriate agents
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 New Query: {user_query}")
        logger.info(f"{'='*60}")
        
        # Select capable agents
        selected_agents = self._select_agents(user_query)
        
        if not selected_agents:
            return self._handle_no_agent(user_query)
        
        logger.info(f"📋 Selected {len(selected_agents)} agent(s):")
        for agent, confidence in selected_agents:
            logger.info(f"   • {agent.name} (confidence: {confidence:.2f})")
        
        # Execute agents
        results = []
        for agent, confidence in selected_agents:
            logger.info(f"\n🤖 Executing {agent.name}...")
            try:
                result = agent.process(user_query)
                result['confidence'] = confidence
                results.append(result)
                logger.info(f"   ✅ {agent.name} completed")
            except Exception as e:
                logger.error(f"   ❌ {agent.name} failed: {e}")
                results.append({
                    'agent': agent.name,
                    'status': 'error',
                    'error': str(e),
                    'confidence': confidence
                })
        
        # Aggregate results
        final_response = self._aggregate_results(user_query, results)
        
        logger.info(f"\n✅ Query processing complete")
        logger.info(f"{'='*60}\n")
        
        return final_response
    
    def _select_agents(self, query: str) -> List[tuple]:
        """
        Select agents that can handle the query
        Returns list of (agent, confidence) tuples
        """
        agent_scores = []
        
        for agent in self.agents:
            confidence = agent.can_handle(query)
            if confidence >= self.confidence_threshold:
                agent_scores.append((agent, confidence))
        
        # Sort by confidence (highest first)
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Limit to max agents
        return agent_scores[:self.max_agents]
    
    def _handle_no_agent(self, query: str) -> Dict[str, Any]:
        """Handle case where no agent can process the query"""
        logger.warning("⚠️  No suitable agent found for query")
        
        # Generate helpful response using LLM
        prompt = f"""The user asked: "{query}"

No specialized agent could handle this query. Provide a helpful response suggesting what kinds of questions can be answered. 

You can answer questions about:
- Products and inventory
- Shipments and deliveries
- Product expiry and batches
- Supply chain relationships

Response:"""
        
        response = self.llm.generate(prompt, max_new_tokens=150)
        
        return {
            'status': 'no_agent',
            'query': query,
            'message': response,
            'suggestions': [
                "Try asking about product inventory",
                "Check shipment status",
                "View expiring products",
                "Find supplier information"
            ]
        }
    
    def _aggregate_results(self, query: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combine results from multiple agents into unified response
        """
        if len(results) == 0:
            return self._handle_no_agent(query)
        
        if len(results) == 1:
            # Single agent response
            return self._format_single_response(results[0])
        
        # Multiple agents responded
        return self._format_multi_response(query, results)
    
    def _format_single_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format response from single agent"""
        if result['status'] == 'error':
            return {
                'status': 'error',
                'query': result.get('query', ''),
                'message': f"Error: {result.get('error', 'Unknown error')}",
                'agent': result.get('agent', 'Unknown')
            }
        
        return {
            'status': 'success',
            'query': result.get('query', ''),
            'agent': result.get('agent', ''),
            'data': result.get('data', []),
            'summary': result.get('summary', ''),
            'record_count': result.get('record_count', 0)
        }
    
    def _format_multi_response(self, query: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format response from multiple agents"""
        successful_results = [r for r in results if r['status'] == 'success']
        failed_results = [r for r in results if r['status'] == 'error']
        
        if not successful_results:
            # All agents failed
            errors = [f"{r['agent']}: {r.get('error', 'Unknown error')}" for r in failed_results]
            return {
                'status': 'error',
                'query': query,
                'message': "All agents encountered errors",
                'errors': errors
            }
        
        # Combine successful results
        combined_data = []
        individual_summaries = []
        
        for result in successful_results:
            agent_name = result.get('agent', 'Unknown Agent')
            data = result.get('data', [])
            summary = result.get('summary', '')
            
            combined_data.append({
                'agent': agent_name,
                'data': data,
                'summary': summary,
                'record_count': len(data) if isinstance(data, list) else 1
            })
            
            individual_summaries.append(f"**{agent_name}**:\n{summary}")
        
        # Generate unified summary using LLM
        unified_summary = self._create_unified_summary(query, individual_summaries)
        
        return {
            'status': 'success',
            'query': query,
            'agent_count': len(successful_results),
            'agents_used': [r['agent'] for r in successful_results],
            'combined_data': combined_data,
            'individual_summaries': individual_summaries,
            'unified_summary': unified_summary,
            'total_records': sum(r.get('record_count', 0) for r in successful_results)
        }
    
    def _create_unified_summary(self, query: str, individual_summaries: List[str]) -> str:
        """Create unified summary from multiple agent responses"""
        summaries_text = "\n\n".join(individual_summaries)
        
        prompt = f"""The user asked: "{query}"

Multiple systems provided these responses:

{summaries_text}

Provide a unified, coherent summary that combines all this information into a clear answer for the user.

Unified Summary:"""
        
        unified = self.llm.generate(prompt, max_new_tokens=300)
        return unified.strip()

# Singleton instance
_orchestrator = None

def get_orchestrator() -> Orchestrator:
    """Get or create orchestrator singleton"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator