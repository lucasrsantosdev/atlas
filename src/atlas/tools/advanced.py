from __future__ import annotations
import subprocess,sys
from pathlib import Path
from atlas.security import Permission,RiskLevel
from .registry import ToolManifest,ToolResult,ToolRegistry
def register_git(registry:ToolRegistry,root:str|Path):
 root=str(Path(root).resolve())
 def git(args):
  p=subprocess.run(['git',*args],cwd=root,text=True,capture_output=True,timeout=15);return ToolResult(p.returncode==0,(p.stdout or p.stderr).strip())
 registry.register(ToolManifest('git.status','Git status',Permission.GIT_READ,schema={'type':'object'}),lambda:git(['status','--short']))
 registry.register(ToolManifest('git.diff','Git diff',Permission.GIT_READ),lambda:git(['diff']))
 registry.register(ToolManifest('git.log','Git log',Permission.GIT_READ),lambda limit=10:git(['log',f'-{int(limit)}','--oneline']))
def register_python(registry:ToolRegistry):
 def run(code):
  p=subprocess.run([sys.executable,'-I','-c',code],text=True,capture_output=True,timeout=10);return ToolResult(p.returncode==0,(p.stdout or p.stderr).strip())
 registry.register(ToolManifest('python.execute','Isolated Python subprocess',Permission.EXECUTE_PROCESS,RiskLevel.HIGH,True,10),run)
