import os
from datetime import datetime

# MCP Server Configuration
# Each agent runs as a separate MCP server with its own port

MCP_SERVERS = {
    # Product & Inventory Agent Server
    'product': {
        'enabled': True,
        'port': 8001,
        'name': 'Product & Inventory Agent',
        'description': 'Handles product catalog, inventory levels, and stock management',
        'endpoints': [
            '/query',
            '/health',
            '/capabilities'
        ],
        'timeout': 30,
        'max_retries': 3
    },
    
    # Supply Chain Agent Server
    'supply_chain': {
        'enabled': True,
        'port': 8002,
        'name': 'Supply Chain Agent',
        'description': 'Manages shipment tracking, warehouse operations, and logistics',
        'endpoints': [
            '/query',
            '/health',
            '/capabilities'
        ],
        'timeout': 30,
        'max_retries': 3
    },
    
    # Expiry Management Agent Server
    'expiry': {
        'enabled': True,
        'port': 8003,
        'name': 'Expiry Management Agent',
        'description': 'Tracks product expiry dates, batch information, and freshness',
        'endpoints': [
            '/query',
            '/health',
            '/capabilities'
        ],
        'timeout': 30,
        'max_retries': 3
    },
    
    # Knowledge Graph Agent Server
    'graph': {
        'enabled': True,
        'port': 8004,
        'name': 'Knowledge Graph Agent',
        'description': 'Handles complex queries across multiple databases and relationships',
        'endpoints': [
            '/query',
            '/health',
            '/capabilities'
        ],
        'timeout': 60,  # Longer timeout for complex graph queries
        'max_retries': 2
    }
}

# Orchestrator Configuration
# The orchestrator coordinates between all agent servers
ORCHESTRATOR_CONFIG = {
    'enabled': True,
    'port': 8000,
    'name': 'Supply Chain Orchestrator',
    'description': 'Routes queries to appropriate agents and aggregates responses',
    'mode': 'server',  # 'server' or 'standalone'
    'timeout': 120,  # Total orchestration timeout
    'max_parallel_agents': 3,  # Maximum agents to query in parallel
    'fallback_enabled': True,  # Enable fallback to alternative agents on failure
    'cache_enabled': True,  # Cache common queries
    'cache_ttl': 300,  # Cache time-to-live in seconds
}

# HTTP Transport Configuration
TRANSPORT_CONFIG = {
    'protocol': 'http',
    'host': os.getenv('MCP_HOST', '0.0.0.0'),
    'cors_enabled': True,
    'cors_origins': ['*'],  # Allow all origins in development
    'max_request_size': 10 * 1024 * 1024,  # 10MB
    'request_timeout': 60,
    'keepalive_timeout': 75,
}

# Server Health Check Configuration
HEALTH_CHECK_CONFIG = {
    'enabled': True,
    'interval': 30,  # Health check interval in seconds
    'endpoint': '/health',
    'timeout': 5,
    'failure_threshold': 3,  # Number of failures before marking as unhealthy
    'success_threshold': 1,  # Number of successes to mark as healthy again
}

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'json': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': 'logs/mcp_servers.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': 'logs/mcp_errors.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        }
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False
        },
        'agents': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'mcp_servers': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'uvicorn': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

# Performance Monitoring Configuration
MONITORING_CONFIG = {
    'enabled': True,
    'metrics_port': 9090,
    'collect_metrics': True,
    'metrics': [
        'request_count',
        'request_duration',
        'error_count',
        'agent_response_time',
        'cache_hit_rate'
    ]
}

# Rate Limiting Configuration
RATE_LIMIT_CONFIG = {
    'enabled': True,
    'requests_per_minute': 60,
    'burst_size': 10,
    'storage': 'memory',  # 'memory' or 'redis'
}

# Security Configuration
SECURITY_CONFIG = {
    'api_key_enabled': False,  # Set to True in production
    'api_keys': os.getenv('MCP_API_KEYS', '').split(',') if os.getenv('MCP_API_KEYS') else [],
    'require_https': False,  # Set to True in production
    'allowed_ips': [],  # Empty list allows all IPs
}

# Development vs Production Settings
ENVIRONMENT = os.getenv('MCP_ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    # Production overrides
    TRANSPORT_CONFIG['cors_origins'] = os.getenv('ALLOWED_ORIGINS', '*').split(',')
    SECURITY_CONFIG['api_key_enabled'] = True
    SECURITY_CONFIG['require_https'] = True
    LOGGING_CONFIG['handlers']['console']['level'] = 'WARNING'
    RATE_LIMIT_CONFIG['requests_per_minute'] = 120

# Utility function to get all server URLs
def get_server_urls():
    """Get dictionary of all server URLs"""
    urls = {}
    # Use localhost for client connections (0.0.0.0 is for server binding only)
    host = 'localhost' if TRANSPORT_CONFIG['host'] == '0.0.0.0' else TRANSPORT_CONFIG['host']
    
    # Add orchestrator URL
    urls['orchestrator'] = f"http://{host}:{ORCHESTRATOR_CONFIG['port']}"
    
    # Add agent server URLs
    for server_id, config in MCP_SERVERS.items():
        if config['enabled']:
            urls[server_id] = f"http://{host}:{config['port']}"
    
    return urls

# Utility function to get enabled servers
def get_enabled_servers():
    """Get list of enabled server IDs"""
    return [server_id for server_id, config in MCP_SERVERS.items() if config['enabled']]

# Print configuration summary
if __name__ == '__main__':
    print("=" * 60)
    print("MCP Server Configuration Summary")
    print("=" * 60)
    print(f"\nEnvironment: {ENVIRONMENT}")
    print(f"\nOrchestrator:")
    print(f"  URL: http://{TRANSPORT_CONFIG['host']}:{ORCHESTRATOR_CONFIG['port']}")
    print(f"\nAgent Servers:")
    for server_id, config in MCP_SERVERS.items():
        if config['enabled']:
            print(f"  {config['name']}")
            print(f"    URL: http://{TRANSPORT_CONFIG['host']}:{config['port']}")
            print(f"    Timeout: {config['timeout']}s")
    print(f"\nHealth Checks: {'Enabled' if HEALTH_CHECK_CONFIG['enabled'] else 'Disabled'}")
    print(f"Rate Limiting: {'Enabled' if RATE_LIMIT_CONFIG['enabled'] else 'Disabled'}")
    print(f"Monitoring: {'Enabled' if MONITORING_CONFIG['enabled'] else 'Disabled'}")
    print(f"CORS: {'Enabled' if TRANSPORT_CONFIG['cors_enabled'] else 'Disabled'}")
    print("=" * 60)
