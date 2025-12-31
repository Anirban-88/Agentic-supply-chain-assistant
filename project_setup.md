# 📋 Project Setup Guide

**Complete command-line instructions to set up and run the Store Supply Chain Multi-Agent System**

---

## 📑 Table of Contents

1. [Prerequisites Check](#prerequisites-check)
2. [Step 1: Environment Setup](#step-1-environment-setup)
3. [Step 2: Knowledge Graph Setup](#step-2-knowledge-graph-setup)
4. [Step 3: Application Run](#step-3-application-run)
5. [Verification & Testing](#verification--testing)
6. [Troubleshooting](#troubleshooting)
7. [Quick Start (TL;DR)](#quick-start-tldr)

---

## ✅ Prerequisites Check

### Before you begin, verify you have:

```bash
# Check Python version (requires 3.9-3.11)
python --version
# Expected: Python 3.9.x or 3.10.x or 3.11.x

# Check pip
pip --version

# Check Docker
docker --version
docker-compose --version

# Check Git
git --version
```

**If any command fails, install the missing software first:**

- **Python 3.9-3.11:** https://www.python.org/downloads/
- **Docker Desktop:** https://www.docker.com/products/docker-desktop/
- **Git:** https://git-scm.com/downloads

---

## 🚀 Step 1: Environment Setup

### 1.1 Clone the Repository

```bash
# Clone the project
git clone https://github.com/yourusername/store-supply-chain.git

# Navigate to project directory
cd store-supply-chain

# Verify you're in the right directory
pwd
# Should show: /path/to/store-supply-chain
```

### 1.2 Create Python Virtual Environment

#### **On Windows (PowerShell or CMD):**

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation (prompt should show (venv))
# Your prompt should now look like: (venv) C:\path\to\store-supply-chain>
```

#### **On macOS/Linux (Terminal):**

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation
# Your prompt should now show: (venv) in front
```

### 1.3 Upgrade pip

```bash
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Verify pip upgrade
pip --version
# Should show version 23.x or higher
```

### 1.4 Install Python Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# This will take 10-20 minutes and install:
# - PyTorch (~2 GB)
# - Transformers + dependencies (~1 GB)
# - Llama model will be downloaded on first run (~5 GB)
# - Neo4j driver
# - Streamlit
# - Other dependencies

# You should see output like:
# Collecting pandas==2.1.4
# Downloading pandas-2.1.4-cp39-cp39-win_amd64.whl (11.5 MB)
# ...
# Successfully installed pandas-2.1.4 transformers-4.36.2 ...
```

**Expected installation time:**
- Fast internet: 10-15 minutes
- Moderate internet: 15-25 minutes
- Slow internet: 25-40 minutes

### 1.5 Verify Installation

```bash
# Test imports
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import transformers; print('Transformers:', transformers.__version__)"
python -c "import neo4j; print('Neo4j driver: OK')"
python -c "import streamlit; print('Streamlit:', streamlit.__version__)"

# All commands should succeed without errors
```

---

## 🕸️ Step 2: Knowledge Graph Setup

### 2.1 Start Neo4j Database

```bash
# Start Neo4j container (Docker must be running!)
docker-compose up -d

# Expected output:
# Creating network "store_supply_chain_default" with the default driver
# Creating volume "store_supply_chain_neo4j_data" with default driver
# Creating store_supply_chain_neo4j ... done

# Verify Neo4j is running
docker-compose ps

# Expected output:
# Name                          Command              State           Ports
# --------------------------------------------------------------------------------
# store_supply_chain_neo4j   /sbin/tini -g -- /dock...   Up      7473/tcp, 
#                                                                0.0.0.0:7474->7474/tcp,
#                                                                0.0.0.0:7687->7687/tcp
```

### 2.2 Wait for Neo4j to Start

```bash
# View Neo4j logs (wait for "Started." message)
docker-compose logs -f neo4j

# Expected output (last lines):
# neo4j_1  | 2024-12-24 10:30:15.123+0000 INFO  Started.
# neo4j_1  | 2024-12-24 10:30:15.456+0000 INFO  Remote interface available at http://localhost:7474/

# Press Ctrl+C to exit logs
```

**Wait time:** 30-60 seconds for first-time startup

### 2.3 Verify Neo4j is Accessible

**Option A: Using Browser**

```bash
# Open Neo4j Browser
# On Windows:
start http://localhost:7474

# On macOS:
open http://localhost:7474

# On Linux:
xdg-open http://localhost:7474

# Or manually open: http://localhost:7474 in your browser
```

**Login credentials:**
- **Username:** `neo4j`
- **Password:** `storechain123`

**Option B: Using Command Line**

```bash
# Test connection using cypher-shell
docker exec -it store_supply_chain_neo4j cypher-shell -u neo4j -p storechain123

# You should see:
# Connected to Neo4j at neo4j://localhost:7687
# Type :help for a list of available commands
# neo4j@neo4j>

# Test query
RETURN "Neo4j is working!" AS message;

# Expected output:
# +---------------------+
# | message             |
# +---------------------+
# | "Neo4j is working!" |
# +---------------------+

# Exit
:exit
```

### 2.4 Generate Synthetic Data

```bash
# Generate store data (products, suppliers, inventory, etc.)
python scripts/01_generate_data.py

# Expected output:
# 🔄 Generating synthetic data...
#   📦 Generating products...
#   🏭 Generating suppliers...
#   📍 Generating locations...
#   🔗 Generating product-location mappings...
#   🔗 Generating product-supplier mappings...
#   📊 Generating inventory...
#   🏷️  Generating batches...
#   📋 Generating orders...
#   📋 Generating order items...
#   🚚 Generating shipments...
#   🏢 Generating warehouse inventory...
# ✅ Data generation complete!
#
# 📊 Data Summary:
#   Products: 100
#   Suppliers: 15
#   Locations: 30
#   Inventory Records: 100
#   Batches: 200
#   Orders: 40
#   Shipments: 50
#   Warehouses: 5
#
# 💾 Saved synthetic_data/products.csv
# 💾 Saved synthetic_data/suppliers.csv
# ... (multiple files)
```

**Time:** 1-2 minutes

### 2.5 Setup Source Databases (PostgreSQL & MongoDB)

```bash
# Setup PostgreSQL databases
python scripts/02_setup_postgresql.py

# Expected output:
# 🔄 Creating PostgreSQL databases...
# ✅ Created database: store_catalog
# ✅ Created database: inventory_mgmt
# ✅ Created database: expiry_tracking
# 🔄 Executing schema on store_catalog...
# ✅ Schema executed on store_catalog
# ... (similar for other databases)
# 🔄 Loading data into databases...
# ✅ Loaded 100 rows into store_catalog.products
# ... (loading continues)
# ✅ PostgreSQL setup complete!

# Setup MongoDB database
python scripts/03_setup_mongodb.py

# Expected output:
# 🚀 Starting MongoDB setup...
# ✅ Connected to MongoDB
# 🚚 Loading shipments...
# ✅ Loaded 50 shipments
# 🏢 Loading warehouses...
# ✅ Loaded 5 warehouses
# 🔍 Creating indexes...
# ✅ Indexes created
# ✅ MongoDB setup complete!
```

**Time:** 2-3 minutes

### 2.6 Verify Data Setup

```bash
# Verify all databases have data
python scripts/04_verify_setup.py

# Expected output:
# ============================================================
# 🔍 VERIFYING DATABASE SETUP
# ============================================================
#
# 📊 Verifying PostgreSQL databases...
#
# 🗄️  Database: store_catalog
#   ✅ products: 100 rows
#   ✅ suppliers: 15 rows
#   ✅ locations: 30 rows
#   ✅ product_locations: 150 rows
#   ✅ product_suppliers: 120 rows
#
# 🗄️  Database: inventory_mgmt
#   ✅ inventory: 100 rows
#   ✅ orders: 40 rows
#   ✅ order_items: 180 rows
#
# 🗄️  Database: expiry_tracking
#   ✅ batches: 200 rows
#
# 📊 Verifying MongoDB...
#   ✅ shipments: 50 documents
#   ✅ warehouses: 5 documents
#
# 📦 Sample Shipment:
#   Shipment ID: SH20241224001
#   Status: in_transit
#   Current Location: Pune
#
# ============================================================
# ✅ VERIFICATION COMPLETE!
# ============================================================
```

### 2.7 Create Knowledge Graph in Neo4j

**This is the main step that loads all data into Neo4j!**

```bash
# Load all data into Neo4j Knowledge Graph
python scripts/06_create_knowledge_graph.py

# Expected output:
# ============================================================
# 🌐 CREATING KNOWLEDGE GRAPH IN NEO4J
# ============================================================
#
# 🗑️  Clearing existing graph...
# ✅ Graph cleared
#
# 🔒 Creating constraints...
# ✅ Constraints created
#
# 📦 Loading Products...
# ✅ Loaded 100 products
#
# 🏭 Loading Suppliers...
# ✅ Loaded 15 suppliers
#
# 📍 Loading Locations...
# ✅ Loaded 30 locations
#
# 🏢 Loading Warehouses...
# ✅ Loaded 5 warehouses
#
# 🔗 Creating Product-Location relationships...
# ✅ Created 150 product-location relationships
#
# 🔗 Creating Product-Supplier relationships...
# ✅ Created 120 product-supplier relationships
#
# 📊 Loading Inventory...
# ✅ Loaded 100 inventory records
#
# 🏷️  Loading Batches...
# ✅ Loaded 200 batches
#
# 📋 Loading Orders...
# ✅ Loaded 40 orders
#
# 🔗 Creating Order-Product relationships...
# ✅ Created 180 order-product relationships
#
# 🚚 Loading Shipments...
# ✅ Loaded 50 shipments
#
# 🔍 Creating indexes...
# ✅ Indexes created
#
# 📊 Knowledge Graph Statistics:
# ============================================================
#
# 📦 Nodes:
#   Product: 100
#   Supplier: 15
#   Location: 30
#   Warehouse: 5
#   Inventory: 100
#   Batch: 200
#   Order: 40
#   Shipment: 50
#
# 🔗 Relationships:
#   LOCATED_IN: 150
#   SUPPLIED_BY: 120
#   HAS_INVENTORY: 100
#   HAS_BATCH: 200
#   CONTAINS: 180
#   PLACED_WITH: 40
#   STOCKS: 250
#   FULFILLS: 50
#   SHIPS_FROM: 50
#
# ============================================================
# Total Nodes: 540
# Total Relationships: 1140
# ============================================================
#
# ✅ Knowledge Graph created successfully!
#
# 🌐 Access Neo4j Browser at: http://localhost:7474
#    Username: neo4j
#    Password: storechain123
```

**Time:** 3-5 minutes

### 2.8 Verify Knowledge Graph

```bash
# Verify data sync between source databases and Neo4j
python scripts/09_verify_data_sync.py

# Expected output:
# ============================================================
# 🔍 DATA SYNCHRONIZATION VERIFICATION
# ============================================================
#
# 📦 Verifying Products...
#   PostgreSQL: 100 products
#   Neo4j:      100 products
#   ✅ Match!
#
# 🏭 Verifying Suppliers...
#   PostgreSQL: 15 suppliers
#   Neo4j:      15 suppliers
#   ✅ Match!
#
# ... (similar for all entities)
#
# 🔗 Verifying Relationships...
#   Product-Location (LOCATED_IN):
#     PostgreSQL: 150
#     Neo4j:      150
#     ✅ Match!
#
# ... (similar for all relationships)
#
# 🔬 Sample Data Comparison...
#   Product ID: P0001
#   PostgreSQL Data:
#     Name:     Fresh Milk
#     Category: Dairy
#     Price:    $3.99
#
#   Neo4j Data:
#     Name:     Fresh Milk
#     Category: Dairy
#     Price:    $3.99
#
#   ✅ Data matches perfectly!
#
# ============================================================
# 📊 VERIFICATION SUMMARY
# ============================================================
#   ✅ Products
#   ✅ Suppliers
#   ✅ Locations
#   ✅ Inventory
#   ✅ Batches
#   ✅ Orders
#   ✅ Warehouses
#   ✅ Shipments
#
# 🎉 ALL DATA SUCCESSFULLY SYNCED TO NEO4J!
#    The Knowledge Graph contains complete data from:
#    • PostgreSQL (store_catalog, inventory_mgmt, expiry_tracking)
#    • MongoDB (supply_chain_realtime)
# ============================================================
```

**✅ Knowledge Graph setup is now complete!**

---

## 🎮 Step 3: Application Run

### 3.1 Test the Agent System

```bash
# Test agents before starting UI
python scripts/10_test_agents.py

# Expected output:
# ============================================================
# 🧪 TESTING MULTI-AGENT SYSTEM
# ============================================================
#
# 🚀 Initializing orchestrator...
# 🦙 Loading Llama model: meta-llama/Llama-3.2-1B-Instruct
# 🔧 Device: cpu
# ⚠️  Running on CPU. Inference will be slower.
#
# [First run will download Llama model - 5GB - this takes 10-30 minutes]
#
# Downloading:   0%|          | 0.00/4.70G [00:00<?, ?B/s]
# Downloading:  10%|█         | 470M/4.70G [02:15<20:15, 3.48MB/s]
# ... (download continues)
# Downloading: 100%|██████████| 4.70G/4.70G [15:30<00:00, 5.05MB/s]
#
# ✅ Llama model loaded successfully!
# ✅ Connected to Neo4j
# ✅ Orchestrator ready!
#
# ============================================================
# Test Case 1/5
# ============================================================
# Query: Show me products with low stock
# Expected Agent: Product & Inventory Agent
#
# 🎯 Orchestrator received query: Show me products with low stock
# 📋 Selected agents: ['Product & Inventory Agent']
#    🤖 Calling Product & Inventory Agent...
#
# Actual Agent(s): Product & Inventory Agent
# ✅ PASS - Correct agent selected
#
# Summary: Based on the current inventory data, here are the products 
# with stock levels below their reorder points:
# 1. Fresh Milk - Current: 8 units, Reorder: 20 units
# 2. Whole Wheat Bread - Current: 12 units, Reorder: 25 units
# ... (more items)
#
# Records: 3
#
# ... (similar for other test cases)
#
# ============================================================
# 📊 TEST SUMMARY
# ============================================================
# Total Tests: 5
# Passed: 5
# Failed: 0
# Success Rate: 100.0%
# ============================================================
```

**Time:** 
- First run: 15-30 minutes (model download)
- Subsequent runs: 2-3 minutes

### 3.2 Start the Application

#### **Option A: Using main.py (Recommended)**

```bash
# Start the application
python main.py

# Expected output:
# 🚀 Starting Store Supply Chain Assistant...
# 🦙 Loading Llama model: meta-llama/Llama-3.2-1B-Instruct
# 🔧 Device: cpu
# ✅ Llama model loaded successfully!
#
# 🎯 Initializing Orchestrator...
# ✅ Initialized Product & Inventory Agent
# ✅ Initialized Supply Chain Agent
# ✅ Initialized Expiry Management Agent
# ✅ Initialized Knowledge Graph Agent
# ✅ Connected to Neo4j
# ✅ Orchestrator initialized with 4 agents
#
# You can now view your Streamlit app in your browser.
#
#   Local URL: http://localhost:8501
#   Network URL: http://192.168.1.100:8501
#
# [Browser should open automatically]
```

#### **Option B: Direct Streamlit**

```bash
# Alternative: Run Streamlit directly
streamlit run ui/streamlit_app.py --server.port 8501

# Same expected output as above
```

**Time:** 2-5 minutes for first startup

### 3.3 Access the Application

```bash
# The browser should open automatically to:
# http://localhost:8501

# If not, manually open your browser and go to:
# http://localhost:8501
```

### 3.4 Test the Application

Once the UI loads, try these sample queries:

1. **Simple Query:**
   ```
   Show products with low stock
   ```

2. **Shipment Query:**
   ```
   What shipments are currently in transit?
   ```

3. **Expiry Query:**
   ```
   Which products are expiring in the next week?
   ```

4. **Complex Query:**
   ```
   Tell me everything about dairy products
   ```

**Expected behavior:**
- Query appears in chat
- "🤔 Thinking..." spinner shows
- Response appears in 3-10 seconds (CPU) or 1-3 seconds (GPU)
- Data tables available in expandable sections

---

## ✅ Verification & Testing

### Quick Health Check

```bash
# Run this command to check all systems
python -c "
import sys
import torch
from neo4j import GraphDatabase
from pymongo import MongoClient
import psycopg2

print('✅ Python:', sys.version)
print('✅ PyTorch:', torch.__version__)

# Test Neo4j
try:
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'storechain123'))
    with driver.session() as session:
        result = session.run('MATCH (n) RETURN count(n) as count')
        count = result.single()['count']
        print(f'✅ Neo4j: {count} nodes')
    driver.close()
except Exception as e:
    print('❌ Neo4j:', e)

# Test MongoDB
try:
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
    db = client['supply_chain_realtime']
    count = db.shipments.count_documents({})
    print(f'✅ MongoDB: {count} shipments')
    client.close()
except Exception as e:
    print('❌ MongoDB:', e)

print('✅ All systems operational!')
"
```

### Test Individual Components

```bash
# Test Neo4j queries
python scripts/07_test_queries.py

# Test graph visualization
python scripts/08_visualize_graph.py

# Test data sync
python scripts/09_verify_data_sync.py

# Test agents
python scripts/10_test_agents.py
```

---

## 🐛 Troubleshooting

### Issue 1: Docker not running

**Error:**
```
ERROR: Couldn't connect to Docker daemon
```

**Solution:**
```bash
# Windows: Start Docker Desktop application
# Mac: Start Docker Desktop application
# Linux:
sudo systemctl start docker
sudo systemctl enable docker

# Verify Docker is running
docker ps
```

---

### Issue 2: Neo4j container fails to start

**Error:**
```
ERROR: for neo4j  Cannot start service neo4j: ...
```

**Solution:**
```bash
# Stop and remove existing containers
docker-compose down -v

# Remove old volumes
docker volume prune -f

# Restart
docker-compose up -d

# Check logs
docker-compose logs neo4j
```

---

### Issue 3: Model download fails

**Error:**
```
HTTPError: 403 Client Error: Forbidden
```

**Solution:**

```bash
# Option 1: Login to Hugging Face
pip install huggingface_hub
huggingface-cli login
# Enter your Hugging Face token

# Option 2: Pre-download the model
python -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
print('Downloading model...')
model = AutoModelForCausalLM.from_pretrained('meta-llama/Llama-3.2-1B-Instruct')
tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-3.2-1B-Instruct')
print('Download complete!')
"

# Option 3: Use alternative model (no auth needed)
# Edit config/llm_config.py:
# 'model_name': 'gpt2'
```

---

### Issue 4: Port already in use

**Error:**
```
ERROR: for neo4j  Cannot start service neo4j: 
Bind for 0.0.0.0:7474 failed: port is already allocated
```

**Solution:**

```bash
# Check what's using the port
# Windows:
netstat -ano | findstr :7474

# Mac/Linux:
lsof -i :7474

# Kill the process or change Neo4j port in docker-compose.yml
# Edit docker-compose.yml:
ports:
  - "7475:7474"  # Change 7474 to 7475
  - "7688:7687"  # Change 7687 to 7688

# Update config/neo4j_config.py:
NEO4J_CONFIG = {
    'uri': 'bolt://localhost:7688',  # Update port
    ...
}
```

---

### Issue 5: Out of memory

**Error:**
```
RuntimeError: CUDA out of memory
MemoryError: Unable to allocate
```

**Solution:**

```bash
# Reduce model size
# Edit config/llm_config.py:

LLAMA_CONFIG = {
    'max_length': 256,      # Reduce from 512
    'device': 'cpu',        # Force CPU if GPU has issues
}

# In llm/llama_client.py, use float32 instead of float16:
torch_dtype=torch.float32

# Close other applications to free RAM
```

---

### Issue 6: Streamlit won't start

**Error:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solution:**

```bash
# Verify virtual environment is activated
# Your prompt should show (venv)

# If not activated:
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Reinstall streamlit
pip install streamlit --upgrade

# Try again
python main.py
```

---

### Issue 7: PostgreSQL connection fails

**Error:**
```
psycopg2.OperationalError: could not connect to server
```

**Solution:**

```bash
# Check if PostgreSQL is installed and running
# Windows: Check Services app
# Mac:
brew services list | grep postgresql

# Linux:
sudo systemctl status postgresql

# If not running, start it:
# Mac:
brew services start postgresql

# Linux:
sudo systemctl start postgresql

# Update password in config/db_config.py if needed
```

---

### Issue 8: Slow query responses

**Problem:** Queries taking 30+ seconds

**Solution:**

```bash
# 1. Check if using GPU
python -c "import torch; print('GPU:', torch.cuda.is_available())"

# 2. Reduce token generation
# Edit agent methods to use:
max_new_tokens=100  # Instead of 256

# 3. Add Neo4j indexes
# In Neo4j Browser (http://localhost:7474):
CREATE INDEX product_name IF NOT EXISTS FOR (p:Product) ON (p.name);
CREATE INDEX product_category IF NOT EXISTS FOR (p:Product) ON (p.category);

# 4. Restart application
# Press Ctrl+C to stop
python main.py
```

---

## 🚀 Quick Start (TL;DR)

**For experienced users - complete setup in ~30 minutes:**

```bash
# 1. Clone and setup environment
git clone https://github.com/yourusername/store-supply-chain.git
cd store-supply-chain
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Start Neo4j
docker-compose up -d
sleep 30  # Wait for Neo4j

# 3. Generate data and create Knowledge Graph
python scripts/01_generate_data.py
python scripts/02_setup_postgresql.py
python scripts/03_setup_mongodb.py
python scripts/06_create_knowledge_graph.py

# 4. Verify
python scripts/09_verify_data_sync.py

# 5. Run application
python main.py

# Open: http://localhost:8501
```

**Total time:** 
- First run: 30-45 minutes (includes model download)
- Subsequent runs: 5-10 minutes

---

## 📊 Expected Directory Structure After Setup

```
store_supply_chain/
├── venv/                           # Virtual environment
├── agents/                         # Agent code
├── database/                       # Database connectors
├── llm/                           # LLM client
├── ui/                            # Streamlit UI
├── config/                        # Configuration files
├── scripts/                       # Setup scripts
├── synthetic_data/                # Generated data ✅
│   ├── products.csv
│   ├── suppliers.csv
│   ├── shipments.json
│   └── ... (more files)
├── docker-compose.yml
├── requirements.txt
├── main.py
└── README.md
```

---

## 🔄 Starting/Stopping the System

### Start Everything

```bash
# Start Neo4j (if not running)
docker-compose up -d

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Start application
python main.py

# Open browser to: http://localhost:8501
```

### Stop Everything

```bash
# Stop Streamlit application
# Press Ctrl+C in the terminal running main.py

# Stop Neo4j
docker-compose down

# Deactivate virtual environment
deactivate
```

### Restart Everything

```bash
# Restart Neo4j
docker-compose restart neo4j

# Restart application
python main.py
```

---

## 🔄 Updating Data

### Refresh Knowledge Graph with New Data

```bash
# 1. Regenerate synthetic data
python scripts/01_generate_data.py

# 2. Update source databases
python scripts/02_setup_postgresql.py
python scripts/03_setup_mongodb.py

# 3. Recreate Knowledge Graph
python scripts/06_create_knowledge_graph.py

# 4. Verify
python scripts/09_verify_data_sync.py

# 5. No need to restart application - data is refreshed
```

---

## 📞 Getting Help

### Check Logs

```bash
# Application logs
# Check the terminal where you ran: python main.py

# Neo4j logs
docker-compose logs neo4j

# Follow logs in real-time
docker-compose logs -f neo4j
```

### Common Commands Reference

```bash
# Check Neo4j status
docker-compose ps

# Stop Neo4j
docker-compose stop

# Start Neo4j
docker-compose start

# Restart Neo4j
docker-compose restart

# View Neo4j data directory
docker volume ls | grep neo4j

# Remove all Neo4j data (⚠️ CAUTION)
docker-compose down -v

# Test Python imports
python -c "import torch, transformers, neo4j, streamlit; print('All OK')"

# Check Python packages
pip list

# Update all packages
pip install -r requirements.txt --upgrade
```

---

## ✅ Success Checklist

After completing all steps, verify:

- [ ] Virtual environment activated (`(venv)` in prompt)
- [ ] All Python packages installed (`pip list` shows 50+ packages)
- [ ] Docker running (`docker ps` shows neo4j container)
- [ ] Neo4j accessible (http://localhost:7474 login works)
- [ ] Synthetic data generated (`synthetic_data/` directory exists with CSV/JSON files)
- [ ] Knowledge Graph created (`Neo4j has 540+ nodes`)
- [ ] Agent tests pass (`python scripts/10_test_agents.py` shows 100% success)
- [ ] Application running (`http://localhost:8501` shows UI)
- [ ] Sample queries work (try "Show products with low stock")

---

## 🎯 Next Steps

Once setup is complete:

1. **Explore the UI:** Try different sample queries from the sidebar
2. **View Neo4j Browser:** Visualize the knowledge graph at http://localhost:7474
3. **Check Documentation:** Read `README.md` for detailed usage
4. **Customize:** Modify `config/` files to tune performance
5. **Develop:** Add new agents following the development guide

---

## 📝 Notes

- **First run:** Llama model download (~5GB) takes 10-30 minutes
- **CPU mode:** Queries take 3-10 seconds (normal)
- **GPU mode:** Queries take 1-3 seconds (recommended for production)
- **Data refresh:** Run `scripts/06_create_knowledge_graph.py` to update Neo4j
- **Clean slate:** `docker-compose down -v` removes all Neo4j data

---

**Setup Complete! 🎉**

You now have a fully functional multi-agent AI system powered by Neo4j Knowledge Graph and Llama 3.2-1B!

For questions or issues, please check the [Troubleshooting](#troubleshooting) section or open an issue on GitHub.

---

**Last Updated:** December 24, 2024  
**Version:** 1.0.0