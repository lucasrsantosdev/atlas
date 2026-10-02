from __future__ import annotations
from pathlib import Path
from atlas.security import Permission, RiskLevel
from .registry import ToolManifest, ToolRegistry, ToolResult
def register_safe_filesystem(registry:ToolRegistry,root:str|Path)->None:
    root=Path(root).resolve()
    def resolve(path:str)->Path:
        target=(root/path).resolve()
        if target!=root and root not in target.parents: raise ValueError("path escapes allowed workspace")
        return target
    registry.register(ToolManifest("filesystem.read","Read UTF-8 text inside workspace",Permission.READ_FILE),lambda path:ToolResult(True,resolve(path).read_text(encoding="utf-8")))
    def write(path:str,content:str):
        target=resolve(path);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(content,encoding="utf-8");return ToolResult(True,str(target))
    registry.register(ToolManifest("filesystem.write","Write UTF-8 text inside workspace",Permission.WRITE_FILE,RiskLevel.HIGH,True),write)
