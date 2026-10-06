from __future__ import annotations
import json
from dataclasses import dataclass,asdict
from datetime import datetime,timezone
from enum import Enum
from pathlib import Path
class Permission(str,Enum):
 READ_FILE='read_file';WRITE_FILE='write_file';NETWORK='network';EXECUTE_PROCESS='execute_process';DATABASE_READ='database_read';DATABASE_WRITE='database_write';GIT_READ='git_read';GIT_WRITE='git_write';HARDWARE_READ='hardware_read';HARDWARE_WRITE='hardware_write'
class RiskLevel(str,Enum):LOW='low';MEDIUM='medium';HIGH='high';CRITICAL='critical'
@dataclass(frozen=True)
class PolicyDecision: allowed:bool;risk:RiskLevel;requires_confirmation:bool;reason:str
class AuditLog:
 def __init__(self,path=None):self.path=Path(path) if path else None;self.events=[]
 def record(self,**event):
  item={'at':datetime.now(timezone.utc).isoformat(),**event};self.events.append(item)
  if self.path:self.path.parent.mkdir(parents=True,exist_ok=True);open(self.path,'a',encoding='utf8').write(json.dumps(item,ensure_ascii=False)+'\n')
class PolicyEngine:
 def __init__(self,allowed=None,audit=None):self.allowed=set(allowed or ());self.audit=audit or AuditLog()
 def evaluate(self,permission,risk=RiskLevel.LOW):
  permitted=permission in self.allowed;confirm=permitted and risk in {RiskLevel.HIGH,RiskLevel.CRITICAL};d=PolicyDecision(permitted,risk,confirm,'permission granted' if permitted else 'permission denied');self.audit.record(permission=permission.value,risk=risk.value,allowed=permitted,requires_confirmation=confirm);return d
