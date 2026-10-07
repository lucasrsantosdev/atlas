from __future__ import annotations
import subprocess,sys
from pathlib import Path
from atlas.security import Permission,RiskLevel
from .registry import ToolManifest,ToolResult,ToolRegistry

def _safe_root(root):return Path(root).resolve()
def register_git(registry:ToolRegistry,root:str|Path):
 root=_safe_root(root)
 def git(args):
  p=subprocess.run(['git',*args],cwd=root,text=True,capture_output=True,timeout=15,shell=False);return ToolResult(p.returncode==0,(p.stdout or p.stderr).strip())
 registry.register(ToolManifest('git.status','Git status',Permission.GIT_READ,schema={'type':'object'}),lambda:git(['status','--short']))
 registry.register(ToolManifest('git.diff','Git diff',Permission.GIT_READ),lambda:git(['diff']))
 registry.register(ToolManifest('git.log','Git log',Permission.GIT_READ,schema={'type':'object','properties':{'limit':{'type':'integer'}}}),lambda limit=10:git(['log',f'-{max(1,min(int(limit),100))}','--oneline']))
 registry.register(ToolManifest('git.show','Git show',Permission.GIT_READ,schema={'type':'object','properties':{'ref':{'type':'string'}},'required':['ref']}),lambda ref:git(['show','--stat','--oneline','--',ref]) if ref.startswith('-') else git(['show','--stat','--oneline',ref]))

def register_python(registry:ToolRegistry):
 def run(code):
  p=subprocess.run([sys.executable,'-I','-c',code],text=True,capture_output=True,timeout=10,shell=False);return ToolResult(p.returncode==0,(p.stdout or p.stderr).strip())
 registry.register(ToolManifest('python.execute','Isolated Python subprocess',Permission.EXECUTE_PROCESS,RiskLevel.HIGH,True,10,{'type':'object','properties':{'code':{'type':'string'}},'required':['code']},False),run)
