from atlas.agent import AgentLoop
from atlas.integrations.mcp import MCPClient, MCPServer
from atlas.knowledge import KnowledgeIndex
from atlas.memory import MemoryRecord, MemorySource, MemoryType, MemoryService
from atlas.memory.sqlite_store import SqliteMemoryStore
from atlas.mosaic import MosaicRequest, MosaicService, PlanRisk
from atlas.models import ModelRouter
from atlas.models.runtime import GenerationResult, ModelRuntime, RuntimeHealth
from atlas.observability import Trace

class FakeRuntime(ModelRuntime):
    @property
    def provider(self): return 'fake'
    def health(self): return RuntimeHealth(True,'fake','ok')
    def generate(self,model,prompt,*,system_prompt=None): return GenerationResult(model=model,response=prompt)

def test_execution_plan_is_bounded_and_risk_aware():
    p=MosaicService().plan(MosaicRequest('commit git changes'))
    assert p.risk is PlanRisk.HIGH and p.max_steps > 0 and p.max_retries >= 0

def test_memory_lifecycle_and_rank(tmp_path):
    store=SqliteMemoryStore(tmp_path/'m.db');svc=MemoryService(store=store)
    a=MemoryRecord.create(memory_type=MemoryType.SEMANTIC,content='Atlas uses persistent memory',source=MemorySource.USER,authorized=True,confidence=.9,metadata={'importance':.9})
    store.save(a); assert svc.recall_text('persistent memory')[0].id==a.id
    svc.forget(a.id); assert not svc.recall_text('persistent memory')

def test_hybrid_knowledge_has_citation(tmp_path):
    k=KnowledgeIndex(tmp_path/'k.db');k.add('d','c1','Atlas local persistent memory','guide.md',{'section':'memory'})
    hit=k.search('persistent memory')[0]; assert hit.citation=='guide.md#c1' and hit.score>0

def test_agent_retrieves_knowledge_and_traces(tmp_path):
    k=KnowledgeIndex(tmp_path/'k.db');k.add('d','c1','Atlas architecture fact','architecture.md')
    r=ModelRouter();r.register(role='primary',model_name='fake',runtime=FakeRuntime())
    out=AgentLoop(r,knowledge=k).run('What architecture fact?')
    assert 'architecture fact' in out.response and 'architecture.md#c1' in out.citations
    names={e['name'] for e in out.trace.events}; assert {'understand','plan','knowledge.retrieve','model.generate','evaluate'} <= names

def test_mcp_discovery_and_call():
    c=MCPClient();c.register_server(MCPServer('git',{'status':lambda repo:'clean:'+repo}))
    assert c.discover_tools()[0].name=='git.status'; assert c.call('git.status',repo='atlas')=='clean:atlas'

def test_trace_metrics():
    t=Trace();t.event('x',duration_ms=2.0);assert t.metrics()['duration_ms']==2.0
