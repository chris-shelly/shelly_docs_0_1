from pathlib import Path
from .kb import get_kb_db_ro, get_kb_db
from ..db import execute_query

def sql_query(kb_path: Path, query: str) -> list[dict]:
  conn = get_kb_db_ro(kb_path)
  results = execute_query(conn, query)
  conn.close()
  return results