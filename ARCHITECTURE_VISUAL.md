# System Architecture - Visual Guide

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Client Layer                              │
│  ┌─────────────────────┐              ┌─────────────────────┐      │
│  │   Streamlit UI      │              │   External API      │       │
│  │   (Port 8501)       │              │   Clients           │       │
│  └──────────┬──────────┘              └──────────┬──────────┘      │
└─────────────┼─────────────────────────────────────┼─────────────────┘
              │                                     │
              │ HTTP POST /query                    │
              └─────────────────┬───────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Orchestration Layer                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │             Orchestrator MCP Server (Port 8000)             │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │  DistributedOrchestrator                            │   │   │
│  │  │  - Load agent capabilities                          │   │   │
│  │  │  - Select agent(s) by keywords                      │   │   │
│  │  │  - Route queries via HTTP                           │   │   │
│  │  │  - Aggregate results                                │   │   │
│  │  │  - Handle errors & timeouts                         │   │   │
│  │  └─────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────┬───────────┬───────────┬───────────┬─────────────────────┘
          │           │           │           │
          │ HTTP      │ HTTP      │ HTTP      │ HTTP
          │           │           │           │
          ▼           ▼           ▼           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Agent Layer                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Product  │  │ Supply   │  │ Expiry   │  │  Graph   │          │
│  │  Agent   │  │  Chain   │  │  Agent   │  │  Agent   │          │
│  │  Server  │  │  Agent   │  │  Server  │  │  Server  │          │
│  │ (8001)   │  │  Server  │  │ (8003)   │  │ (8004)   │          │
│  │          │  │ (8002)   │  │          │  │          │          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
└───────┼─────────────┼─────────────┼─────────────┼──────────────────┘
        │             │             │             │
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Data Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────┐  ┌──────────┐   │
│  │  PostgreSQL  │  │   MongoDB    │  │  Redis  │  │  Neo4j   │   │
│  │              │  │              │  │ (Cache) │  │ (Graph)  │   │
│  │ - Products   │  │ - Shipments  │  └─────────┘  └──────────┘   │
│  │ - Inventory  │  │ - Warehouses │                               │
│  │ - Expiry     │  │              │                               │
│  └──────────────┘  └──────────────┘                               │
└─────────────────────────────────────────────────────────────────────┘
```

## Request Flow

### Example: "What is the price of product P0001?"

```
1. Streamlit UI
   │
   └─> POST http://localhost:8000/query
       {"query": "What is the price of product P0001?"}
       
2. Orchestrator Server (Port 8000)
   │
   ├─> Extract keywords: ["price", "product"]
   ├─> Select agent: "product" (score: 1.0)
   │
   └─> POST http://localhost:8001/query
       {"query": "What is the price of product P0001?"}
       
3. Product Agent Server (Port 8001)
   │
   ├─> Extract entity: "P0001"
   ├─> Query PostgreSQL:
   │   SELECT * FROM products WHERE product_id = 'P0001'
   │
   └─> Response: {
         "query": "...",
         "response": "Product P0001 costs $29.99",
         "metadata": {...}
       }
       
4. Orchestrator Server
   │
   └─> Aggregate results
       Add metadata (agent_server_url, execution_time)
       
5. Streamlit UI
   │
   └─> Display: "Product P0001 costs $29.99"
```

## Agent Routing Logic

```
Query Keywords → Agent Selection
─────────────────────────────────
price, stock     → Product Agent (8001)
product, sku     → Product Agent (8001)
inventory        → Product Agent (8001)

order, shipment  → Supply Chain Agent (8002)
delivery         → Supply Chain Agent (8002)
tracking         → Supply Chain Agent (8002)
warehouse        → Supply Chain Agent (8002)

expiry, expire   → Expiry Agent (8003)
expiration       → Expiry Agent (8003)
shelf life       → Expiry Agent (8003)

