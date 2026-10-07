from __future__ import annotations
import time,uuid
from dataclasses import dataclass,field
from typing import Any,Protocol
@dataclass(frozen=True)
class HardwareMessage:
 protocol:str;device:str;request_id:str;capability:str;arguments:dict[str,Any]
@dataclass
class Device:
 id:str;capabilities:frozenset[str];state:dict[str,Any]=field(default_factory=dict);healthy:bool=True;last_heartbeat:float=field(default_factory=time.monotonic);protocol:str='atlas-hw/1'
class HardwareTransport(Protocol):
 def request(self,message:HardwareMessage)->Any:...
class SafetyController:
 def __init__(self):self.emergency_stopped=False
 def validate(self,capability,args):
  if self.emergency_stopped and capability not in {'device.health'}:raise PermissionError('hardware emergency stop active')
  if capability=='led.control' and not isinstance(args.get('on'),bool):raise ValueError('led.control requires boolean on')
  return True
 def emergency_stop(self):self.emergency_stopped=True
 def reset(self):self.emergency_stopped=False
class SimulatorTransport:
 def __init__(self,devices):self.devices=devices
 def request(self,m):
  d=self.devices[m.device]
  if not d.healthy:raise RuntimeError('device unavailable')
  if m.capability=='temperature.read':return d.state.get('temperature',25.0)
  if m.capability=='humidity.read':return d.state.get('humidity',50.0)
  if m.capability=='led.control':d.state['led']=m.arguments['on'];return d.state['led']
  if m.capability=='device.health':return {'healthy':d.healthy,'protocol':d.protocol}
  raise ValueError('unsupported capability')
class HardwareGateway:
 def __init__(self,safety=None,heartbeat_timeout=30.):self.devices={};self.safety=safety or SafetyController();self.heartbeat_timeout=heartbeat_timeout;self.transport=SimulatorTransport(self.devices)
 def register(self,d):self.devices[d.id]=d
 def heartbeat(self,device_id):d=self.devices[device_id];d.last_heartbeat=time.monotonic();d.healthy=True
 def sweep(self):
  now=time.monotonic()
  for d in self.devices.values():
   if now-d.last_heartbeat>self.heartbeat_timeout:d.healthy=False
 def reconnect(self,device_id):self.heartbeat(device_id);return True
 def capabilities(self):self.sweep();return frozenset(c for d in self.devices.values() if d.healthy for c in d.capabilities)
 def execute(self,device_id,capability,**args):
  self.sweep();d=self.devices[device_id]
  if not d.healthy:raise RuntimeError('device unavailable')
  if capability not in d.capabilities:raise ValueError('unsupported capability')
  self.safety.validate(capability,args);m=HardwareMessage(d.protocol,device_id,str(uuid.uuid4()),capability,args);return self.transport.request(m)
 def emergency_stop(self):self.safety.emergency_stop()
 def reset_emergency_stop(self):self.safety.reset()
def simulated_esp32(device_id='esp32-sim'):return Device(device_id,frozenset({'temperature.read','humidity.read','led.control','device.health'}),{'temperature':25.0,'humidity':50.0,'led':False})
