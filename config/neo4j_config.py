# config/neo4j_config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Neo4j Configuration
NEO4J_CONFIG = {
    'uri': os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
    'username': os.getenv('NEO4J_USERNAME', 'neo4j'),
    'password': os.getenv('NEO4J_PASSWORD', 'password'),
}

print(f"✅ Neo4j configuration loaded")
print(f"   URI: {NEO4J_CONFIG['uri']}")
print(f"   Username: {NEO4J_CONFIG['username']}")
