#!/usr/bin/env python3
# mcp_servers/expiry_server.py

import sys
import os
import argparse
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.expiry_agent import ExpiryAgent
from mcp_servers.base_server import run_mcp_server
from config.logging_config import setup_logging

setup_logging()
logger = logging.getLogger('mcp_servers.expiry_server')


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Expiry Management Agent MCP Server')
    parser.add_argument('--port', type=int, default=8003, help='Port to listen on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    args = parser.parse_args()
    
    try:
        # Initialize agent
        logger.info("Initializing Expiry Agent...")
        agent = ExpiryAgent()
        
        # Run server
        run_mcp_server(agent, args.port, args.host)
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    main()
