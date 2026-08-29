"""
Initialize the Knowledge Base
- create database if it's not already created
- create tables if they are not already created
"""

from pathlib import Path
import sqlite3
from rich import print
from ..db import execute_query

def init_kb(path: Path):
  print("---init_kb---")
  db_path = path / "kb.db"
  conn = sqlite3.connect(db_path)
  conn.row_factory = sqlite3.Row
  execute_query(
    conn,
    "CREATE TABLE items(key, name, parent, data, content, document, type, uuid, start_line, end_line)"
  )
  execute_query(
    conn,
    "CREATE TABLE item_ids(stem, next)"
  )
  execute_query(
    conn,
    "CREATE TABLE item_types(type)"
  )
  execute_query(
    conn,
    "CREATE TABLE jobs(name, type, script, active, item_types, query)"
  )
  return conn
