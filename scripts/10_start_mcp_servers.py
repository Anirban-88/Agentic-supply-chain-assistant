

import sys
import os
import logging
import asyncio
import signal
import argparse
import subprocess
from typing import Dict, List, Any

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.mcp_config import MCP_SERVERS, ORCHESTRATOR_CONFIG, LOGGING_CONFIG
import logging.config

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Global variables for process management
processes = {}
running = True

class MCPServerManager:
    """Manage MCP server processes"""
    
    def __init__(self, use_subprocess=True):
        """
        Initialize MCP server manager
        
        Args:
            use_subprocess: If True, use subprocess to start servers
                           If False, import and run servers directly
        """
        self.use_subprocess = use_subprocess
        self.processes = {}
    
    async def start_all_servers(self):
        """Start all MCP servers"""
        logger.info("Starting all MCP servers...")
        
        # Start individual agent servers first
        for server_id, config in MCP_SERVERS.items():
            if config['enabled']:
                await self.start_server(server_id, config)
        
        # Start orchestrator last
        await self.start_orchestrator()
        
        logger.info("All servers started")
    
    async def start_server(self, server_id: str, config: Dict[str, Any]):
        """
        Start a single MCP server
        
        Args:
            server_id: Server identifier
            config: Server configuration
        """
        logger.info(f"Starting {server_id} server on port {config['port']}...")
        
        if self.use_subprocess:
            # Start as separate process
            cmd = [
                sys.executable,
                "-m", f"mcp_servers.{server_id}_server",
                "--port", str(config['port']),
                "--transport", "http"
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            self.processes[server_id] = process
            logger.info(f"{server_id} server started with PID {process.pid}")
            
            # Start log monitoring
            asyncio.create_task(self._monitor_process_logs(server_id, process))
        else:
            # Import and run directly (for debugging)
            module_name = f"mcp_servers.{server_id}_server"
            try:
                module = __import__(module_name, fromlist=['run_server'])
                asyncio.create_task(module.run_server(port=config['port']))
                logger.info(f"{server_id} server started in current process")
            except Exception as e:
                logger.error(f"Failed to start {server_id} server: {e}")
    
    async def start_orchestrator(self):
        """Start the orchestrator agent"""
        logger.info(f"Starting orchestrator on port {ORCHESTRATOR_CONFIG['port']}...")
        
        if self.use_subprocess:
            # Start as separate process
            cmd = [
                sys.executable,
                "-m", "agents.orchestrator",
                "--port", str(ORCHESTRATOR_CONFIG['port']),
                "--mode", "server"
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            self.processes['orchestrator'] = process
            logger.info(f"Orchestrator started with PID {process.pid}")
            
            # Start log monitoring
            asyncio.create_task(self._monitor_process_logs('orchestrator', process))
        else:
            # Import and run directly (for debugging)
            try:
                from agents.orchestrator import run_server
                asyncio.create_task(run_server(port=ORCHESTRATOR_CONFIG['port']))
                logger.info("Orchestrator started in current process")
            except Exception as e:
                logger.error(f"Failed to start orchestrator: {e}")
    
    async def _monitor_process_logs(self, name: str, process: subprocess.Popen):
        """
        Monitor and log process output
        
        Args:
            name: Process name
            process: Subprocess object
        """
        while True:
            # Check if process is still running
            if process.poll() is not None:
                logger.warning(f"{name} process exited with code {process.returncode}")
                break
            
            # Read stdout
            if process.stdout:
                line = process.stdout.readline()
                if line:
                    logger.info(f"[{name}] {line.strip()}")
            
            # Read stderr
            if process.stderr:
                line = process.stderr.readline()
                if line:
                    logger.error(f"[{name}] {line.strip()}")
            
            # Sleep briefly to avoid CPU spinning
            await asyncio.sleep(0.1)
    
    async def stop_all_servers(self):
        """Stop all running servers"""
        logger.info("Stopping all servers...")
        
        if self.use_subprocess:
            # Stop orchestrator first
            if 'orchestrator' in self.processes:
                self._stop_process('orchestrator', self.processes['orchestrator'])
            
            # Stop agent servers
            for server_id, process in self.processes.items():
                if server_id != 'orchestrator':
                    self._stop_process(server_id, process)
        
        logger.info("All servers stopped")
    
    def _stop_process(self, name: str, process: subprocess.Popen):
        """
        Stop a single process
        
        Args:
            name: Process name
            process: Subprocess object
        """
        if process.poll() is None:  # Process is still running
            logger.info(f"Stopping {name} (PID {process.pid})...")
            process.terminate()
            
            # Wait for process to terminate
            try:
                process.wait(timeout=5)
                logger.info(f"{name} stopped")
            except subprocess.TimeoutExpired:
                logger.warning(f"{name} did not terminate, killing...")
                process.kill()


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Start MCP servers')
    parser.add_argument('--subprocess', action='store_true', 
                        help='Start servers as separate processes')
    args = parser.parse_args()
    
    manager = MCPServerManager(use_subprocess=args.subprocess)
    
    # Setup signal handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(manager)))
    
    try:
        await manager.start_all_servers()
        
        # Keep running until shutdown
        while running:
            await asyncio.sleep(1)
    finally:
        await manager.stop_all_servers()


async def shutdown(manager):
    """Shutdown function for signal handling"""
    global running
    logger.info("Shutdown signal received")
    running = False
    await manager.stop_all_servers()


if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)