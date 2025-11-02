#!/usr/bin/env python3
"""
MCP Protocol Types and Interfaces

Standard types dan interfaces untuk MCP Protocol 2025-06-18 compliance.
Berdasarkan specification: https://spec.modelcontextprotocol.io/
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Literal, cast
from enum import Enum
import time

# MCP Protocol Version
MCP_PROTOCOL_VERSION = "2025-06-18"

# Standard Error Codes (JSON-RPC 2.0 + MCP extensions)
class MCPErrorCode(Enum):
    # JSON-RPC 2.0 Standard Errors
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    
    # MCP Protocol Specific Errors
    INITIALIZE_ERROR = -32001
    PROTOCOL_ERROR = -32002
    TOOL_ERROR = -32003
    RESOURCE_ERROR = -32004
    PROMPT_ERROR = -32005

@dataclass
class MCPError:
    """Standard MCP Error Response"""
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None
    
    @classmethod
    def parse_error(cls, data: Optional[Dict] = None) -> 'MCPError':
        return cls(MCPErrorCode.PARSE_ERROR.value, "Parse error", data)
    
    @classmethod
    def invalid_request(cls, data: Optional[Dict] = None) -> 'MCPError':
        return cls(MCPErrorCode.INVALID_REQUEST.value, "Invalid Request", data)
    
    @classmethod
    def method_not_found(cls, method: str) -> 'MCPError':
        return cls(MCPErrorCode.METHOD_NOT_FOUND.value, "Method not found", {"method": method})
    
    @classmethod
    def invalid_params(cls, message: str = "Invalid params") -> 'MCPError':
        return cls(MCPErrorCode.INVALID_PARAMS.value, message)
    
    @classmethod
    def internal_error(cls, message: str = "Internal error") -> 'MCPError':
        return cls(MCPErrorCode.INTERNAL_ERROR.value, message)
    
    @classmethod
    def tool_error(cls, tool_name: str, message: str) -> 'MCPError':
        return cls(MCPErrorCode.TOOL_ERROR.value, f"Tool error: {message}", {"tool": tool_name})

# JSON-RPC 2.0 Message Types
@dataclass
class JSONRPCRequest:
    """Standard JSON-RPC 2.0 Request"""
    jsonrpc: Literal["2.0"] = "2.0"
    method: str = ""
    params: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None

@dataclass
class JSONRPCResponse:
    """Standard JSON-RPC 2.0 Response"""
    jsonrpc: Literal["2.0"] = "2.0"
    id: Optional[Union[str, int]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

@dataclass
class JSONRPCNotification:
    """JSON-RPC 2.0 Notification (no response expected)"""
    jsonrpc: Literal["2.0"] = "2.0"
    method: str = ""
    params: Optional[Dict[str, Any]] = None

# MCP Protocol Core Types
@dataclass
class MCPCapabilities:
    """MCP Server/Client Capabilities"""
    tools: Optional[Dict[str, Any]] = None
    resources: Optional[Dict[str, Any]] = None
    prompts: Optional[Dict[str, Any]] = None
    logging: Optional[Dict[str, Any]] = None

@dataclass
class MCPImplementation:
    """MCP Implementation Information"""
    name: str
    version: str

@dataclass
class MCPInitializeRequest:
    """MCP Initialize Request Parameters"""
    protocolVersion: str
    capabilities: MCPCapabilities
    clientInfo: MCPImplementation

@dataclass
class MCPInitializeResponse:
    """MCP Initialize Response"""
    protocolVersion: str
    capabilities: MCPCapabilities
    serverInfo: MCPImplementation
    instructions: Optional[str] = None

# Tool Types
@dataclass
class MCPToolParameter:
    """MCP Tool Parameter Definition"""
    type: str
    description: Optional[str] = None
    enum: Optional[List[str]] = None
    default: Optional[Any] = None
    required: bool = True

@dataclass
class MCPToolInputSchema:
    """MCP Tool Input Schema (JSON Schema)"""
    type: Literal["object"] = "object"
    properties: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)
    additionalProperties: bool = False

@dataclass
class MCPTool:
    """MCP Tool Definition"""
    name: str
    description: str
    inputSchema: MCPToolInputSchema

@dataclass
class MCPToolsListResponse:
    """Response for tools/list"""
    tools: List[MCPTool]

@dataclass
class MCPToolCallRequest:
    """Parameters for tools/call"""
    name: str
    arguments: Dict[str, Any]

@dataclass
class MCPTextContent:
    """MCP Text Content"""
    text: str
    type: Literal["text"] = "text"

@dataclass
class MCPImageContent:
    """MCP Image Content"""
    data: str  # base64 encoded
    mimeType: str
    type: Literal["image"] = "image"

@dataclass
class MCPResourceContent:
    """MCP Resource Content"""
    resource: Dict[str, Any]
    type: Literal["resource"] = "resource"

# Union of all content types
MCPContent = Union[MCPTextContent, MCPImageContent, MCPResourceContent]

@dataclass
class MCPToolResult:
    """Tool execution result"""
    content: List[MCPContent] = field(default_factory=list)
    isError: bool = False

@dataclass
class MCPToolCallResponse:
    """Response for tools/call"""
    content: List[MCPContent] = field(default_factory=list)
    isError: bool = False

# Resource Types
@dataclass
class MCPResource:
    """MCP Resource Definition"""
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None

@dataclass
class MCPResourcesListResponse:
    """Response for resources/list"""
    resources: List[MCPResource]

# Prompt Types
@dataclass
class MCPPromptArgument:
    """MCP Prompt Argument"""
    name: str
    description: str
    required: bool = True

@dataclass
class MCPPrompt:
    """MCP Prompt Definition"""
    name: str
    description: str
    arguments: List[MCPPromptArgument] = field(default_factory=list)

@dataclass
class MCPPromptsListResponse:
    """Response for prompts/list"""
    prompts: List[MCPPrompt]

# Logging Types
class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    ALERT = "alert"
    EMERGENCY = "emergency"

@dataclass
class MCPLogEntry:
    """MCP Log Entry"""
    level: LogLevel
    data: Any
    logger: Optional[str] = None

# Server State
class MCPServerState(Enum):
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    ERROR = "error"

# Utility Functions
def create_jsonrpc_request(method: str, params: Optional[Dict] = None, request_id: Optional[Union[str, int]] = None) -> JSONRPCRequest:
    """Create a standard JSON-RPC request"""
    return JSONRPCRequest(method=method, params=params, id=request_id)

def create_jsonrpc_response(result: Any = None, error: Optional[MCPError] = None, request_id: Optional[Union[str, int]] = None) -> JSONRPCResponse:
    """Create a standard JSON-RPC response"""
    error_dict = None
    if error:
        error_dict = {
            "code": error.code,
            "message": error.message,
            "data": error.data
        }
    
    return JSONRPCResponse(id=request_id, result=result, error=error_dict)

def create_text_content(text: str) -> MCPTextContent:
    """Create MCP text content"""
    return MCPTextContent(text=text)

def create_tool_result(content: List[MCPContent], is_error: bool = False) -> MCPToolResult:
    """Create MCP tool result"""
    return MCPToolResult(content=content, isError=is_error)

def create_tool_result_from_text_list(content: List[MCPTextContent], is_error: bool = False) -> MCPToolResult:
    """Create MCP tool result from text content list with proper type casting"""
    # Cast to List[MCPContent] since MCPTextContent is a valid MCPContent type
    content_list: List[MCPContent] = cast(List[MCPContent], content)
    return MCPToolResult(content=content_list, isError=is_error)

# Validation Functions
def validate_protocol_version(version: str) -> bool:
    """Validate MCP protocol version"""
    return version == MCP_PROTOCOL_VERSION

def validate_jsonrpc_version(version: str) -> bool:
    """Validate JSON-RPC version"""
    return version == "2.0"

# Type Aliases for clarity
MCPRequestId = Union[str, int, None]
MCPParams = Dict[str, Any]
MCPResult = Any