#!/usr/bin/env python3
# mcp_servers/orchestrator_server.py

import sys
import os
import argparse
import logging
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.distributed_orchestrator import get_distributed_orchestrator
from config.logging_config import setup_logging
import os

setup_logging()
logger = logging.getLogger('mcp_servers.orchestrator_server')

# Use distributed orchestrator by default
USE_DISTRIBUTED = os.getenv('USE_DISTRIBUTED_ORCHESTRATOR', 'true').lower() == 'true'


class OrchestratorRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Orchestrator"""
    
    orchestrator = None
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/health':
            self._handle_health()
        elif parsed_path.path == '/capabilities':
            self._handle_capabilities()
        else:
            self._send_json_response({'error': 'Not found'}, status=404)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/query':
            self._handle_query()
        else:
            self._send_json_response({'error': 'Not found'}, status=404)
    
    def _handle_health(self):
        """Health check endpoint"""
        response = {
            'status': 'healthy',
            'service': 'Orchestrator',
            'version': '0.1.0',
            'agents': len(self.orchestrator.agents) if self.orchestrator else 0
        }
        self._send_json_response(response)
    
    def _handle_capabilities(self):
        """Capabilities endpoint"""
        if not self.orchestrator:
            self._send_json_response({'error': 'Orchestrator not initialized'}, status=500)
            return
        
        response = {
            'name': 'Supply Chain Orchestrator',
            'description': 'Routes queries to appropriate agents and aggregates responses',
            'agents': [agent.name for agent in self.orchestrator.agents],
            'endpoints': ['/query', '/health', '/capabilities']
        }
        self._send_json_response(response)
    
    def _handle_query(self):
        """Query processing endpoint"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            if not body:
                self._send_json_response({'error': 'Empty request body'}, status=400)
                return
            
            # Parse JSON
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self._send_json_response({'error': 'Invalid JSON'}, status=400)
                return
            
            # Get query
            query = data.get('query')
            if not query:
                self._send_json_response({'error': 'Missing query parameter'}, status=400)
                return
            
            # Process query with orchestrator
            if not self.orchestrator:
                self._send_json_response({'error': 'Orchestrator not initialized'}, status=500)
                return
            
            logger.info(f"Processing query: {query}")
            result = self.orchestrator.process_query(query)
            
            # Add metadata
            response = {
                'service': 'Orchestrator',
                'query': query,
                'result': result,
                'status': 'success'
            }
            
            self._send_json_response(response)
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self._send_json_response({
                'error': str(e),
                'status': 'error'
            }, status=500)
    
    def _send_json_response(self, data: dict, status: int = 200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle OPTIONS for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Override to use proper logging"""
        logger.info(f"{self.address_string()} - {format % args}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Orchestrator MCP Server')
    parser.add_argument('--port', type=int, default=8000, help='Port to listen on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    args = parser.parse_args()
    
    try:
        # Initialize orchestrator (distributed or direct mode)
        if USE_DISTRIBUTED:
            logger.info("Initializing Distributed Orchestrator (HTTP-based agent communication)...")
            orchestrator = get_distributed_orchestrator()
        else:
            logger.info("Initializing Direct Orchestrator (in-process agents)...")
            from agents.orchestrator import get_orchestrator
            orchestrator = get_orchestrator()
        
        # Set orchestrator on handler class
        OrchestratorRequestHandler.orchestrator = orchestrator
        
        # Create server
        server = HTTPServer((args.host, args.port), OrchestratorRequestHandler)
        
        logger.info(f"🚀 Orchestrator server starting on {args.host}:{args.port}")
        logger.info(f"   Health check: http://{args.host}:{args.port}/health")
        logger.info(f"   Capabilities: http://{args.host}:{args.port}/capabilities")
        logger.info(f"   Query endpoint: http://{args.host}:{args.port}/query")
        
        # Run server
        server.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("Shutting down Orchestrator server")
        server.shutdown()
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    main()
