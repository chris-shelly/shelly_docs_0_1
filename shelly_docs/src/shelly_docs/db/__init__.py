import sqlite3
from typing import Optional, Union

def execute_query(conn: sqlite3.Connection, query: str, params: Optional[tuple]=None) -> list[dict]:
  print("query", query)
  cursor = conn.cursor()
  if params:
    cursor.execute(query, params)
  else:
    cursor.execute(query)
  results = cursor.fetchall()
  cursor.close()
  return [dict(row) for row in results]

def execute_query_many(conn: sqlite3.Connection, query: str, params: Union[list[dict], tuple[dict]]):
  print("query", query)
  cursor = conn.cursor()
  if params:
    cursor.executemany(query, params)
  else:
    cursor.executemany(query)
  results = cursor.fetchall()
  cursor.close()
  return [dict(row) for row in results]