from pathlib import Path
from atlas.hardware import HardwareGateway,simulated_esp32
from atlas.integrations.mcp import MCPClient,MCPServer,MCPToolAdapter
from atlas.models.router import ModelRouter
from atlas.models.runtime import GenerationResult,ModelRequest,ModelRuntime,RuntimeHealth
from atlas.security import Permission,PolicyEngine
from atlas.tools import ToolRegistry
class Fake(ModelRuntime):
 def __init__(self,name='fake',fail=False):self.name=name;self.fail=fail
 @property
 def provider(self):return self.name
 def health(self):return RuntimeHealth(True,self.name,'ok')
 def generate(self,model,prompt,*,system_prompt=None):
  if self.fail:raise RuntimeError('boom')
  return GenerationResult(model,'ok',self.name)
def test_model_capability_fallback():
 r=ModelRouter(retries=0);r.register(role='bad',model_name='x',runtime=Fake('bad',True),capabilities={'reasoning'},priority=1);r.register(role='good',model_name='y',runtime=Fake('good'),capabilities={'reasoning'},priority=2)
 assert r.generate_request(ModelRequest('hi')).provider=='good'
def test_local_only_filters_remote():
 r=ModelRouter();r.register(role='remote',model_name='x',runtime=Fake(),capabilities={'reasoning'},local=False);r.register(role='local',model_name='y',runtime=Fake('local'),capabilities={'reasoning'},local=True)
 assert r.generate_request(ModelRequest('x',privacy='local_only')).provider=='local'
def test_mcp_adapter_governed_by_policy():
 c=MCPClient();c.register_server(MCPServer('git',{'status':lambda:'clean'}));reg=ToolRegistry(PolicyEngine({Permission.NETWORK}));MCPToolAdapter(c).install(reg)
 assert reg.execute('mcp.git.status').output=='clean'
def test_hardware_simulator():
 g=HardwareGateway();g.register(simulated_esp32());assert g.execute('esp32-sim','temperature.read')==25.0;assert g.execute('esp32-sim','led.control',on=True) is True
