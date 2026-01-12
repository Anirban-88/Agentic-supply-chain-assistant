# mcp_servers/base_server.py

import asyncio
import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional
import traceback
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

class MCPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP servers"""
    
    agent = None  # Will be set by the server
    
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
            'agent': self.agent.name if self.agent else 'unknown',
            'version': '0.1.0'
        }
        self._send_json_response(response)
    
    def _handle_capabilities(self):
        """Capabilities endpoint"""
        if not self.agent:
            self._send_json_response({'error': 'Agent not initialized'}, status=500)
            return
        
        response = {
            'name': self.agent.name,
            'description': self.agent.description,
            'keywords': self.agent.keywords,
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
            
            # Process query with agent
            if not self.agent:
                self._send_json_response({'error': 'Agent not initialized'}, status=500)
                return
            
            logger.info(f"Processing query: {query}")
            result = self.agent.process(query)
            
            # Add metadata
            response = {
                'agent': self.agent.name,
                'query': query,
                'result': result,
                'status': 'success'
            }
            
            self._send_json_response(response)
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            logger.error(traceback.format_exc())
            self._send_json_response({
                'error': str(e),
                'status': 'error'
            }, status=500)
    
    def _send_json_response(self, data: Dict[str, Any], status: int = 200):
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


def run_mcp_server(agent, port: int, host: str = '0.0.0.0'):
    """
    Run an MCP server for the given agent
    
    Args:
        agent: Agent instance to wrap
        port: Port to listen on
        host: Host to bind to
    """
    # Set the agent on the handler class
    MCPRequestHandler.agent = agent
    
    # Create server
    server = HTTPServer((host, port), MCPRequestHandler)
    
    logger.info(f"🚀 {agent.name} server starting on {host}:{port}")
    logger.info(f"   Health check: http://{host}:{port}/health")
    logger.info(f"   Capabilities: http://{host}:{port}/capabilities")
    logger.info(f"   Query endpoint: http://{host}:{port}/query")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info(f"Shutting down {agent.name} server")
        server.shutdown()


if __name__ == '__main__':
    print("This is a base server module. Use specific agent servers instead.")
