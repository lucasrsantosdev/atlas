from pathlib import Path
from atlas.capabilities import CapabilityProvider, CapabilityRegistry
from atlas.memory import MemoryRecord, MemorySource, MemoryType
from atlas.memory.sqlite_store import SqliteMemoryStore
from atlas.knowledge.index import KnowledgeIndex
from atlas.security import Permission, PolicyEngine, RiskLevel
from atlas.tools import ToolRegistry, register_safe_filesystem
from atlas.mosaic import IntentType, MosaicRequest, MosaicService

def test_capability_registry():
    r=CapabilityRegistry();r.register(CapabilityProvider("pc",frozenset({"filesystem.read","reasoning"})))
    assert r.has("reasoning") and r.providers_for("filesystem.read")[0].name=="pc"
def test_policy_requires_confirmation_for_high_risk():
    d=PolicyEngine({Permission.WRITE_FILE}).evaluate(Permission.WRITE_FILE,RiskLevel.HIGH)
    assert d.allowed and d.requires_confirmation
def test_sqlite_memory_roundtrip(tmp_path):
    s=SqliteMemoryStore(tmp_path/"m.db"); rec=MemoryRecord.create(memory_type=MemoryType.SEMANTIC,content="Atlas usa memória persistente",source=MemorySource.USER,authorized=True,tags=("atlas",));s.save(rec)
    assert s.get_by_id(rec.id)==rec and s.search_text("persistente")[0].id==rec.id
def test_knowledge_index(tmp_path):
    i=KnowledgeIndex(tmp_path/"k.db");i.add("doc","c1","Atlas possui conhecimento local","doc.md")
    assert i.search("conhecimento")[0].chunk_id=="c1"
def test_mosaic_is_now_functional():
    result=MosaicService().analyze(MosaicRequest("Execute os testes Python"));assert result.intent is IntentType.COMMAND

def test_filesystem_write_is_guarded(tmp_path):
    policy=PolicyEngine({Permission.READ_FILE,Permission.WRITE_FILE});tools=ToolRegistry(policy);register_safe_filesystem(tools,tmp_path)
    assert not tools.execute("filesystem.write",path="a.txt",content="x").success
    assert tools.execute("filesystem.write",confirmed=True,path="a.txt",content="x").success
    assert tools.execute("filesystem.read",path="a.txt").output=="x"
