from __future__ import annotations
import json, sqlite3
from pathlib import Path
from atlas.memory.models import MemoryRecord, MemorySource, MemoryType, MemoryVerification
class SqliteMemoryStore:
    """Store local transacional com FTS5; fallback lexical continua disponível via LIKE."""
    def __init__(self, path: str|Path="data/memory/atlas.db") -> None:
        self.path=Path(path); self.path.parent.mkdir(parents=True, exist_ok=True); self._init()
    def _connect(self): return sqlite3.connect(self.path)
    def _init(self):
        with self._connect() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS memories(id TEXT PRIMARY KEY,memory_type TEXT,content TEXT,source TEXT,created_at TEXT,verification TEXT,confidence REAL,authorized INTEGER,tags TEXT,metadata TEXT,status TEXT DEFAULT 'active',valid_from TEXT,valid_until TEXT,supersedes TEXT)''')
            try: c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(id UNINDEXED, content, tags)")
            except sqlite3.OperationalError: pass
    def save(self,r:MemoryRecord)->None:
        if not r.authorized: raise ValueError("Memória não autorizada não pode ser persistida.")
        m=r.metadata
        with self._connect() as c:
            c.execute("INSERT OR REPLACE INTO memories VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(r.id,r.memory_type.value,r.content,r.source.value,r.created_at,r.verification.value,r.confidence,1,json.dumps(r.tags),json.dumps(m,ensure_ascii=False),m.get('status','active'),m.get('valid_from'),m.get('valid_until'),m.get('supersedes')))
            try:
                c.execute("DELETE FROM memories_fts WHERE id=?",(r.id,)); c.execute("INSERT INTO memories_fts VALUES(?,?,?)",(r.id,r.content," ".join(r.tags)))
            except sqlite3.OperationalError: pass
    def _record(self,row):
        return MemoryRecord(id=row[0],memory_type=MemoryType(row[1]),content=row[2],source=MemorySource(row[3]),created_at=row[4],verification=MemoryVerification(row[5]),confidence=row[6],authorized=bool(row[7]),tags=tuple(json.loads(row[8])),metadata=json.loads(row[9]))
    def get_by_id(self,memory_id:str):
        with self._connect() as c: row=c.execute("SELECT * FROM memories WHERE id=?",(memory_id,)).fetchone()
        return self._record(row) if row else None
    def search_text(self,query:str,*,memory_type:MemoryType|None=None,limit:int=10):
        q=f"%{query.strip()}%"; sql="SELECT * FROM memories WHERE status='active' AND content LIKE ?"; args=[q]
        if memory_type: sql+=" AND memory_type=?"; args.append(memory_type.value)
        sql+=" ORDER BY created_at DESC LIMIT ?"; args.append(limit)
        with self._connect() as c: rows=c.execute(sql,args).fetchall()
        return tuple(self._record(r) for r in rows)
    def search_tags(self,tags:tuple[str,...],*,memory_type=None,match_all=True,limit=10):
        records=self.recent(memory_type=memory_type,limit=1000); wanted={t.casefold() for t in tags}
        out=[r for r in records if (wanted <= {t.casefold() for t in r.tags} if match_all else bool(wanted & {t.casefold() for t in r.tags}))]
        return tuple(out[:limit])
    def recent(self,*,memory_type=None,limit=10):
        sql="SELECT * FROM memories WHERE status='active'"; args=[]
        if memory_type: sql+=" AND memory_type=?"; args.append(memory_type.value)
        sql+=" ORDER BY created_at DESC LIMIT ?"; args.append(limit)
        with self._connect() as c: rows=c.execute(sql,args).fetchall()
        return tuple(self._record(r) for r in rows)
