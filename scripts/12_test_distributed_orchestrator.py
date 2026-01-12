import sys
import os
import requests
import json
import time
from typing import Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.mcp_config import ORCHESTRATOR_CONFIG, MCP_SERVERS
from config.logging_config import setup_logging

# Setup logging
setup_logging()
import logging
logger = logging.getLogger(__name__)


def test_health_checks():
    """Test health endpoints of all servers"""
    print("\n" + "="*60)
    print("Testing Health Checks")
    print("="*60)
    
    # Test orchestrator
    orchestrator_url = f"http://localhost:{ORCHESTRATOR_CONFIG['port']}/health"
    try:
        response = requests.get(orchestrator_url, timeout=2)
        if response.status_code == 200:
            print(f"✅ Orchestrator (port {ORCHESTRATOR_CONFIG['port']}): {response.json()['status']}")
        else:
            print(f"❌ Orchestrator (port {ORCHESTRATOR_CONFIG['port']}): HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Orchestrator (port {ORCHESTRATOR_CONFIG['port']}): {e}")
    
    # Test agent servers
    for server_id, config in MCP_SERVERS.items():
        if config['enabled']:
            url = f"http://localhost:{config['port']}/health"
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    print(f"✅ {server_id} (port {config['port']}): {response.json()['status']}")
                else:
                    print(f"❌ {server_id} (port {config['port']}): HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ {server_id} (port {config['port']}): {e}")


def test_capabilities():
    """Test capabilities endpoint of orchestrator"""
    print("\n" + "="*60)
    print("Testing Orchestrator Capabilities")
    print("="*60)
    
    url = f"http://localhost:{ORCHESTRATOR_CONFIG['port']}/capabilities"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            capabilities = response.json()
            print(f"✅ Orchestrator capabilities loaded")
            
            # Check if it's the distributed format (dict) or old format (list)
            if 'agents' in capabilities:
                agents = capabilities['agents']
                if isinstance(agents, dict):
                    # Distributed orchestrator format
                    print(f"\n📡 Using Distributed Architecture")
                    print(f"Available agents: {len(agents)}")
                    for agent_id, agent_info in agents.items():
                        print(f"  - {agent_id}:")
                        print(f"    URL: {agent_info.get('url', 'N/A')}")
                        print(f"    Capabilities: {', '.join(agent_info.get('capabilities', []))}")
                elif isinstance(agents, list):
                    # Old in-process format
                    print(f"\n⚠️  Using In-Process Architecture (not distributed)")
                    print(f"Available agents: {len(agents)}")
                    for agent_name in agents:
                        print(f"  - {agent_name}")
            else:
                print("❌ No agents found in capabilities")
        else:
            print(f"❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_query(query: str, expected_agent: str = None):
    """
    Test a query through the distributed orchestrator
    
    Args:
        query: Query string to test
        expected_agent: Expected agent ID that should handle the query (optional)
    """
    print("\n" + "="*60)
    print(f"Testing Query: {query}")
    print("="*60)
    
    url = f"http://localhost:{ORCHESTRATOR_CONFIG['port']}/query"
    payload = {"query": query}
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=30)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query successful ({elapsed:.2f}s)")
            
            # Check different response formats
            selected_agent = result.get('selected_agent') or result.get('agent')
            response_text = result.get('response') or result.get('answer') or str(result.get('result', 'No response'))
            
            print(f"\nSelected Agent: {selected_agent or 'Unknown'}")
            
            if expected_agent and selected_agent != expected_agent:
                print(f"⚠️  Expected {expected_agent}, got {selected_agent}")
            
            print(f"\nResponse:")
            print("-" * 60)
            print(response_text)
            print("-" * 60)
            
            # Check if distributed architecture was used
            metadata = result.get('metadata', {})
            if 'agent_server_url' in metadata:
                print(f"\n📡 Agent server called: {metadata['agent_server_url']}")
            elif selected_agent is None:
                print(f"\n⚠️  No agent selection detected - may be using in-process mode")
            
            return True
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_test_suite():
    """Run complete test suite"""
    print("\n" + "="*80)
    print(" DISTRIBUTED ORCHESTRATOR TEST SUITE")
    print("="*80)
    
    # Wait a bit for servers to be ready
    print("\nWaiting for servers to be ready...")
    time.sleep(2)
    
    # Test health checks
    test_health_checks()
    
    # Test capabilities
    test_capabilities()
    
    # Test queries
    test_queries = [
        ("Tell me about product P0001", "product"),
        ("What is the price of P0001?", "product"),
        ("Check shipment status for order 1", "supply_chain"),
        ("Show me expiring products", "expiry"),
        ("What products are supplied by S0001?", "graph"),
        ("Give me complete information about product P0001", "graph"),
    ]
    
    successful = 0
    for query, expected_agent in test_queries:
        if test_query(query, expected_agent):
            successful += 1
        time.sleep(1)  # Brief pause between queries
    
    # Summary
    print("\n" + "="*80)
    print(" TEST SUMMARY")
    print("="*80)
    print(f"Successful queries: {successful}/{len(test_queries)}")
    
    if successful == len(test_queries):
        print("\n✅ All tests passed!")
    else:
        print(f"\n⚠️  {len(test_queries) - successful} test(s) failed")
    
    print("\n💡 Check logs/mcp_servers.log to see HTTP communication between services")


if __name__ == "__main__":
    try:
        run_test_suite()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        logger.error(f"Test error: {e}", exc_info=True)
        sys.exit(1)
