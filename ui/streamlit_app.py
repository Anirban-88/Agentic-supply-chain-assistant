import streamlit as st
import sys
import os
import requests
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

# MCP Server Configuration
ORCHESTRATOR_URL = os.getenv('ORCHESTRATOR_URL', 'http://localhost:8000')
USE_MCP_SERVERS = os.getenv('USE_MCP_SERVERS', 'true').lower() == 'true'

# Page configuration
st.set_page_config(
    page_title="Store Supply Chain Assistant",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-badge {
        background-color: #2c3e50;
        color: #ffffff;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.5rem;
        display: inline-block;
        font-size: 0.9rem;
        font-weight: 500;
        border: 2px solid #34495e;
    }
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'use_mcp' not in st.session_state:
    st.session_state.use_mcp = USE_MCP_SERVERS

# Only initialize orchestrator if not using MCP servers
if not st.session_state.use_mcp:
    if 'orchestrator' not in st.session_state:
        with st.spinner("🚀 Initializing AI Agents..."):
            from agents.orchestrator import get_orchestrator
            st.session_state.orchestrator = get_orchestrator()


def query_mcp_server(query: str) -> dict:
    """Query the MCP orchestrator server via HTTP"""
    try:
        response = requests.post(
            f"{ORCHESTRATOR_URL}/query",
            json={"query": query},
            timeout=120
        )
        response.raise_for_status()
        data = response.json()
        
        # Extract the result from MCP server response
        if 'result' in data:
            return data['result']
        return data
        
    except requests.exceptions.ConnectionError:
        return {
            'status': 'error',
            'message': f'Cannot connect to MCP server at {ORCHESTRATOR_URL}. Please ensure the servers are running with: python scripts/10_start_mcp_servers.py --subprocess'
        }
    except requests.exceptions.Timeout:
        return {
            'status': 'error',
            'message': 'Request timed out. The query may be taking too long to process.'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error querying MCP server: {str(e)}'
        }


def process_query(query: str) -> dict:
    """Process query using either MCP server or direct orchestrator"""
    if st.session_state.use_mcp:
        return query_mcp_server(query)
    else:
        return st.session_state.orchestrator.process_query(query)

# Sidebar
with st.sidebar:
    st.image("app_logo.png", use_container_width=True)
    
    # Mode selector
    st.markdown("## ⚙️ Configuration")
    use_mcp = st.toggle("Use MCP Servers", value=st.session_state.use_mcp, 
                        help="Enable to use distributed MCP servers (port 8000), disable for direct in-process calls")
    if use_mcp != st.session_state.use_mcp:
        st.session_state.use_mcp = use_mcp
        st.rerun()
    
    if st.session_state.use_mcp:
        st.success("🌐 Using MCP Servers")
        st.caption(f"Orchestrator: {ORCHESTRATOR_URL}")
    else:
        st.info("💻 Using Direct Mode")
        st.caption("In-process agents")
    
    st.markdown("---")
    
    st.markdown("## 🤖 Active Agents")
    st.markdown("""
    <div class="agent-badge">📦 Product Agent</div>
    <div class="agent-badge">🚚 Supply Chain Agent</div>
    <div class="agent-badge">⏰ Expiry Agent</div>
    <div class="agent-badge">🕸️ Graph Agent</div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("## 💡 Sample Queries")
    
    sample_queries = [
        "Show products with low stock",
        "What is the price of milk?",
        "Show active shipments",
        "Which products are expiring soon?",
        "Where is bread located?",
        "Show warehouse inventory",
        "Who supplies dairy products?",
        "Show me everything about product P0001"
    ]
    
    for query in sample_queries:
        if st.button(query, key=f"sample_{query}"):
            st.session_state.current_query = query
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔧 System Info")
    st.markdown(f"**Agents:** 4 active")
    st.markdown(f"**Database:** Neo4j KG")
    st.markdown(f"**LLM:** Llama 3.2-1B")

# Main content
st.markdown('<h1 class="main-header">🏪 Store Supply Chain Assistant</h1>', unsafe_allow_html=True)

st.markdown("""
Welcome to the **Store Supply Chain Assistant**! Ask questions about products, inventory, 
shipments, expiry dates, and more. Our AI agents will work together to provide you with accurate information.
""")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display data if available
        if "data" in message and message["data"]:
            with st.expander("📊 View Detailed Data"):
                if isinstance(message["data"], list) and len(message["data"]) > 0:
                    df = pd.DataFrame(message["data"])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.json(message["data"])

# Chat input
if prompt := st.chat_input("Ask about products, inventory, shipments, or expiry..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process query
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            response = process_query(prompt)
        
        # Format response based on status
        if response['status'] == 'success':
            # Check if single or multi-agent
            if 'unified_summary' in response:
                # Multi-agent response
                st.markdown(f"**🤝 Collaborative Response from {response['agent_count']} agents:**")
                st.markdown(response['unified_summary'])
                
                # Show which agents responded
                st.markdown("**Agents used:**")
                for agent in response['agents_used']:
                    st.markdown(f"- {agent}")
                
                # Show individual summaries
                with st.expander("📋 View Individual Agent Responses"):
                    for summary in response['individual_summaries']:
                        st.markdown(summary)
                        st.markdown("---")
                
                # Show data
                if response['total_records'] > 0:
                    with st.expander(f"📊 View All Data ({response['total_records']} records)"):
                        for item in response['combined_data']:
                            st.markdown(f"**{item['agent']}** ({item['record_count']} records)")
                            if isinstance(item['data'], list) and len(item['data']) > 0:
                                df = pd.DataFrame(item['data'])
                                st.dataframe(df, use_container_width=True)
                            st.markdown("---")
                
                # Store in messages
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response['unified_summary'],
                    "data": response['combined_data']
                })
            
            else:
                # Single agent response
                st.markdown(f"**🤖 Response from {response['agent']}:**")
                st.markdown(response['summary'])
                
                # Show data
                if response['record_count'] > 0:
                    with st.expander(f"📊 View Data ({response['record_count']} records)"):
                        if isinstance(response['data'], list):
                            df = pd.DataFrame(response['data'])
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.json(response['data'])
                
                # Store in messages
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response['summary'],
                    "data": response['data']
                })
        
        elif response['status'] == 'error':
            st.error(f"**Error:** {response.get('message', 'Unknown error')}")
            
            if 'errors' in response:
                with st.expander("View Error Details"):
                    for error in response['errors']:
                        st.markdown(f"- {error}")
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ {response.get('message', 'An error occurred')}"
            })
        
        elif response['status'] == 'no_agent':
            st.warning(response['message'])
            
            st.markdown("**Suggestions:**")
            for suggestion in response.get('suggestions', []):
                st.markdown(f"- {suggestion}")
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": response['message']
            })

# Handle sample query clicks
if 'current_query' in st.session_state:
    query = st.session_state.current_query
    del st.session_state.current_query
    
    # Add to messages
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Process
    response = process_query(query)
    
    if response['status'] == 'success':
        content = response.get('unified_summary', response.get('summary', 'Response received'))
        data = response.get('combined_data', response.get('data', []))
    else:
        content = response.get('message', 'Error processing query')
        data = []
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": content,
        "data": data
    })
    
    st.rerun()