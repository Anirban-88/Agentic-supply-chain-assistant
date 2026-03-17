# Quick Start Guide - Distributed Architecture

## 🚀 Starting the System

### Step 1: Start MCP Servers
```bash
# Open a terminal
cd /Users/anirbanchatterjee/Documents/store_supply_chain
python scripts/10_start_mcp_servers.py --subprocess
```

This will start:
- Product Agent (port 8001)
- Supply Chain Agent (port 8002)  
- Expiry Agent (port 8003)
- Graph Agent (port 8004)
- Orchestrator (port 8000)

Wait until you see "All servers started" message.

### Step 2: Verify Servers Are Running
```bash
# In a new terminal
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

All should return `{"status": "healthy"}`.

### Step 3: Test Distributed Communication
```bash
python scripts/12_test_distributed_orchestrator.py
```

This will:
- ✅ Check all servers are healthy
- ✅ Verify orchestrator can discover agent capabilities
- ✅ Test queries to each agent type
- ✅ Confirm HTTP communication between services

### Step 4: Start Streamlit UI (Optional)
```bash
# In a new terminal
streamlit run ui/streamlit_app.py
```

Open http://localhost:8501 and try queries like:
- "What is the price of product P0001?"
- "Check shipment status for order 1"
- "Show me expiring products"

## 🔍 Monitoring

### Watch Distributed Communication
```bash
# In a new terminal
tail -f logs/mcp_servers.log
```

You'll see HTTP requests between orchestrator and agents:
```
Calling agent 'product' at http://localhost:8001/query
Agent 'product' responded in 0.15s
```

### Check Agent Processing
```bash
tail -f logs/agents.log
```

### Check Errors
```bash
tail -f logs/errors.log
```

## 🧪 Testing Individual Agents

### Test Product Agent Directly
```bash
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the price of P0001?"}'
```

### Test Supply Chain Agent
```bash
curl -X POST http://localhost:8002/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Check shipment status for order 1"}'
```

### Test Expiry Agent
```bash
curl -X POST http://localhost:8003/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me expiring products"}'
```

### Test Graph Agent
```bash
curl -X POST http://localhost:8004/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What products are supplied by S0001?"}'
```

### Test Orchestrator (Routes to Appropriate Agent)
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about product P0001"}'
```

## 🛑 Stopping the System

Press `Ctrl+C` in the terminal running the servers.

Or kill processes manually:
```bash
pkill -f mcp_servers
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Agent Not Responding
```bash
# Check if running
lsof -i :8001

# Restart individual agent
python -m mcp_servers.product_server --port 8001
```

### Connection Refused
1. Ensure agent servers started before orchestrator
2. Wait 3-5 seconds after starting agents
3. Check firewall settings

### Wrong Agent Selected
1. Check query contains agent-specific keywords
2. Review logs: `tail -f logs/agents.log`
3. See agent capabilities: `curl http://localhost:8000/capabilities`

## 📊 Architecture Verification

Check that you're using distributed architecture:
```bash
curl http://localhost:8000/capabilities | jq
```

You should see agent URLs like:
```json
{
  "agents": {
    "product": {
      "url": "http://localhost:8001",
      ...
    }
  }
}
```

## 💡 Example Queries

### Product Information
- "What is the price of product P0001?"
- "Tell me about product P0005"
- "Show stock levels for P0001"

### Supply Chain
- "Check shipment status for order 1"
- "Where is shipment SH001?"
- "List all orders"

### Expiry Tracking
- "Show me expiring products"
- "Which products expire soon?"
- "Check expiry dates"

### Graph Relationships
- "What products are supplied by S0001?"
- "Show me complete information about P0001"
- "Which suppliers provide laptop products?"

## 📈 Next Steps

1. Review [DISTRIBUTED_ARCHITECTURE.md](DISTRIBUTED_ARCHITECTURE.md) for detailed architecture
2. Check logs to see distributed communication
3. Try scaling agents (run multiple instances on different ports)
4. Implement load balancing
5. Add monitoring with Prometheus/Grafana

## 🔗 Useful Links

- Orchestrator: http://localhost:8000/health
- Product Agent: http://localhost:8001/health
- Supply Chain Agent: http://localhost:8002/health
- Expiry Agent: http://localhost:8003/health
- Graph Agent: http://localhost:8004/health
- Streamlit UI: http://localhost:8501
