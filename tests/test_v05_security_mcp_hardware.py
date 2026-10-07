from pathlib import Path
import time
from atlas.security import AuditLog,Permission,PolicyEngine,RiskLevel
from atlas.tools import ToolManifest,ToolRegistry
from atlas.integrations.mcp import MCPClient,MCPServer,MCPToolAdapter,InProcessTransport
from atlas.hardware import HardwareGateway,simulated_esp32

def test_security_deny_by_default_and_single_use_approval():
 p=PolicyEngine({Permission.WRITE_FILE})
 assert not p.evaluate(Permission.NETWORK).allowed
 r=ToolRegistry(p);r.register(ToolManifest('write','w',Permission.WRITE_FILE,RiskLevel.HIGH,True),lambda value:value)
 assert not r.execute('write',value='x').success
 token=p.issue_approval(Permission.WRITE_FILE,'write')
 assert r.execute('write',approval_token=token,value='x').success
 assert not r.execute('write',approval_token=token,value='x').success
 assert p.audit.verify()

def test_audit_hash_chain_detects_tamper():
 a=AuditLog();a.record(event='one');a.record(event='two');assert a.verify();a.events[0]['event']='evil';assert not a.verify()

def test_tool_schema_validation():
 p=PolicyEngine({Permission.READ_FILE});r=ToolRegistry(p);r.register(ToolManifest('x','x',Permission.READ_FILE,schema={'required':['name'],'properties':{'name':{'type':'string'}}}),lambda name:name)
 assert not r.execute('x').success
 assert not r.execute('x',name=3).success
 assert r.execute('x',name='ok').success

def test_mcp_lifecycle_adapter_and_policy():
 c=MCPClient();c.register_server(MCPServer('demo',transport=InProcessTransport({'echo':lambda text:text})))
 assert c.call('demo.echo',text='hi')=='hi';c.disconnect('demo')
 try:c.call('demo.echo',text='x');assert False
 except RuntimeError:pass
 c.reconnect('demo');p=PolicyEngine({Permission.NETWORK});r=ToolRegistry(p);MCPToolAdapter(c).install(r);assert r.execute('mcp.demo.echo',text='atlas').output=='atlas'
 c.unregister_server('demo');assert c.health()=={}

def test_hardware_protocol_safety_heartbeat_and_reconnect():
 g=HardwareGateway(heartbeat_timeout=.001);d=simulated_esp32();g.register(d)
 assert g.execute(d.id,'led.control',on=True) is True
 g.emergency_stop()
 try:g.execute(d.id,'led.control',on=False);assert False
 except PermissionError:pass
 assert g.execute(d.id,'device.health')['healthy'] is True
 g.reset_emergency_stop();time.sleep(.003);g.sweep();assert not d.healthy
 assert g.reconnect(d.id);assert g.execute(d.id,'temperature.read')==25.0
