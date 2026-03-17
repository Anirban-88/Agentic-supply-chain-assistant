# Oracle Cloud Deployment Architecture
 
## 🏗️ Infrastructure Architecture Diagram
 
```mermaid
graph TB
    subgraph "Oracle Cloud Infrastructure"
        subgraph "Region: Your Selected Region"
            subgraph "Compartment: supply-chain-dev"
                subgraph "VCN: supply-chain-vcn (10.0.0.0/16)"
                    subgraph "Public Subnet: 10.0.1.0/24"
                        VM["🖥️ Compute Instance<br/>VM.Standard.E2.1.Micro<br/>1 OCPU, 1GB RAM<br/>Oracle Linux 8<br/>Public IP: xxx.xxx.xxx.xxx"]
                    end
                    IGW["🌐 Internet Gateway<br/>supply-chain-igw"]
                    RT["📋 Route Table<br/>0.0.0.0/0 → IGW"]
                    SL["🔒 Security List<br/>Ports: 22, 8501, 7474, 7687"]
                end
            end
        end
    end
    
    subgraph "VM Internal Architecture"
        subgraph "Docker Environment"
            subgraph "Application Stack"
                APP["🐍 Python Application<br/>Streamlit UI<br/>Multi-Agent System<br/>Port: 8501"]
            end
            
            subgraph "Database Layer"
                PG["🐘 PostgreSQL<br/>Structured Data<br/>Port: 5432"]
                MONGO["🍃 MongoDB<br/>Real-time Data<br/>Port: 27017"]
                REDIS["⚡ Redis<br/>Caching & Expiry<br/>Port: 6379"]
                NEO4J["🕸️ Neo4j<br/>Knowledge Graph<br/>Ports: 7474, 7687"]
            end
        end
        
        subgraph "System Services"
            DOCKER["🐳 Docker Engine"]
            COMPOSE["📦 Docker Compose"]
            FIREWALL["🔥 Firewall"]
            LOGS["📝 Logging System"]
        end
    end
    
    subgraph "External Access"
        USER["👤 Users<br/>Web Browser"]
        ADMIN["👨‍💻 Administrator<br/>SSH Access"]
    end
    
    subgraph "Backup & Monitoring"
        BACKUP["💾 Backup Storage<br/>Daily Automated Backups"]
        MONITOR["📊 Monitoring Scripts<br/>Health Checks"]
    end
    
    %% Connections
    USER --> IGW
    ADMIN --> IGW
    IGW --> VM
    VM --> APP
    APP --> PG
    APP --> MONGO
    APP --> REDIS
    APP --> NEO4J
    VM --> BACKUP
    VM --> MONITOR
    
    %% Styling
    classDef oci fill:#f96,stroke:#333,stroke-width:2px,color:#fff
    classDef compute fill:#4a90e2,stroke:#333,stroke-width:2px,color:#fff
    classDef database fill:#7ed321,stroke:#333,stroke-width:2px,color:#fff
    classDef application fill:#f5a623,stroke:#333,stroke-width:2px,color:#fff
    classDef network fill:#9013fe,stroke:#333,stroke-width:2px,color:#fff
    classDef external fill:#50e3c2,stroke:#333,stroke-width:2px,color:#fff
    
    class VM compute
    class PG,MONGO,REDIS,NEO4J database
    class APP application
    class IGW,RT,SL network
    class USER,ADMIN external
```
 
## 🔄 Data Flow Architecture
 
```mermaid
sequenceDiagram
    participant U as User Browser
    participant S as Streamlit App
    participant O as Orchestrator
    participant A as AI Agents
    participant N as Neo4j
    participant P as PostgreSQL
    participant M as MongoDB
    participant R as Redis
    
    U->>S: HTTP Request (Port 8501)
    S->>O: Process Query
    O->>A: Route to Appropriate Agent
    
    par Database Queries
        A->>N: Graph Queries (Port 7687)
        A->>P: Structured Data (Port 5432)
        A->>M: Real-time Data (Port 27017)
        A->>R: Cache Lookup (Port 6379)
    end
    
    N-->>A: Graph Results
    P-->>A: Structured Results
    M-->>A: Real-time Results
    R-->>A: Cached Results
    
    A->>O: Aggregated Response
    O->>S: Formatted Response
    S->>U: HTML Response
```
 
