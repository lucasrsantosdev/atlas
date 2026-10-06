from __future__ import annotations
import json, sqlite3, math, re
from datetime import datetime, timezone
from pathlib import Path
from atlas.memory.models import MemoryRecord, MemorySource, MemoryType, MemoryVerification

def _terms(s): return set(re.findall(r'\w+',s.casefold(),re.UNICODE))
def _recency(created):
    try: days=max(0,(datetime.now(timezone.utc)-datetime.fromisoformat(created)).total_seconds()/86400); return math.exp(-days/180)
    except Exception:return .5
class SqliteMemoryStore:
    def __init__(self,path:str|Path='data/memory/atlas.db')->None:self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True);self._init()
    def _connect(self):return sqlite3.connect(self.path)
    def _init(self):
        with self._connect() as c:
            c.execute("CREATE TABLE IF NOT EXISTS memories(id TEXT PRIMARY KEY,memory_type TEXT,content TEXT,source TEXT,created_at TEXT,verification TEXT,confidence REAL,authorized INTEGER,tags TEXT,metadata TEXT,status TEXT DEFAULT 'active',valid_from TEXT,valid_until TEXT,supersedes TEXT)")
            try:c.execute('CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(id UNINDEXED,content,tags)')
            except sqlite3.OperationalError:pass
    def save(self,r):
        if not r.authorized:raise ValueError('Memória não autorizada não pode ser persistida.')
        m=r.metadata
        with self._connect() as c:
            c.execute('INSERT OR REPLACE INTO memories VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(r.id,r.memory_type.value,r.content,r.source.value,r.created_at,r.verification.value,r.confidence,1,json.dumps(r.tags),json.dumps(m,ensure_ascii=False),m.get('status','active'),m.get('valid_from'),m.get('valid_until'),m.get('supersedes')))
            try:c.execute('DELETE FROM memories_fts WHERE id=?',(r.id,));c.execute('INSERT INTO memories_fts VALUES(?,?,?)',(r.id,r.content,' '.join(r.tags)))
            except sqlite3.OperationalError:pass
    def _record(self,row):return MemoryRecord(id=row[0],memory_type=MemoryType(row[1]),content=row[2],source=MemorySource(row[3]),created_at=row[4],verification=MemoryVerification(row[5]),confidence=row[6],authorized=bool(row[7]),tags=tuple(json.loads(row[8])),metadata=json.loads(row[9]))
    def get_by_id(self,memory_id):
        with self._connect() as c:row=c.execute('SELECT * FROM memories WHERE id=?',(memory_id,)).fetchone()
        return self._record(row) if row else None
    def search_text(self,query,*,memory_type=None,limit=10):
        sql="SELECT * FROM memories WHERE status='active'";args=[]
        if memory_type:sql+=' AND memory_type=?';args.append(memory_type.value)
        with self._connect() as c:
            rows=c.execute(sql,args).fetchall(); fts={}
            try:
                for rid,rank in c.execute("SELECT id,bm25(memories_fts) FROM memories_fts WHERE memories_fts MATCH ? LIMIT 100",(query,)): fts[rid]=1/(1+abs(float(rank)))
            except sqlite3.OperationalError: pass
        qt=_terms(query); ranked=[]
        for row in rows:
            r=self._record(row); terms=_terms(r.content+' '+' '.join(r.tags)); lexical=len(qt&terms)/max(1,len(qt)); importance=float(r.metadata.get('importance',.5)); score=.25*lexical+.20*fts.get(r.id,0.0)+.20*_recency(r.created_at)+.20*r.confidence+.15*importance
            if lexical>0 or query.casefold() in r.content.casefold():ranked.append((score,r))
        return tuple(r for _,r in sorted(ranked,key=lambda x:x[0],reverse=True)[:limit])
    def supersede(self,old_id,new_record):
        self.save(new_record)
        with self._connect() as c:c.execute("UPDATE memories SET status='superseded' WHERE id=?",(old_id,))
    def forget(self,memory_id):
        with self._connect() as c:c.execute("UPDATE memories SET status='forgotten' WHERE id=?",(memory_id,))
    def search_tags(self,tags,*,memory_type=None,match_all=True,limit=10):
        records=self.recent(memory_type=memory_type,limit=1000);wanted={t.casefold() for t in tags};out=[r for r in records if (wanted<={t.casefold() for t in r.tags} if match_all else bool(wanted&{t.casefold() for t in r.tags}))];return tuple(out[:limit])
    def recent(self,*,memory_type=None,limit=10):
        sql="SELECT * FROM memories WHERE status='active'";args=[]
        if memory_type:sql+=' AND memory_type=?';args.append(memory_type.value)
        sql+=' ORDER BY created_at DESC LIMIT ?';args.append(limit)
        with self._connect() as c:rows=c.execute(sql,args).fetchall()
        return tuple(self._record(r) for r in rows)

    def consolidate(self, limit=1000):
        records=self.recent(limit=limit);seen={};merged=[]
        for r in records:
            key=r.content.strip().casefold()
            if key in seen:
                self.forget(r.id);merged.append(r.id)
            else:seen[key]=r.id
        return tuple(merged)