supplier         → Graph Agent (8004)
relationship     → Graph Agent (8004)
location         → Graph Agent (8004)
complete info    → Graph Agent (8004)
```

## Component Responsibilities

### Orchestrator (Port 8000)
```
┌────────────────────────────────────┐
│  DistributedOrchestrator           │
├────────────────────────────────────┤
│                                    │
│  _load_agent_capabilities()        │
│    • GET /capabilities from each   │
│      agent server                  │
│    • Store in memory               │
│                                    │
│  _select_agents(query)             │
│    • Extract keywords from query   │
│    • Match against agent keywords  │
│    • Calculate confidence scores   │
│    • Return best match(es)         │
│                                    │
│  _call_agent_server(agent, query)  │
│    • POST /query to agent server   │
│    • Timeout: 30 seconds           │
│    • Error handling                │
│                                    │
│  _aggregate_results(results)       │
│    • Combine responses             │
│    • Add metadata                  │
│    • Format output                 │
│                                    │
│  process_query(query)              │
│    • Main entry point              │
│    • Orchestrates entire flow      │
│                                    │
└────────────────────────────────────┘
```

### Product Agent (Port 8001)
```
┌────────────────────────────────────┐
│  ProductAgent                      │
├────────────────────────────────────┤
│                                    │
│  Capabilities:                     │
│    • product_information           │
│    • pricing_queries               │
│    • stock_levels                  │
│    • inventory_search              │
│                                    │
│  Keywords:                         │
│    product, price, stock,          │
│    inventory, sku, cost            │
│                                    │
│  Data Sources:                     │
│    • store_catalog DB              │
│    • inventory_mgmt DB             │
│                                    │
│  Query Types:                      │
│    • Get product by ID             │
│    • Search products by name       │
│    • Check stock levels            │
│    • Get pricing information       │
│                                    │
└────────────────────────────────────┘
```

### Supply Chain Agent (Port 8002)
```
┌────────────────────────────────────┐
│  SupplyChainAgent                  │
├────────────────────────────────────┤
│                                    │
│  Capabilities:                     │
│    • order_tracking                │
│    • shipment_status               │
│    • delivery_information          │
│    • warehouse_management          │
│                                    │
│  Keywords:                         │
│    order, shipment, delivery,      │
│    tracking, warehouse             │
│                                    │
│  Data Sources:                     │
│    • MongoDB (shipments)           │
│    • MongoDB (warehouses)          │
│                                    │
│  Query Types:                      │
│    • Track shipment                │
│    • Check order status            │
│    • Find warehouse location       │
│    • Get delivery estimates        │
│                                    │
└────────────────────────────────────┘
```

### Expiry Agent (Port 8003)
```
┌────────────────────────────────────┐
│  ExpiryAgent                       │
├────────────────────────────────────┤
│                                    │
│  Capabilities:                     │
│    • expiry_tracking               │
│    • expiration_alerts             │
│    • batch_monitoring              │
│                                    │
│  Keywords:                         │
│    expiry, expiration, expire,     │
│    shelf life, batch               │
│                                    │
│  Data Sources:                     │
│    • expiry_tracking DB            │
│                                    │
│  Query Types:                      │
│    • Find expiring products        │
│    • Check batch expiry dates      │
│    • Get expiry alerts             │
│    • Monitor shelf life            │
│                                    │
└────────────────────────────────────┘
```

### Graph Agent (Port 8004)
```
┌────────────────────────────────────┐
│  GraphAgent                        │
├────────────────────────────────────┤
│                                    │
│  Capabilities:                     │
│    • relationship_queries          │
│    • supplier_networks             │
│    • location_mapping              │
│    • complex_analytics             │
│                                    │
│  Keywords:                         │
│    relationship, supplier,         │
│    location, connected, network    │
│                                    │
│  Data Sources:                     │
│    • Neo4j Knowledge Graph         │
│                                    │
│  Query Types:                      │
│    • Find product suppliers        │
│    • Get complete product info     │
│    • Analyze supply networks       │
│    • Location relationships        │
│                                    │
└────────────────────────────────────┘
```

## HTTP Communication Protocol

### Request Format
```json
POST /query
Content-Type: application/json

{
  "query": "What is the price of product P0001?",
  "context": {  // Optional
    "user_id": "user123",
    "session_id": "session456"
  }
}
```

### Response Format
```json
{
  "query": "What is the price of product P0001?",
  "response": "Product P0001 costs $29.99",
  "metadata": {
    "agent": "product",
    "execution_time": 0.15,
    "data_sources": ["PostgreSQL"],
    "entity_extracted": "P0001"
  }
}
```

### Error Response
```json
{
  "error": "Agent not available",
  "message": "Connection to product agent failed",
  "retry_after": 5
}
```

## Logging Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Log Files                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  application.log         → General application logs         │
│  errors.log              → All errors                       │
│  agents.log              → Agent processing                 │
│  mcp_servers.log         → HTTP communication ⭐            │
│  llm_extraction.log      → Entity extraction                │
│  queries.log             → Database queries                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Log: mcp_servers.log
This shows the distributed HTTP communication:
```
2024-01-15 10:30:45 - mcp_servers.orchestrator - INFO - 
  Calling agent 'product' at http://localhost:8001/query
  
2024-01-15 10:30:45 - mcp_servers.product_server - INFO - 
  Received query: "What is the price of product P0001?"
  
2024-01-15 10:30:45 - mcp_servers.product_server - INFO - 
  Extracted entity: P0001
  
2024-01-15 10:30:45 - mcp_servers.product_server - INFO - 
  Query completed in 0.12s
  
2024-01-15 10:30:45 - mcp_servers.orchestrator - INFO - 
  Agent 'product' responded in 0.15s
```

## Scalability Patterns

### Horizontal Scaling
```
                  ┌─> Product Agent 1 (8001)
Orchestrator  ──> ├─> Product Agent 2 (8011)  
                  └─> Product Agent 3 (8021)
```

### Load Balancing
```
                      ┌─> Product Agent 1
Orchestrator ─> LB ──> ├─> Product Agent 2
                      └─> Product Agent 3
```

### Geographic Distribution
```
US East:     Product Agent    ─> PostgreSQL (US East)
EU West:     Supply Agent     ─> MongoDB (EU West)
Asia Pacific: Graph Agent     ─> Neo4j (Asia)
```

## Deployment Options

### Local Development
- All services on localhost
- Ports 8000-8004
- Single machine

### Docker Compose
- Each service in container
- Shared network
- Volume mounts for data

### Kubernetes
- Each agent as deployment
- Services for discovery
- Horizontal pod autoscaling
- Ingress for routing

### Cloud Native
- AWS ECS/EKS
- Google Cloud Run
- Azure Container Instances
- API Gateway for routing

## Monitoring Points

```
Orchestrator (8000)
├─> Request rate
├─> Response times (p50, p95, p99)
├─> Agent selection accuracy
├─> Error rate
└─> Active connections

Product Agent (8001)
├─> Request rate
├─> Database query times
├─> Cache hit rate
├─> Error rate
└─> Resource usage (CPU, memory)

Supply Chain Agent (8002)
├─> MongoDB query times
├─> Document fetch rate
├─> Cache effectiveness
└─> Connection pool usage

Expiry Agent (8003)
├─> Alert generation rate
├─> Query performance
└─> Batch processing times

Graph Agent (8004)
├─> Cypher query times
├─> Graph traversal depth
├─> Neo4j connection health
└─> Result set sizes
```

This distributed architecture provides the foundation for a highly scalable, resilient, and maintainable supply chain management system! 🚀
