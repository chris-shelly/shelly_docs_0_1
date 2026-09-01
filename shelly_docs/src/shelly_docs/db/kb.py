"""
Initialize the Knowledge Base
- create database if it's not already created
- create tables if they are not already created
"""

from pathlib import Path
import sqlite3
from rich import print
from ..db import execute_query

# Column order matters: `_ensure_columns` appends missing columns with ALTER TABLE, so a
# migrated database only lines up with a freshly created one if this order is preserved.
TABLES = {
  "items": "key, name, parent, data, content, document, type, uuid, start_line, end_line, level",
  "item_keys": "key",
  "item_stems": "stem, next",
  "item_types": "type",
  "jobs": "name, type, script, active, item_types, query",
}

ITEMS_COLUMNS = [column.strip() for column in TABLES["items"].split(",")]

def _ensure_columns(conn: sqlite3.Connection, table: str, columns: list[str]) -> None:
  """
  Add any columns missing from an existing table.

  `init_kb` ignores the "table already exists" error, so a `kb.db` written by an older
  version of Shelly Docs keeps its original schema forever unless we ALTER it explicitly.
  """
  # PRAGMA on a table that doesn't exist returns an empty result set rather than raising
  existing = {row["name"] for row in execute_query(conn, f"PRAGMA table_info({table})")}
  if not existing:
    return # brand new database, the CREATE TABLE already made every column
  for column in columns:
    if column not in existing:
      execute_query(conn, f"ALTER TABLE {table} ADD COLUMN {column}")

def init_kb(path: Path, mode: str = "read_write"):
  """
  Create `kb.db` and its tables for the Knowledge Base at `path`.

  Safe to call repeatedly: existing tables are left alone, and an `items` table from an
  earlier schema has its missing columns added.
  """
  if mode == "read_write":
    db_path = path / "kb.db"
  
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    for table, columns in TABLES.items():
      try:
        execute_query(conn, f"CREATE TABLE {table}({columns})")
      except sqlite3.OperationalError as e:
        if "already exists" not in str(e):
          print(f"{e}, continuing to next part of 'init_kb'")
    _ensure_columns(conn, "items", ITEMS_COLUMNS)
    conn.commit()
  elif mode == "read_only":
    db_path =  Path("file:" + str(path)) / "kb.db?mode=ro"
    conn = sqlite3.connect(db_path, uri=True)
    conn.row_factory = sqlite3.Row
  return conn

def get_kb_db(kb_path: Path):
  # `init_kb` is idempotent, so initializing here means every caller gets the tables (and
  # any pending column migration) without having to remember to do it themselves.
  return init_kb(kb_path)

def get_kb_db_ro(kb_path: Path):
  return init_kb(kb_path, "read_only")