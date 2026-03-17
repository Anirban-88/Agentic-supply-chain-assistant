# Production Environment Configuration for Oracle Cloud
# Copy this file to .env and update the values as needed

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# PostgreSQL Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123_CHANGE_ME
POSTGRES_DB=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# MongoDB Configuration
MONGO_USERNAME=admin
MONGO_PASSWORD=admin123_CHANGE_ME
MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_DATABASE=supply_chain

# Redis Configuration
REDIS_PASSWORD=redis123_CHANGE_ME
REDIS_HOST=redis
REDIS_PORT=6379

# Neo4j Configuration
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=storechain123_CHANGE_ME

# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# LLM Configuration
MODEL_NAME=meta-llama/Llama-3.2-1B
DEVICE=cpu
MAX_LENGTH=512
TEMPERATURE=0.7

# =============================================================================
# ORACLE CLOUD SPECIFIC CONFIGURATION
# =============================================================================

# Instance Configuration
OCI_REGION=us-ashburn-1
OCI_COMPARTMENT_ID=your_compartment_ocid_here
OCI_INSTANCE_ID=your_instance_ocid_here

# Network Configuration
PUBLIC_IP=your_public_ip_here
DOMAIN_NAME=your_domain_here

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

# JWT Secret (generate a random string)
JWT_SECRET=your_jwt_secret_here

# API Keys (if needed)
OPENAI_API_KEY=your_openai_key_here
HUGGINGFACE_API_KEY=your_hf_key_here

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Log Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
LOG_FILE_MAX_SIZE=10MB
LOG_FILE_BACKUP_COUNT=5

# =============================================================================
# BACKUP CONFIGURATION
# =============================================================================

# Backup Settings
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=7
BACKUP_LOCATION=/home/opc/backups

# =============================================================================
# MONITORING CONFIGURATION
# =============================================================================

# Health Check Settings
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10

# Metrics Collection
METRICS_ENABLED=true
METRICS_PORT=9090
