import logging
import logging.handlers
import os
from datetime import datetime

# Create logs directory
LOGS_DIR = 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)

# Log file paths
MAIN_LOG = os.path.join(LOGS_DIR, 'application.log')
ERROR_LOG = os.path.join(LOGS_DIR, 'errors.log')
AGENTS_LOG = os.path.join(LOGS_DIR, 'agents.log')
MCP_LOG = os.path.join(LOGS_DIR, 'mcp_servers.log')
LLM_LOG = os.path.join(LOGS_DIR, 'llm_extraction.log')
QUERIES_LOG = os.path.join(LOGS_DIR, 'queries.log')

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(asctime)s [%(levelname)s] %(name)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        },
        'main_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': MAIN_LOG,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': ERROR_LOG,
            'maxBytes': 10485760,
            'backupCount': 5,
            'encoding': 'utf8'
        },
        'agents_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': AGENTS_LOG,
            'maxBytes': 10485760,
            'backupCount': 3,
            'encoding': 'utf8'
        },
        'mcp_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': MCP_LOG,
            'maxBytes': 10485760,
            'backupCount': 3,
            'encoding': 'utf8'
        },
        'llm_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': LLM_LOG,
            'maxBytes': 5242880,  # 5MB
            'backupCount': 3,
            'encoding': 'utf8'
        },
        'queries_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'filename': QUERIES_LOG,
            'maxBytes': 5242880,
            'backupCount': 3,
            'encoding': 'utf8'
        }
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'main_file', 'error_file'],
            'level': 'INFO',
            'propagate': False
        },
        'agents': {
            'handlers': ['console', 'agents_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'agents.orchestrator': {
            'handlers': ['console', 'agents_file', 'queries_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'agents.product_agent': {
            'handlers': ['console', 'agents_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'agents.supply_chain_agent': {
            'handlers': ['console', 'agents_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'agents.expiry_agent': {
            'handlers': ['console', 'agents_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'agents.graph_agent': {
            'handlers': ['console', 'agents_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'mcp_servers': {
            'handlers': ['console', 'mcp_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'llm': {
            'handlers': ['console', 'llm_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'llm.llama_client': {
            'handlers': ['console', 'llm_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'database': {
            'handlers': ['console', 'main_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'database.neo4j_connector': {
            'handlers': ['console', 'main_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}


def setup_logging():
    """Initialize logging configuration"""
    import logging.config
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Log startup
    logger = logging.getLogger(__name__)
    logger.info("="*60)
    logger.info("Logging initialized")
    logger.info(f"Main log: {MAIN_LOG}")
    logger.info(f"Error log: {ERROR_LOG}")
    logger.info(f"Agents log: {AGENTS_LOG}")
    logger.info(f"MCP log: {MCP_LOG}")
    logger.info(f"LLM log: {LLM_LOG}")
    logger.info(f"Queries log: {QUERIES_LOG}")
    logger.info("="*60)


if __name__ == '__main__':
    setup_logging()
    print("✅ Logging configuration created")
    print(f"\nLog files will be created in: {os.path.abspath(LOGS_DIR)}/")
