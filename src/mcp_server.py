#!/usr/bin/env python3
"""
MCP Server Core Implementation

Standard MCP Protocol 2025-06-18 compliant server with proper endpoints,
error handling, and tool management.
"""

import asyncio
import json
import logging
import traceback
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import asdict
import time

from .mcp_types import (
    MCP_PROTOCOL_VERSION, MCPServerState, MCPError, MCPRequestId, MCPParams,
    JSONRPCRequest, JSONRPCResponse, JSONRPCNotification,
    MCPInitializeRequest, MCPInitializeResponse, MCPCapabilities, MCPImplementation,
    MCPTool, MCPToolsListResponse, MCPToolCallRequest, MCPToolCallResponse,
    MCPContent, MCPTextContent, MCPToolResult,
    create_jsonrpc_response, create_text_content, create_tool_result,
    validate_protocol_version, validate_jsonrpc_version
)

# Setup logging
logger = logging.getLogger(__name__)

class MCPServer:
    """
    Standard MCP Protocol Server Implementation
    
    Implements MCP Protocol 2025-06-18 with proper:
    - JSON-RPC 2.0 compliance
    - Standard endpoint structure
    - Error handling with MCP error codes
    - Tool management and execution
    """
    
    def __init__(self, 
                 server_name: str = "MCP Server",
                 server_version: str = "1.0.0",
                 description: Optional[str] = None):
        self.server_name = server_name
        self.server_version = server_version
        self.description = description
        
        # Server state
        self.state = MCPServerState.UNINITIALIZED
        self.client_capabilities: Optional[MCPCapabilities] = None
        self.server_capabilities = MCPCapabilities(
            tools={"listChanged": True},
            resources={},
            prompts={},
            logging={}
        )
        
        # Tool registry
        self._tools: Dict[str, MCPTool] = {}
        self._tool_handlers: Dict[str, Callable] = {}
        
        # Method handlers registry
        self._method_handlers: Dict[str, Callable] = {}
        self._register_standard_handlers()
        
        logger.info(f"MCP Server initialized: {server_name} v{server_version}")
    
    def _register_standard_handlers(self):
        """Register standard MCP protocol method handlers"""
        self._method_handlers.update({
            "initialize": self._handle_initialize,
            "initialized": self._handle_initialized,
            "tools/list": self._handle_tools_list,
            "tools/call": self._handle_tools_call,
            "resources/list": self._handle_resources_list,
            "prompts/list": self._handle_prompts_list,
            "logging/setLevel": self._handle_logging_set_level,
            "ping": self._handle_ping
        })
    
    # Core Protocol Methods
    async def _handle_initialize(self, params: MCPParams, request_id: MCPRequestId) -> JSONRPCResponse:
        """Handle initialize request"""
        try:
            self.state = MCPServerState.INITIALIZING
            
            # Validate request parameters
            if not params:
                return create_jsonrpc_response(
                    error=MCPError.invalid_params("Missing initialize parameters"),
                    request_id=request_id
                )
            
            # Parse initialize request
            protocol_version = params.get("protocolVersion")
            capabilities = params.get("capabilities", {})
            client_info = params.get("clientInfo", {})
            
            # Validate protocol version
            if not protocol_version or not validate_protocol_version(protocol_version):
                return create_jsonrpc_response(
                    error=MCPError(
                        code=-32001,  # Initialize error
                        message=f"Unsupported protocol version: {protocol_version}",
                        data={"supported_version": MCP_PROTOCOL_VERSION}
                    ),
                    request_id=request_id
                )
            
            # Store client capabilities
            self.client_capabilities = MCPCapabilities(**capabilities)
            
            # Create response
            response = MCPInitializeResponse(
                protocolVersion=MCP_PROTOCOL_VERSION,
                capabilities=self.server_capabilities,
                serverInfo=MCPImplementation(
                    name=self.server_name,
                    version=self.server_version
                ),
                instructions=self.description
            )
            
            self.state = MCPServerState.INITIALIZED
            logger.info(f"Client initialized: {client_info.get('name', 'Unknown')} v{client_info.get('version', '?')}")
            
            return create_jsonrpc_response(result=asdict(response), request_id=request_id)
            
        except Exception as e:
            logger.error(f"Initialize error: {e}")
            self.state = MCPServerState.ERROR
            return create_jsonrpc_response(
                error=MCPError.internal_error(f"Initialize failed: {str(e)}"),
                request_id=request_id
            )
    
    async def _handle_initialized(self, params: MCPParams, request_id: MCPRequestId) -> Optional[JSONRPCResponse]:
        """Handle initialized notification (no response)"""
        logger.info("Client initialization complete")
        return None  # Notification - no response
    
    async def _handle_tools_list(self, params: MCPParams, request_id: MCPRequestId) -> JSONRPCResponse:
        """Handle tools/list request"""
        try:
            if self.state != MCPServerState.INITIALIZED:
                return create_jsonrpc_response(
                    error=MCPError(-32002, "Server not initialized"),
                    request_id=request_id
                )
            
            tools_list = list(self._tools.values())
            response = MCPToolsListResponse(tools=tools_list)
            
            logger.debug(f"Returning {len(tools_list)} tools")
            return create_jsonrpc_response(result=asdict(response), request_id=request_id)
            
        except Exception as e:
            logger.error(f"Tools list error: {e}")
            return create_jsonrpc_response(
                error=MCPError.internal_error(f"Failed to list tools: {str(e)}"),
                request_id=request_id
            )
    
    async def _handle_tools_call(self, params: MCPParams, request_id: MCPRequestId) -> JSONRPCResponse:
        """Handle tools/call request"""
        try:
            if self.state != MCPServerState.INITIALIZED:
                return create_jsonrpc_response(
                    error=MCPError(-32002, "Server not initialized"),
                    request_id=request_id
                )
            
            # Validate parameters
            if not params:
                return create_jsonrpc_response(
                    error=MCPError.invalid_params("Missing tool call parameters"),
                    request_id=request_id
                )
            
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if not tool_name:
                return create_jsonrpc_response(
                    error=MCPError.invalid_params("Missing tool name"),
                    request_id=request_id
                )
            
            # Check if tool exists
            if tool_name not in self._tools:
                return create_jsonrpc_response(
                    error=MCPError.tool_error(tool_name, "Tool not found"),
                    request_id=request_id
                )
            
            # Get tool handler
            handler = self._tool_handlers.get(tool_name)
            if not handler:
                return create_jsonrpc_response(
                    error=MCPError.tool_error(tool_name, "Tool handler not available"),
                    request_id=request_id
                )
            
            # Validate arguments against tool schema
            tool = self._tools[tool_name]
            validation_error = self._validate_tool_arguments(tool, arguments)
            if validation_error:
                return create_jsonrpc_response(
                    error=validation_error,
                    request_id=request_id
                )
            
            # Execute tool
            logger.info(f"Executing tool: {tool_name}")
            try:
                result = await self._execute_tool(handler, arguments)
                
                # Convert result to MCP format
                if isinstance(result, MCPToolResult):
                    response = MCPToolCallResponse(
                        content=result.content,
                        isError=result.isError
                    )
                else:
                    # Convert simple result to MCP content
                    content: List[MCPContent] = [create_text_content(str(result))]
                    response = MCPToolCallResponse(content=content, isError=False)
                
                return create_jsonrpc_response(result=asdict(response), request_id=request_id)
                
            except Exception as tool_error:
                logger.error(f"Tool execution error: {tool_error}")
                error_content: List[MCPContent] = [create_text_content(f"Tool execution failed: {str(tool_error)}")]
                response = MCPToolCallResponse(content=error_content, isError=True)
                return create_jsonrpc_response(result=asdict(response), request_id=request_id)
            
        except Exception as e:
            logger.error(f"Tools call error: {e}")
            return create_jsonrpc_response(
                error=MCPError.internal_error(f"Tool call failed: {str(e)}"),
                request_id=request_id
            )
    
    async def _handle_resources_list(self, params: MCPParams, request_id: MCPRequestId) -> JSONRPCResponse:
        """Handle resources/list request"""
        # Default implementation - no resources
        return create_jsonrpc_response(result={"resources": []}, request_id=request_id)
    
    async def _handle_prompts_list(self, params: MCPParams, request_id: MCPRequestId) -> JSONRPCResponse:
        """Handle prompts/list request"""
        # Default implementation - no prompts
        return create_jsonrpc_response(result={"prompts": []}, request_id=request_id)
    
    async def _handle_logging_set_level(self, params: MCPParams, request_id: MCPRequestId) -> JSONRPCResponse:
        """Handle logging/setLevel request"""
        level = params.get("level", "info") if params else "info"
        # Set logging level (implementation specific)
        logger.info(f"Logging level set to: {level}")
        return create_jsonrpc_response(result={}, request_id=request_id)
    
    async def _handle_ping(self, params: MCPParams, request_id: MCPRequestId) -> JSONRPCResponse:
        """Handle ping request"""
        return create_jsonrpc_response(result={"pong": True}, request_id=request_id)
    
    # Tool Management
    def register_tool(self, tool: MCPTool, handler: Callable) -> bool:
        """Register a tool with its handler"""
        try:
            self._tools[tool.name] = tool
            self._tool_handlers[tool.name] = handler
            logger.info(f"Tool registered: {tool.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register tool {tool.name}: {e}")
            return False
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool"""
        try:
            if tool_name in self._tools:
                del self._tools[tool_name]
            if tool_name in self._tool_handlers:
                del self._tool_handlers[tool_name]
            logger.info(f"Tool unregistered: {tool_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to unregister tool {tool_name}: {e}")
            return False
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get tool definition"""
        return self._tools.get(tool_name)
    
    def list_tools(self) -> List[MCPTool]:
        """List all registered tools"""
        return list(self._tools.values())
    
    # Request Processing
    async def process_request(self, request_data: str) -> Optional[str]:
        """Process JSON-RPC request and return response"""
        try:
            # Parse JSON
            try:
                request_json = json.loads(request_data)
            except json.JSONDecodeError as e:
                error_response = create_jsonrpc_response(
                    error=MCPError.parse_error({"details": str(e)})
                )
                return json.dumps(asdict(error_response))
            
            # Handle batch requests
            if isinstance(request_json, list):
                responses = []
                for req in request_json:
                    response = await self._process_single_request(req)
                    if response:  # Notifications return None
                        responses.append(response)
                return json.dumps([asdict(r) for r in responses]) if responses else None
            else:
                response = await self._process_single_request(request_json)
                return json.dumps(asdict(response)) if response else None
            
        except Exception as e:
            logger.error(f"Request processing error: {e}")
            error_response = create_jsonrpc_response(
                error=MCPError.internal_error(f"Request processing failed: {str(e)}")
            )
            return json.dumps(asdict(error_response))
    
    async def _process_single_request(self, request_json: Dict) -> Optional[JSONRPCResponse]:
        """Process a single JSON-RPC request"""
        try:
            # Validate JSON-RPC format
            jsonrpc_version = request_json.get("jsonrpc", "")
            if not validate_jsonrpc_version(jsonrpc_version):
                return create_jsonrpc_response(
                    error=MCPError.invalid_request({"reason": "Invalid jsonrpc version"}),
                    request_id=request_json.get("id")
                )
            
            method = request_json.get("method")
            params = request_json.get("params")
            request_id = request_json.get("id")
            
            if not method:
                return create_jsonrpc_response(
                    error=MCPError.invalid_request({"reason": "Missing method"}),
                    request_id=request_id
                )
            
            # Get method handler
            handler = self._method_handlers.get(method)
            if not handler:
                return create_jsonrpc_response(
                    error=MCPError.method_not_found(method),
                    request_id=request_id
                )
            
            # Execute handler
            response = await handler(params, request_id)
            return response
            
        except Exception as e:
            logger.error(f"Single request processing error: {e}")
            return create_jsonrpc_response(
                error=MCPError.internal_error(str(e)),
                request_id=request_json.get("id")
            )
    
    # Utility Methods
    def _validate_tool_arguments(self, tool: MCPTool, arguments: Dict[str, Any]) -> Optional[MCPError]:
        """Validate tool arguments against schema"""
        try:
            schema = tool.inputSchema
            
            # Check required parameters
            for required_param in schema.required:
                if required_param not in arguments:
                    return MCPError.invalid_params(
                        f"Missing required parameter: {required_param}"
                    )
            
            # Check parameter types (basic validation)
            for param_name, param_value in arguments.items():
                if param_name in schema.properties:
                    param_schema = schema.properties[param_name]
                    if not self._validate_parameter_type(param_value, param_schema):
                        return MCPError.invalid_params(
                            f"Invalid type for parameter {param_name}"
                        )
            
            return None
            
        except Exception as e:
            return MCPError.invalid_params(f"Parameter validation error: {str(e)}")
    
    def _validate_parameter_type(self, value: Any, schema: Dict[str, Any]) -> bool:
        """Basic parameter type validation"""
        param_type = schema.get("type", "string")
        
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        expected_type = type_map.get(param_type)
        if expected_type:
            return isinstance(value, expected_type)
        
        return True  # Unknown type - allow
    
    async def _execute_tool(self, handler: Callable, arguments: Dict[str, Any]) -> Any:
        """Execute tool handler"""
        if asyncio.iscoroutinefunction(handler):
            return await handler(**arguments)
        else:
            return handler(**arguments)
    
    # Server Info
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return {
            "name": self.server_name,
            "version": self.server_version,
            "protocol_version": MCP_PROTOCOL_VERSION,
            "state": self.state.value,
            "capabilities": asdict(self.server_capabilities),
            "tools_count": len(self._tools)
        }
    
    # Public handler methods for HTTP endpoints
    async def handle_initialize(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Public handler for initialize endpoint"""
        request_id = body.get("id")
        params = body.get("params", {})
        response = await self._handle_initialize(params, request_id)
        return asdict(response)
    
    async def handle_tools_list(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Public handler for tools list endpoint"""
        request_id = body.get("id")
        params = body.get("params", {})
        response = await self._handle_tools_list(params, request_id)
        return asdict(response)
    
    async def handle_tools_call(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Public handler for tools call endpoint"""
        request_id = body.get("id")
        params = body.get("params", {})
        response = await self._handle_tools_call(params, request_id)
        return asdict(response)
    
    async def handle_jsonrpc(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Public handler for JSON-RPC endpoint"""
        if isinstance(body, list):
            # Batch request
            responses = []
            for request in body:
                response = await self._process_single_request(request)
                if response:
                    responses.append(asdict(response))
            return responses
        else:
            # Single request
            response = await self._process_single_request(body)
            return asdict(response) if response else {}
    
    def set_tools_registry(self, registry):
        """Set tools registry for the server"""
        self.tools_registry = registry