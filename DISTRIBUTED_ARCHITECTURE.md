# Distributed MCP Architecture

## Overview

This system implements a fully distributed microservices architecture using the Model Context Protocol (MCP). Each agent runs as an independent HTTP server, and the orchestrator routes queries to appropriate agents via HTTP requests.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit UI                              │
│                     (Port 8501)                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP POST /query
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Orchestrator MCP Server                         │
│                     (Port 8000)                                  │
│  - Routes queries to appropriate agents                          │
│  - Aggregates results from multiple agents                       │
│  - Handles parallel execution                                    │
└──┬─────────┬─────────────┬─────────────┬────────────────────────┘
   │         │             │             │
   │ HTTP    │ HTTP        │ HTTP        │ HTTP
   │         │             │             │
   ▼         ▼             ▼             ▼
┌────────┐ ┌──────────┐ ┌────────┐ ┌──────────┐
│Product │ │Supply    │ │Expiry  │ │Graph     │
│Agent   │ │Chain     │ │Agent   │ │Agent     │
│8001    │ │Agent 8002│ │8003    │ │8004      │
└────────┘ └──────────┘ └────────┘ └──────────┘
    │          │             │          │
    ▼          ▼             ▼          ▼
┌─────────────────────────────────────────────┐
│         Data Sources                         │
│  PostgreSQL │ MongoDB │ Redis │ Neo4j       │
└─────────────────────────────────────────────┘
```

## Components

### 1. Orchestrator MCP Server (Port 8000)
- **File**: `mcp_servers/orchestrator_server.py`
- **Implementation**: `agents/distributed_orchestrator.py`
- **Responsibilities**:
  - Receives queries from UI or external clients
  - Loads agent capabilities from each agent server at startup
  - Selects appropriate agent(s) based on query keywords
  - Makes HTTP POST requests to agent servers
  - Aggregates responses from multiple agents
  - Returns unified response to client

### 2. Product Agent MCP Server (Port 8001)
- **File**: `mcp_servers/product_server.py`
- **Capabilities**: Product information, pricing, stock levels
- **Data Source**: PostgreSQL (store_catalog, inventory_mgmt)
- **Keywords**: product, price, stock, inventory, sku

### 3. Supply Chain Agent MCP Server (Port 8002)
- **File**: `mcp_servers/supply_chain_server.py`
- **Capabilities**: Orders, shipments, deliveries, logistics
- **Data Source**: MongoDB (supply_chain_logistics)
- **Keywords**: order, shipment, delivery, tracking, warehouse

### 4. Expiry Agent MCP Server (Port 8003)
- **File**: `mcp_servers/expiry_server.py`
- **Capabilities**: Product expiration tracking and alerts
- **Data Source**: PostgreSQL (expiry_tracking)
- **Keywords**: expiry, expiration, expire, shelf life

### 5. Graph Agent MCP Server (Port 8004)
- **File**: `mcp_servers/graph_server.py`
- **Capabilities**: Complex relationships and analytics
- **Data Source**: Neo4j (knowledge graph)
- **Keywords**: relationship, supplier, location, analytics, connected

## Configuration

All configuration is in `config/mcp_config.py`:

```python
MCP_SERVERS = {
    'product': {'port': 8001, 'enabled': True},
    'supply_chain': {'port': 8002, 'enabled': True},
    'expiry': {'port': 8003, 'enabled': True},
    'graph': {'port': 8004, 'enabled': True}
}

ORCHESTRATOR_CONFIG = {'port': 8000}
```

### Environment Variables

- `USE_DISTRIBUTED_ORCHESTRATOR=true`: Enable distributed mode (default)
- `USE_DISTRIBUTED_ORCHESTRATOR=false`: Use in-process agents (legacy mode)

## API Endpoints

Each server exposes three endpoints:

### 1. Health Check
```bash
GET http://localhost:8000/health
```
Response:
```json
{
  "status": "healthy",
  "server": "orchestrator",
  "port": 8000
}
```

### 2. Capabilities
```bash
GET http://localhost:8000/capabilities
```
Response:
```json
{
  "server": "orchestrator",
  "agents": {
    "product": {
      "url": "http://localhost:8001",
      "capabilities": ["product_info", "pricing", "stock_levels"],
      "keywords": ["product", "price", "stock"]
    }
  }
}
```

### 3. Query
```bash
POST http://localhost:8000/query
Content-Type: application/json

{
  "query": "What is the price of product P0001?"
}
```
Response:
```json
{
  "query": "What is the price of product P0001?",
  "selected_agent": "product",
  "response": "Product P0001 costs $29.99",
  "metadata": {
    "agent_server_url": "http://localhost:8001",
    "execution_time": 0.45
  }
}
```

## Starting the System

### Option 1: Automated Startup Script
```bash
python scripts/10_start_mcp_servers.py --subprocess
```

This starts all servers in the correct order:
1. Agent servers (8001-8004) in parallel
2. Wait 3 seconds for initialization
3. Orchestrator server (8000)

### Option 2: Manual Startup
```bash
# Terminal 1 - Product Agent
python -m mcp_servers.product_server --port 8001

# Terminal 2 - Supply Chain Agent
python -m mcp_servers.supply_chain_server --port 8002

# Terminal 3 - Expiry Agent
python -m mcp_servers.expiry_server --port 8003

# Terminal 4 - Graph Agent
python -m mcp_servers.graph_server --port 8004

# Terminal 5 - Orchestrator (start after agents are ready)
python -m mcp_servers.orchestrator_server --port 8000