## 🛡️ Security Architecture
 
```mermaid
graph LR
    subgraph "Internet"
        I[Internet Traffic]
    end
    
    subgraph "OCI Security"
        SL[Security List<br/>Port Filtering]
        NSG[Network Security Groups<br/>Advanced Rules]
    end
    
    subgraph "VM Security"
        FW[OS Firewall<br/>firewalld]
        SSH[SSH Key Auth<br/>No Password]
    end
    
    subgraph "Application Security"
        ENV[Environment Variables<br/>Secrets Management]
        DB[Database Authentication<br/>Strong Passwords]
        NET[Internal Network<br/>Docker Bridge]
    end
    
    I --> SL
    SL --> NSG
    NSG --> FW
    FW --> SSH
    SSH --> ENV
    ENV --> DB
    DB --> NET
```
 
## 📊 Resource Allocation
 
| Component | CPU | Memory | Storage | Network |
|-----------|-----|--------|---------|---------|
| **VM Instance** | 1 OCPU | 1 GB | 50 GB | 1 Gbps |
| **Streamlit App** | ~20% | ~200 MB | ~1 GB | Primary |
| **PostgreSQL** | ~15% | ~150 MB | ~5 GB | Internal |
| **MongoDB** | ~15% | ~150 MB | ~5 GB | Internal |
| **Redis** | ~10% | ~100 MB | ~1 GB | Internal |
| **Neo4j** | ~25% | ~300 MB | ~10 GB | Internal |
| **System Overhead** | ~15% | ~100 MB | ~28 GB | - |
 
## 🔌 Port Configuration
 
| Service | Internal Port | External Port | Protocol | Access |
|---------|---------------|---------------|----------|---------|
| SSH | 22 | 22 | TCP | Public |
| Streamlit | 8501 | 8501 | TCP | Public |
| Neo4j HTTP | 7474 | 7474 | TCP | Public |
| Neo4j Bolt | 7687 | 7687 | TCP | Public |
| PostgreSQL | 5432 | - | TCP | Internal |
| MongoDB | 27017 | - | TCP | Internal |
| Redis | 6379 | - | TCP | Internal |
 
## 🔄 Deployment Workflow
 
```mermaid
flowchart TD
    A[Start Deployment] --> B[Setup OCI Account]
    B --> C[Create VCN & Subnet]
    C --> D[Configure Security]
    D --> E[Provision VM Instance]
    E --> F[Install Docker]
    F --> G[Transfer Application]
    G --> H[Configure Environment]
    H --> I[Deploy with Docker Compose]
    I --> J[Initialize Databases]
    J --> K[Configure Monitoring]
    K --> L[Setup Backups]
    L --> M[Test Application]
    M --> N{All Tests Pass?}
    N -->|Yes| O[Deployment Complete]
    N -->|No| P[Debug Issues]
    P --> I
    
    style A fill:#e1f5ff
    style O fill:#e8f5e8
    style P fill:#ffe1e1
```
 
## 🎯 Success Criteria
 
### Infrastructure Ready ✅
- [ ] VCN and subnet created with proper CIDR blocks
- [ ] Security lists configured with required ports
- [ ] VM instance running with public IP assigned
- [ ] SSH access working with key-based authentication
 
### Application Deployed ✅
- [ ] All Docker containers running successfully
- [ ] Databases initialized with sample data
- [ ] Streamlit UI accessible via public IP
- [ ] All AI agents responding to queries
 
### Production Ready ✅
- [ ] Monitoring scripts configured and running
- [ ] Backup strategy implemented and tested
- [ ] Firewall rules properly configured
- [ ] SSL certificate installed (if domain available)
 
This architecture provides a clear visual representation of your Oracle Cloud deployment structure and the relationships between all components.
 
 