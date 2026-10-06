from __future__ import annotations
import hashlib, json, math, re, sqlite3
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class KnowledgeHit:
    document_id:str; chunk_id:str; content:str; source:str; score:float; metadata:dict|None=None
    @property
    def citation(self)->str: return f'{self.source}#{self.chunk_id}'

def _tokens(text:str)->list[str]: return re.findall(r'\w+', text.casefold(), re.UNICODE)
def _embed(text:str,dims:int=128)->list[float]:
    v=[0.0]*dims
    for token in _tokens(text):
        h=int(hashlib.sha256(token.encode()).hexdigest(),16); v[h%dims]+=1.0 if (h>>8)&1 else -1.0
    n=math.sqrt(sum(x*x for x in v)) or 1.0
    return [x/n for x in v]
def _cos(a,b): return sum(x*y for x,y in zip(a,b))

class KnowledgeIndex:
    """Local hybrid lexical+semantic index; dependency-free embedding is replaceable."""
    def __init__(self,path:str|Path='data/knowledge/atlas.db'):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        with sqlite3.connect(self.path) as c:
            c.execute('CREATE TABLE IF NOT EXISTS chunks(document_id TEXT,chunk_id TEXT PRIMARY KEY,content TEXT,source TEXT,metadata TEXT,embedding TEXT)')
            cols={r[1] for r in c.execute('PRAGMA table_info(chunks)')}
            if 'embedding' not in cols:c.execute('ALTER TABLE chunks ADD COLUMN embedding TEXT')
            try:c.execute('CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(chunk_id UNINDEXED,content)')
            except sqlite3.OperationalError:pass
    def add(self,document_id,chunk_id,content,source,metadata='{}'):
        emb=json.dumps(_embed(content)); meta=metadata if isinstance(metadata,str) else json.dumps(metadata,ensure_ascii=False)
        with sqlite3.connect(self.path) as c:
            c.execute('INSERT OR REPLACE INTO chunks VALUES(?,?,?,?,?,?)',(document_id,chunk_id,content,source,meta,emb))
            try:c.execute('DELETE FROM chunks_fts WHERE chunk_id=?',(chunk_id,));c.execute('INSERT INTO chunks_fts VALUES(?,?)',(chunk_id,content))
            except sqlite3.OperationalError:pass
    def search(self,query,limit=5):
        lexical={}
        with sqlite3.connect(self.path) as c:
            try:
                for r in c.execute('SELECT chunk_id,bm25(chunks_fts) FROM chunks_fts WHERE chunks_fts MATCH ? LIMIT 50',(query,)): lexical[r[0]]=1/(1+abs(float(r[1])))
            except sqlite3.OperationalError: pass
            rows=c.execute('SELECT document_id,chunk_id,content,source,metadata,embedding FROM chunks').fetchall()
        q=_embed(query); hits=[]
        for d,cid,content,source,meta,emb in rows:
            semantic=max(0.0,_cos(q,json.loads(emb) if emb else _embed(content)))
            lexical_score=lexical.get(cid, 1.0 if query.casefold() in content.casefold() else 0.0)
            score=.65*semantic+.35*lexical_score
            if score>0:hits.append(KnowledgeHit(d,cid,content,source,score,json.loads(meta or '{}')))
        return tuple(sorted(hits,key=lambda h:h.score,reverse=True)[:limit])
    def build_context(self,query,limit=5):
        hits=self.search(query,limit); return '\n\n'.join(f'[{h.citation}] {h.content}' for h in hits), hits
