from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from pathlib import Path
@dataclass(frozen=True)
class KnowledgeHit:
    document_id:str; chunk_id:str; content:str; source:str; score:float
class KnowledgeIndex:
    def __init__(self,path:str|Path="data/knowledge/atlas.db"):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        with sqlite3.connect(self.path) as c:
            c.execute("CREATE TABLE IF NOT EXISTS chunks(document_id TEXT,chunk_id TEXT PRIMARY KEY,content TEXT,source TEXT,metadata TEXT)")
            try:c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(chunk_id UNINDEXED,content)")
            except sqlite3.OperationalError:pass
    def add(self,document_id:str,chunk_id:str,content:str,source:str,metadata:str="{}"):
        with sqlite3.connect(self.path) as c:
            c.execute("INSERT OR REPLACE INTO chunks VALUES(?,?,?,?,?)",(document_id,chunk_id,content,source,metadata))
            try:c.execute("DELETE FROM chunks_fts WHERE chunk_id=?",(chunk_id,));c.execute("INSERT INTO chunks_fts VALUES(?,?)",(chunk_id,content))
            except sqlite3.OperationalError:pass
    def search(self,query:str,limit:int=5):
        with sqlite3.connect(self.path) as c:
            try:
                rows=c.execute("SELECT c.document_id,c.chunk_id,c.content,c.source,bm25(chunks_fts) FROM chunks_fts JOIN chunks c USING(chunk_id) WHERE chunks_fts MATCH ? ORDER BY bm25(chunks_fts) LIMIT ?",(query,limit)).fetchall()
                return tuple(KnowledgeHit(r[0],r[1],r[2],r[3],-float(r[4])) for r in rows)
            except sqlite3.OperationalError:
                rows=c.execute("SELECT document_id,chunk_id,content,source FROM chunks WHERE content LIKE ? LIMIT ?",(f"%{query}%",limit)).fetchall()
                return tuple(KnowledgeHit(*r,1.0) for r in rows)
