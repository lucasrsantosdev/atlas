from __future__ import annotations
import hashlib,json,secrets
from dataclasses import dataclass
from datetime import datetime,timedelta,timezone
from enum import Enum
from pathlib import Path
from typing import Iterable

class Permission(str,Enum):
 READ_FILE='read_file';WRITE_FILE='write_file';NETWORK='network';EXECUTE_PROCESS='execute_process';DATABASE_READ='database_read';DATABASE_WRITE='database_write';GIT_READ='git_read';GIT_WRITE='git_write';HARDWARE_READ='hardware_read';HARDWARE_WRITE='hardware_write'
class RiskLevel(str,Enum):LOW='low';MEDIUM='medium';HIGH='high';CRITICAL='critical'
@dataclass(frozen=True)
class PolicyDecision: allowed:bool;risk:RiskLevel;requires_confirmation:bool;reason:str
@dataclass(frozen=True)
class ApprovalToken: token:str;permission:Permission;scope:str;expires_at:datetime

class AuditLog:
 """Append-only audit with a hash chain so accidental/tampered edits are detectable."""
 def __init__(self,path=None):self.path=Path(path) if path else None;self.events=[];self._last_hash='0'*64
 def record(self,**event):
  body={'at':datetime.now(timezone.utc).isoformat(),'previous_hash':self._last_hash,**event}
  digest=hashlib.sha256(json.dumps(body,sort_keys=True,default=str).encode()).hexdigest();item={**body,'hash':digest};self._last_hash=digest;self.events.append(item)
  if self.path:self.path.parent.mkdir(parents=True,exist_ok=True);open(self.path,'a',encoding='utf8').write(json.dumps(item,ensure_ascii=False)+'\n')
  return item
 def verify(self):
  prev='0'*64
  for item in self.events:
   body={k:v for k,v in item.items() if k!='hash'}
   if body.get('previous_hash')!=prev or hashlib.sha256(json.dumps(body,sort_keys=True,default=str).encode()).hexdigest()!=item['hash']:return False
   prev=item['hash']
  return True

class PolicyEngine:
 def __init__(self,allowed:Iterable[Permission]|None=None,audit=None,network_hosts=None,processes=None):
  self.allowed=set(allowed or ());self.audit=audit or AuditLog();self.network_hosts=set(network_hosts or ());self.processes=set(processes or ());self._approvals={}
 def evaluate(self,permission,risk=RiskLevel.LOW,*,scope='*'):
  permitted=permission in self.allowed;confirm=permitted and risk in {RiskLevel.HIGH,RiskLevel.CRITICAL}
  reason='permission granted' if permitted else 'permission denied (deny-by-default)'
  d=PolicyDecision(permitted,risk,confirm,reason);self.audit.record(event='policy',permission=permission.value,risk=risk.value,scope=scope,allowed=permitted,requires_confirmation=confirm);return d
 def issue_approval(self,permission,scope='*',ttl_seconds=60):
  if permission not in self.allowed:raise PermissionError('cannot approve denied permission')
  token=ApprovalToken(secrets.token_urlsafe(24),permission,scope,datetime.now(timezone.utc)+timedelta(seconds=ttl_seconds));self._approvals[token.token]=token;self.audit.record(event='approval_issued',permission=permission.value,scope=scope);return token.token
 def consume_approval(self,token,permission,scope='*'):
  a=self._approvals.pop(token,None);ok=bool(a and a.permission==permission and a.expires_at>=datetime.now(timezone.utc) and (a.scope=='*' or a.scope==scope));self.audit.record(event='approval_consumed',permission=permission.value,scope=scope,allowed=ok);return ok
 def host_allowed(self,host):return not self.network_hosts or host in self.network_hosts
 def process_allowed(self,process):return not self.processes or process in self.processes