# Terminal 6 - Streamlit UI
streamlit run ui/streamlit_app.py
```

## Testing

### Quick Test
```bash
# Test orchestrator health
curl http://localhost:8000/health

# Test query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the price of P0001?"}'
```

### Comprehensive Test Suite
```bash
python scripts/12_test_distributed_orchestrator.py
```

This tests:
- Health checks for all servers
- Capability discovery
- Query routing to correct agents
- Response aggregation
- End-to-end functionality

## Logging

All logs are written to `logs/` directory:

- `mcp_servers.log`: HTTP requests/responses between services
- `agents.log`: Agent processing and decision making
- `llm_extraction.log`: Entity extraction from queries
- `queries.log`: Database queries
- `errors.log`: All errors
- `application.log`: General application logs

### Monitoring Distributed Communication

Check `logs/mcp_servers.log` to see HTTP communication:
```log
2024-01-15 10:30:45,123 - mcp_servers.orchestrator - INFO - Calling agent 'product' at http://localhost:8001/query
2024-01-15 10:30:45,234 - mcp_servers.orchestrator - INFO - Agent 'product' responded in 0.11s
```

## Benefits of Distributed Architecture

### 1. Independent Scaling
Each agent can be scaled independently based on load:
```bash
# Run multiple instances of product agent
python -m mcp_servers.product_server --port 8001
python -m mcp_servers.product_server --port 8011
python -m mcp_servers.product_server --port 8021
```

### 2. Technology Flexibility
Each agent can use different:
- Programming languages (Python, Node.js, Go)
- Frameworks and libraries
- Database connections
- Caching strategies

### 3. Fault Isolation
If one agent fails, others continue working:
- Orchestrator handles connection errors gracefully
- Partial results can be returned
- Failed agents can be restarted independently

### 4. Development Flexibility
Teams can work on agents independently:
- No shared codebase conflicts
- Deploy agents separately
- Roll back individual agents if issues arise

### 5. Load Balancing
Add load balancer in front of agent servers:
```
Orchestrator → Load Balancer → [Product Agent 1, Product Agent 2, Product Agent 3]
```

### 6. Geographic Distribution
Agents can run in different locations:
- Product Agent: US data center (close to PostgreSQL)
- Supply Chain Agent: EU data center (close to MongoDB)
- Graph Agent: Asia data center (close to Neo4j)

## Deployment Considerations

### Docker Compose
```yaml
version: '3.8'
services:
  orchestrator:
    build: .
    command: python -m mcp_servers.orchestrator_server
    ports:
      - "8000:8000"
    environment:
      - USE_DISTRIBUTED_ORCHESTRATOR=true
  
  product-agent:
    build: .
    command: python -m mcp_servers.product_server
    ports:
      - "8001:8001"
    replicas: 3  # Scale to 3 instances
  
  # ... other agents
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: product-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: product-agent
  template:
    spec:
      containers:
      - name: product-agent
        image: supply-chain:latest
        command: ["python", "-m", "mcp_servers.product_server"]
        ports:
        - containerPort: 8001
```

### Service Mesh (Istio/Linkerd)
Add service mesh for:
- Automatic retry and circuit breaking
- Distributed tracing
- Metrics collection
- mTLS between services

## Troubleshooting

### Agent Not Responding
```bash
# Check agent health
curl http://localhost:8001/health

# Check logs
tail -f logs/mcp_servers.log | grep product

# Restart agent
pkill -f product_server
python -m mcp_servers.product_server --port 8001
```

### Connection Refused
1. Ensure agent servers started before orchestrator
2. Check firewall rules
3. Verify port availability: `lsof -i :8001`

### Wrong Agent Selected
1. Check query keywords in agent capabilities
2. Review `logs/agents.log` for selection logic
3. Adjust keywords in agent implementations

### Slow Response Times
1. Check network latency between services
2. Review database query performance in `logs/queries.log`
3. Consider adding caching (Redis)
4. Enable parallel agent execution for multi-agent queries

## Performance Optimization

### 1. Connection Pooling
Use `requests.Session()` for HTTP connection reuse:
```python
session = requests.Session()
response = session.post(url, json=payload)
```

### 2. Async/Await
Convert to async HTTP calls for better concurrency:
```python
import aiohttp
async with aiohttp.ClientSession() as session:
    async with session.post(url, json=payload) as response:
        return await response.json()
```

### 3. Caching
Add Redis cache for frequently accessed data:
```python
# Check cache first
cached = redis_client.get(f"query:{query_hash}")
if cached:
    return json.loads(cached)
```

### 4. Circuit Breaker
Prevent cascading failures:
```python
from pybreaker import CircuitBreaker

breaker = CircuitBreaker(fail_max=5, timeout_duration=60)

@breaker
def call_agent(url, payload):
    return requests.post(url, json=payload, timeout=5)
```

## Monitoring & Observability

### Metrics to Track
- Request count per agent
- Response times (p50, p95, p99)
- Error rates
- Agent availability
- Query routing accuracy

### Tools
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Jaeger**: Distributed tracing
- **ELK Stack**: Log aggregation

## Future Enhancements

1. **API Gateway**: Add authentication, rate limiting
2. **Message Queue**: Use RabbitMQ/Kafka for async processing
3. **Event Sourcing**: Track all state changes
4. **GraphQL**: Unified query interface
5. **WebSockets**: Real-time updates
6. **gRPC**: Faster inter-service communication

## References

- MCP Specification: https://modelcontextprotocol.io/
- Microservices Patterns: https://microservices.io/
- Distributed Systems: https://www.allthingsdistributed.com/
