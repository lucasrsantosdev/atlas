from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Any

@dataclass(frozen=True)
class MCPTool:
    name:str; description:str=''; input_schema:dict[str,Any]=field(default_factory=dict)
@dataclass
class MCPServer:
    name:str; tools:dict[str,Callable[...,Any]]=field(default_factory=dict); healthy:bool=True
class MCPClient:
    """Transport-neutral MCP facade. Real transports can implement the same contract."""
    def __init__(self):self._servers={}
    def register_server(self,server:MCPServer):self._servers[server.name]=server
    def health(self):return {n:s.healthy for n,s in self._servers.items()}
    def discover_tools(self):return tuple(MCPTool(f'{n}.{t}') for n,s in self._servers.items() if s.healthy for t in s.tools)
    def call(self,qualified_name:str,**arguments):
        server_name,tool_name=qualified_name.split('.',1);server=self._servers[server_name]
        if not server.healthy:raise RuntimeError(f'MCP server unavailable: {server_name}')
        return server.tools[tool_name](**arguments)
