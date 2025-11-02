#!/usr/bin/env python3
"""
MCP Protocol Compliant Server Runner

Production-ready MCP server yang mengikuti standard MCP Protocol 2025-06-18
dengan proper endpoints, error handling, dan structure yang rapi.
https://modelcontextprotocol.io/docs/develop/build-server 
"""

import asyncio
import logging
import sys
import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

# Import MCP components
try:
    from .mcp_server import MCPServer
    from .mcp_tools import MCPToolsRegistry
except ImportError:
    # Fallback to absolute imports
    from mcp_server import MCPServer
    from mcp_tools import MCPToolsRegistry
# Note: SSEToolsProvider moved to backup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPServerRunner:
    """Production MCP Server Runner dengan HTTP endpoints"""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self._start_time = time.time()
        
        # Initialize components
        self.tools_registry = MCPToolsRegistry()
        self.mcp_server = MCPServer(
            server_name="OCR PDF MCP Server",
            server_version="1.0.0",
            description="MCP Protocol compliant server for OCR PDF processing"
        )
        self.mcp_server.set_tools_registry(self.tools_registry)
        
        # Register all tools from registry to MCP server
        self._register_tools_to_mcp_server()
        
        # Skip SSE provider for now (has complex dependencies)
        self.sse_provider = None
    
    def _register_tools_to_mcp_server(self):
        """Register all tools from registry to MCP server"""
        tools = self.tools_registry.list_tools()
        for tool in tools:
            handler = self.tools_registry.get_tool_handler(tool.name)
            if handler:
                success = self.mcp_server.register_tool(tool, handler)
                if success:
                    logger.debug(f"Registered tool to MCP server: {tool.name}")
                else:
                    logger.error(f"Failed to register tool to MCP server: {tool.name}")
            else:
                logger.error(f"No handler found for tool: {tool.name}")
        
        logger.info(f"Registered {len(self.mcp_server._tools)} tools to MCP server")
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="OCR PDF MCP Server",
            description="MCP Protocol compliant server for OCR PDF processing",
            version="1.0.0"
        )
        
        # Add custom middleware for connection tracking
        @self.app.middleware("http")
        async def add_custom_headers(request: Request, call_next):
            # Add helpful headers for MCP clients
            response = await call_next(request)
            response.headers["X-MCP-Version"] = "2025-06-18"
            response.headers["X-Server-Status"] = str(self.mcp_server.state.value if hasattr(self.mcp_server.state, 'value') else self.mcp_server.state)
            response.headers["X-Server-Name"] = self.mcp_server.server_name
            
            # Log connection attempts (debug level)
            if request.method in ["POST", "GET"] and not request.url.path.startswith("/static"):
                logger.debug(f"{request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}")
            
            return response
        
        # Add error handling middleware
        @self.app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            """Global exception handler for better error responses"""
            logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
            
            # For API endpoints, return JSON error
            if request.url.path.startswith(("/api/", "/mcp/", "/jsonrpc")):
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": {
                            "code": -32603,
                            "message": "Internal server error",
                            "data": str(exc) if logger.level <= logging.DEBUG else "Server error"
                        }
                    }
                )
            else:
                # For other endpoints, return HTTP error
                raise HTTPException(status_code=500, detail="Internal server error")
        
        # Setup CORS with specific settings for MCP clients
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, specify actual origins
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=[
                "Content-Type", 
                "Authorization", 
                "X-Requested-With",
                "Accept",
                "Origin",
                "User-Agent",
                "Cache-Control"
            ],
            expose_headers=["X-MCP-Version", "X-Server-Status"]
        )
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup all MCP standard routes"""
        
        # Health check
        @self.app.get("/")
        async def root():
            """Root endpoint with server info"""
            return {
                "name": "OCR PDF MCP Server",
                "version": "1.0.0",
                "description": "MCP Protocol 2025-06-18 compliant server for OCR PDF processing",
                "protocol_version": "2025-06-18",
                "status": "ready",
                "endpoints": {
                    "initialize": "/mcp/initialize",
                    "tools_list": "/mcp/tools/list", 
                    "tools_call": "/mcp/tools/call",
                    "jsonrpc": "/jsonrpc",
                    "health": "/health"
                }
            }
            
        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            return {
                "status": "healthy", 
                "timestamp": time.time(),
                "server": "OCR PDF MCP Server",
                "version": "1.0.0",
                "protocol": "MCP 2025-06-18"
            }
        
        @self.app.get("/api/version")
        async def api_version():
            """API Version endpoint - commonly requested by MCP clients"""
            return {
                "name": self.mcp_server.server_name,
                "version": self.mcp_server.server_version,
                "protocol_version": "2025-06-18",
                "capabilities": {
                    "tools": True,
                    "resources": False,
                    "prompts": False,
                    "logging": True
                },
                "status": "ready"
            }
        
        @self.app.get("/api/status")
        async def api_status():
            """Connection status endpoint"""
            return {
                "server_name": self.mcp_server.server_name,
                "server_version": self.mcp_server.server_version,
                "state": self.mcp_server.state.value if hasattr(self.mcp_server.state, 'value') else str(self.mcp_server.state),
                "timestamp": time.time(),
                "tools_count": len(self.mcp_server._tools),
                "uptime": time.time() - getattr(self, '_start_time', time.time())
            }
        
        @self.app.get("/api/ping")
        async def api_ping():
            """Simple ping endpoint for connection testing"""
            return {"pong": True, "timestamp": time.time()}
        
        # Static files - favicon and logo
        @self.app.get("/favicon.ico")
        async def favicon():
            """Serve favicon.ico"""
            favicon_path = Path(__file__).parent.parent / "favicon.ico"
            if favicon_path.exists():
                return FileResponse(favicon_path, media_type="image/x-icon")
            else:
                raise HTTPException(status_code=404, detail="Favicon not found")
        
        @self.app.get("/logo.png")
        async def logo():
            """Serve logo.png"""
            logo_path = Path(__file__).parent.parent / "logo.png"
            if logo_path.exists():
                return FileResponse(logo_path, media_type="image/png")
            else:
                raise HTTPException(status_code=404, detail="Logo not found")
        
        @self.app.get("/mcp/manifest")
        async def mcp_manifest():
            """MCP Manifest endpoint - server capabilities and info"""
            return {
                "name": self.mcp_server.server_name,
                "version": self.mcp_server.server_version,
                "description": self.mcp_server.description,
                "protocol_version": "2025-06-18",
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    },
                    "resources": {},
                    "prompts": {},
                    "logging": {}
                },
                "tools": [
                    {
                        "name": tool_name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
                    for tool_name, tool in self.mcp_server._tools.items()
                ]
            }

        # MCP Protocol endpoints
        @self.app.post("/mcp/initialize")
        async def mcp_initialize(request: Request):
            """MCP Initialize endpoint"""
            try:
                body = await request.json()
                response = await self.mcp_server.handle_initialize(body)
                return response
            except Exception as e:
                logger.error(f"Initialize error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/mcp/tools/list")
        async def mcp_list_tools(request: Request):
            """MCP Tools List endpoint"""
            try:
                body = await request.json()
                response = await self.mcp_server.handle_tools_list(body)
                return response
            except Exception as e:
                logger.error(f"List tools error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/mcp/tools/call")
        async def mcp_call_tool(request: Request):
            """MCP Tool Call endpoint"""
            try:
                body = await request.json()
                response = await self.mcp_server.handle_tools_call(body)
                return response
            except Exception as e:
                logger.error(f"Tool call error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # MCP Protocol endpoints are above - removed SSE endpoints for standard compliance
        
        # JSON-RPC 2.0 endpoint for MCP protocol compliance  
        @self.app.post("/jsonrpc")
        async def jsonrpc_handler(request: Request):
            """JSON-RPC 2.0 endpoint for MCP protocol with connection persistence"""
            body = None
            try:
                # Log incoming connection
                client_ip = request.client.host if request.client else "unknown"
                logger.debug(f"JSON-RPC request from {client_ip}")
                
                body = await request.json()
                
                # Handle ping method for connection testing
                if body.get("method") == "ping":
                    return {
                        "jsonrpc": "2.0",
                        "result": {"pong": True, "timestamp": time.time()},
                        "id": body.get("id")
                    }
                
                # Process request through MCP server
                response = await self.mcp_server.handle_jsonrpc(body)
                
                # Log successful processing
                method = body.get("method", "unknown")
                logger.debug(f"Processed {method} successfully")
                
                return response
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": "Parse error",
                        "data": str(e)
                    },
                    "id": None
                }
            except Exception as e:
                logger.error(f"JSON-RPC error: {e}")
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": str(e)
                    },
                    "id": body.get("id") if isinstance(body, dict) else None
                }
        
        # WebSocket endpoint for persistent connections
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for persistent MCP connections"""
            await websocket.accept()
            client_ip = websocket.client.host if websocket.client else "unknown"
            logger.info(f"WebSocket connection opened from {client_ip}")
            
            try:
                while True:
                    # Receive message from client
                    data = await websocket.receive_text()
                    logger.debug(f"WebSocket received: {data[:100]}...")
                    
                    try:
                        # Parse and process JSON-RPC message
                        body = json.loads(data)
                        
                        # Handle ping for connection testing
                        if body.get("method") == "ping":
                            response = {
                                "jsonrpc": "2.0",
                                "result": {"pong": True, "timestamp": time.time()},
                                "id": body.get("id")
                            }
                        else:
                            # Process through MCP server
                            response = await self.mcp_server.handle_jsonrpc(body)
                        
                        # Send response back
                        await websocket.send_text(json.dumps(response))
                        logger.debug(f"WebSocket sent response for {body.get('method', 'unknown')}")
                        
                    except json.JSONDecodeError as e:
                        error_response = {
                            "jsonrpc": "2.0",
                            "error": {
                                "code": -32700,
                                "message": "Parse error",
                                "data": str(e)
                            },
                            "id": None
                        }
                        await websocket.send_text(json.dumps(error_response))
                        
                    except Exception as e:
                        logger.error(f"WebSocket processing error: {e}")
                        error_response = {
                            "jsonrpc": "2.0",
                            "error": {
                                "code": -32603,
                                "message": "Internal error",
                                "data": str(e)
                            },
                            "id": None
                        }
                        await websocket.send_text(json.dumps(error_response))
                        
            except WebSocketDisconnect:
                logger.info(f"WebSocket connection closed from {client_ip}")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                try:
                    await websocket.close()
                except:
                    pass
    
    async def start_server(self):
        """Start the MCP server"""
        logger.info(f"Starting MCP Server on {self.host}:{self.port}")
        logger.info("Available endpoints:")
        logger.info("  - GET  /                 - Server info")
        logger.info("  - GET  /health           - Health check")
        logger.info("  - GET  /api/version      - API version info")
        logger.info("  - GET  /api/status       - Connection status")  
        logger.info("  - GET  /api/ping         - Ping test")
        logger.info("  - GET  /mcp/manifest     - MCP manifest")
        logger.info("  - POST /mcp/initialize   - MCP Initialize")
        logger.info("  - POST /mcp/tools/list   - MCP List Tools")
        logger.info("  - POST /mcp/tools/call   - MCP Call Tool")
        logger.info("  - POST /call             - LM Studio Tool Call")
        logger.info("  - POST /<tool_name>      - Direct Tool Call")
        logger.info("  - POST /jsonrpc          - JSON-RPC 2.0")
        logger.info("  - WS   /ws               - WebSocket connection") 
        logger.info("  - GET  /events           - LM Studio SSE Stream")
        logger.info("  - GET  /stream           - Alternative Stream")
        logger.info("  - GET  /sse/tools        - SSE Tools Stream")
        logger.info("  - GET  /sse/status       - SSE Status Stream")
        logger.info("  - GET  /tools            - Tools Discovery")
        logger.info("  - GET  /docs             - API Documentation")
        
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OCR PDF MCP Server")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run server
    server_runner = MCPServerRunner(host=args.host, port=args.port)
    
    try:
        asyncio.run(server_runner.start_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()