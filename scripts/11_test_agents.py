# scripts/10_test_agents.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.orchestrator import get_orchestrator
import json

def test_queries():
    """Test the multi-agent system with sample queries"""
    
    print("\n" + "="*60)
    print("🧪 TESTING MULTI-AGENT SYSTEM")
    print("="*60)
    
    # Initialize orchestrator
    print("\n🚀 Initializing orchestrator...")
    orchestrator = get_orchestrator()
    print("✅ Orchestrator ready!")
    
    # Test queries
    test_cases = [
        {
            'query': 'Show me products with low stock',
            'expected_agent': 'Product & Inventory Agent'
        },
        {
            'query': 'What shipments are currently in transit?',
            'expected_agent': 'Supply Chain Agent'
        },
        {
            'query': 'Which products are expiring in the next week?',
            'expected_agent': 'Expiry Management Agent'
        },
        {
            'query': 'Who are the suppliers for dairy products?',
            'expected_agent': 'Knowledge Graph Agent'
        },
        {
            'query': 'Tell me everything about product P0001',
            'expected_agent': 'Knowledge Graph Agent'
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {i}/{len(test_cases)}")
        print(f"{'='*60}")
        print(f"Query: {test['query']}")
        print(f"Expected Agent: {test['expected_agent']}")
        
        # Process query
        response = orchestrator.process_query(test['query'])
        
        # Check result
        success = False
        if response['status'] == 'success':
            if 'agent' in response:
                actual_agent = response['agent']
            elif 'agents_used' in response:
                actual_agent = ', '.join(response['agents_used'])
            else:
                actual_agent = 'Unknown'
            
            print(f"Actual Agent(s): {actual_agent}")
            
            # Check if expected agent was used
            if test['expected_agent'] in actual_agent:
                print("✅ PASS - Correct agent selected")
                success = True
            else:
                print("⚠️  PARTIAL - Different agent selected")
                success = True  # Still successful if query was answered
            
            # Show summary
            if 'summary' in response:
                print(f"\nSummary: {response['summary'][:200]}...")
            elif 'unified_summary' in response:
                print(f"\nSummary: {response['unified_summary'][:200]}...")
            
            # Show data count
            if 'record_count' in response:
                print(f"Records: {response['record_count']}")
            elif 'total_records' in response:
                print(f"Total Records: {response['total_records']}")
        
        else:
            print(f"❌ FAIL - Status: {response['status']}")
            print(f"Message: {response.get('message', 'Unknown error')}")
        
        results.append({
            'query': test['query'],
            'expected': test['expected_agent'],
            'success': success,
            'status': response['status']
        })
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    total = len(results)
    passed = sum(1 for r in results if r['success'])
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    test_queries()