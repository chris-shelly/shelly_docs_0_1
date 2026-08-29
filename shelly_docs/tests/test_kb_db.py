import os
from pathlib import Path
from typing import Optional, Union
import sqlite3

import pytest
from rich import print

from shelly_docs.db import execute_query
from shelly_docs.db.kb import init_kb


class TestInitializeKBDB:
  def test_db_created(self, test_db: sqlite3.Connection):
    cursor = test_db.cursor()
    assert isinstance(cursor, sqlite3.Cursor)
  def test_tables_created(self, test_db: sqlite3.Connection):
    print("\n--test_tables_created--")
    execute_query(
      test_db,
      "CREATE TABLE items(key, name, parent, data, content, document, type, uuid, start_line, end_line)"
    )
    execute_query(
      test_db,
      "CREATE TABLE item_ids(stem, next)"
    )
    execute_query(
      test_db,
      "CREATE TABLE item_types(type)"
    )
    execute_query(
      test_db,
      "CREATE TABLE jobs(name, type, script, active, item_types, query)"
    )
    tables = execute_query(test_db, "SELECT name FROM sqlite_master WHERE type='table'")
    assert len(tables) > 0
    assert {'name': 'items'} in tables
    assert {'name': 'item_ids'} in tables
    assert {'name': 'item_types'} in tables
    assert {'name': 'jobs'} in tables

  def test_kb_init(self, kb_a):
    print("\n--test_kb_init--")
    test_db = init_kb(Path(kb_a))
    tables = execute_query(test_db, "SELECT name FROM sqlite_master WHERE type='table'")
    print("tables", tables)
    assert len(tables) > 0
    assert {'name': 'items'} in tables
    assert {'name': 'item_ids'} in tables
    assert {'name': 'item_types'} in tables
    assert {'name': 'jobs'} in tables
    test_db.close()

class TestStateUpdateETL:
  def test_state_update(self, kb_a, test_db):
    """
    Test how we update the state of a knowledge base, reflecting the updates in the Database
    """
    pass
