from __future__ import annotations
from atlas.security import Permission,RiskLevel
from atlas.tools import ToolManifest,ToolResult
class MCPToolAdapter:
 def __init__(self,client):self.client=client
 def install(self,registry,permission=Permission.NETWORK):
  for tool in self.client.discover_tools():
   name='mcp.'+tool.name
   def handler(_q=tool.name,**kwargs):return ToolResult(True,str(self.client.call(_q,**kwargs)))
   registry.register(ToolManifest(name,'MCP '+tool.name,permission,RiskLevel.MEDIUM,False,30,tool.input_schema),handler)
