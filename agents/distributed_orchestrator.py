from typing import List, Dict, Any
import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from config.mcp_config import MCP_SERVERS, get_server_urls
from llm.llama_client import get_llama_client

logger = logging.getLogger('agents.orchestrator')

class DistributedOrchestrator:
    """
    Distributed orchestrator that routes queries to MCP agent servers via HTTP
    """
    
    def __init__(self):
        logger.info("🎯 Initializing Distributed Orchestrator...")
        
        self.server_urls = get_server_urls()
        self.llm = get_llama_client()
        self.max_parallel_agents = 3
        self.confidence_threshold = 0.2
        self.request_timeout = 60
        
        # Get agent capabilities from servers
        self.agents_info = {}
        self._load_agent_capabilities()
        
        logger.info(f"✅ Distributed Orchestrator initialized with {len(self.agents_info)} agent servers")
    
    def _load_agent_capabilities(self):
        """Load capabilities from all agent servers"""
        for server_id, url in self.server_urls.items():
            if server_id == 'orchestrator':
                continue
            
            try:
                response = requests.get(f"{url}/capabilities", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.agents_info[server_id] = {
                        'name': data.get('name', server_id),
                        'description': data.get('description', ''),
                        'keywords': data.get('keywords', []),
                        'url': url
                    }
                    logger.info(f"✅ Loaded capabilities for {server_id}: {data.get('name')}")
            except Exception as e:
                logger.error(f"❌ Failed to load capabilities for {server_id}: {e}")
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Main entry point: Process user query through appropriate agent servers
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 New Query: {user_query}")
        logger.info(f"{'='*60}")
        
        # Select capable agents
        selected_agents = self._select_agents(user_query)
        
        if not selected_agents:
            return self._handle_no_agent(user_query)
        
        logger.info(f"📋 Selected {len(selected_agents)} agent(s):")
        for server_id, confidence in selected_agents:
            agent_name = self.agents_info[server_id]['name']
            logger.info(f"   • {agent_name} (confidence: {confidence:.2f})")
        
        # Execute agents via HTTP
        results = []
        for server_id, confidence in selected_agents:
            logger.info(f"\n🤖 Calling {self.agents_info[server_id]['name']} via HTTP...")
            try:
                result = self._call_agent_server(server_id, user_query)
                result['confidence'] = confidence
                results.append(result)
                logger.info(f"   ✅ {self.agents_info[server_id]['name']} completed")
            except Exception as e:
                logger.error(f"   ❌ {self.agents_info[server_id]['name']} failed: {e}")
                results.append({
                    'agent': self.agents_info[server_id]['name'],
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
        Select agents based on query keywords
        Returns list of (server_id, confidence) tuples
        """
        query_lower = query.lower()
        agent_scores = []
        
        for server_id, info in self.agents_info.items():
            # Count keyword matches
            matches = sum(1 for keyword in info['keywords'] if keyword in query_lower)
            
            if matches > 0:
                confidence = min(matches / 3.0, 1.0)
                agent_scores.append((server_id, confidence))
        
        # Sort by confidence and take top agents
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Filter by threshold and limit
        selected = [(sid, conf) for sid, conf in agent_scores 
                   if conf >= self.confidence_threshold][:self.max_parallel_agents]
        
        return selected
    
    def _call_agent_server(self, server_id: str, query: str) -> Dict[str, Any]:
        """
        Call an agent server via HTTP
        
        Args:
            server_id: Agent server identifier
            query: User query
            
        Returns:
            Agent response dictionary
        """
        url = self.agents_info[server_id]['url']
        
        try:
            response = requests.post(
                f"{url}/query",
                json={"query": query},
                timeout=self.request_timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract result from MCP response
            if 'result' in data:
                return data['result']
            return data
            
        except requests.exceptions.Timeout:
            return {
                'agent': self.agents_info[server_id]['name'],
                'status': 'error',
                'error': f'Request timeout after {self.request_timeout}s'
            }
        except requests.exceptions.ConnectionError:
            return {
                'agent': self.agents_info[server_id]['name'],
                'status': 'error',
                'error': f'Cannot connect to agent server at {url}'
            }
        except Exception as e:
            return {
                'agent': self.agents_info[server_id]['name'],
                'status': 'error',
                'error': str(e)
            }
    
    def _aggregate_results(self, query: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from multiple agents"""
        successful_results = [r for r in results if r.get('status') == 'success']
        error_results = [r for r in results if r.get('status') == 'error']
        
        if not successful_results and error_results:
            # All agents failed
            return {
                'status': 'error',
                'query': query,
                'message': f"All agents encountered errors",
                'errors': [r.get('error', 'Unknown error') for r in error_results],
                'agent': error_results[0].get('agent', 'Unknown') if error_results else 'Unknown'
            }
        
        if not successful_results:
            return self._handle_no_agent(query)
        
        # Single agent response
        if len(successful_results) == 1:
            return successful_results[0]
        
        # Multiple agent responses - combine them
        combined_data = []
        individual_summaries = []
        
        for result in successful_results:
            combined_data.append({
                'agent': result.get('agent', 'Unknown'),
                'data': result.get('data', []),
                'record_count': result.get('record_count', 0)
            })
            
            if 'summary' in result:
                individual_summaries.append(f"**{result['agent']}:**\n{result['summary']}")
        
        # Create unified summary
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
    
    def _handle_no_agent(self, query: str) -> Dict[str, Any]:
        """Handle case when no agent can process the query"""
        return {
            'status': 'no_agent',
            'query': query,
            'message': "I couldn't find a suitable agent to handle your query.",
            'suggestions': [
                "Try asking about products, inventory, shipments, or expiry dates",
                "Be more specific about what information you need",
                "Use keywords like: product, stock, shipment, expiry, batch, supplier"
            ]
        }


# Singleton instance
_distributed_orchestrator = None

def get_distributed_orchestrator() -> DistributedOrchestrator:
    """Get or create distributed orchestrator singleton"""
    global _distributed_orchestrator
    if _distributed_orchestrator is None:
        _distributed_orchestrator = DistributedOrchestrator()
    return _distributed_orchestrator
