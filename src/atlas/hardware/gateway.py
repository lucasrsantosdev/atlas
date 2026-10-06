from __future__ import annotations
from dataclasses import dataclass,field
from typing import Any
@dataclass
class Device: id:str;capabilities:frozenset[str];state:dict[str,Any]=field(default_factory=dict);healthy:bool=True
class HardwareGateway:
 def __init__(self):self.devices={}
 def register(self,d):self.devices[d.id]=d
 def capabilities(self):return frozenset(c for d in self.devices.values() if d.healthy for c in d.capabilities)
 def execute(self,device_id,capability,**args):
  d=self.devices[device_id]
  if not d.healthy:raise RuntimeError('device unavailable')
  if capability not in d.capabilities:raise ValueError('unsupported capability')
  if capability=='temperature.read':return d.state.get('temperature',25.0)
  if capability=='humidity.read':return d.state.get('humidity',50.0)
  if capability=='led.control':d.state['led']=bool(args.get('on'));return d.state['led']
  if capability=='device.health':return d.healthy
  raise ValueError('unsupported capability')
def simulated_esp32(device_id='esp32-sim'):return Device(device_id,frozenset({'temperature.read','humidity.read','led.control','device.health'}),{'temperature':25.0,'humidity':50.0,'led':False})
