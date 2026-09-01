import os
from pathlib import Path
from typing import Optional, Union
import sqlite3

import pytest
from rich import print

from shelly_docs.db import execute_query
from shelly_docs.db.kb import init_kb, get_kb_db


class TestInitializeKBDB:
  def test_db_created(self, test_db: sqlite3.Connection):
    cursor = test_db.cursor()
    assert isinstance(cursor, sqlite3.Cursor)
  def test_tables_created(self, test_db: sqlite3.Connection):
    print("\n--test_tables_created--")
    execute_query(
      test_db,
      "CREATE TABLE items(key, name, parent, data, content, document, type, uuid, start_line, end_line, level)"
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
    assert {'name': 'item_keys'} in tables
    assert {'name': 'item_stems'} in tables
    assert {'name': 'item_types'} in tables
    assert {'name': 'jobs'} in tables
    columns = [column["name"] for column in execute_query(test_db, "PRAGMA table_info(items)")]
    assert columns == [
      "key", "name", "parent", "data", "content",
      "document", "type", "uuid", "start_line", "end_line", "level",
    ]
    test_db.close()

  def test_kb_init_migrates_legacy_items_table(self, tmp_path):
    """
    A kb.db written before `end_line`/`level` existed gets the columns added, rather than
    silently keeping the old schema (init_kb ignores the "table already exists" error).
    """
    print("\n--test_kb_init_migrates_legacy_items_table--")
    legacy = sqlite3.connect(tmp_path / "kb.db")
    legacy.row_factory = sqlite3.Row
    execute_query(
      legacy,
      "CREATE TABLE items(key, name, parent, data, content, document, type, uuid, start_line)"
    )
    legacy.commit()
    legacy.close()

    conn = init_kb(tmp_path)
    columns = [column["name"] for column in execute_query(conn, "PRAGMA table_info(items)")]
    # appended in the same order as the CREATE TABLE, so positional inserts still line up
    assert columns[-2:] == ["end_line", "level"]
    conn.close()

class TestStateUpdateETL:
  def test_state_update_sequential_order(self, kb_a):
    """
    Test how we update the state of a knowledge base, reflecting the updates in the Database
    """
    print("\n--test_state_update_sequential--")
    test_db = get_kb_db(Path(kb_a))
    items = execute_query(test_db, "SELECT key FROM items")
    print("items", items)
    # all items are added
    expected_items = ['ABC-1', 'ABC-2', 'ABC-2-1', 'XYZ-1', 'XYZ-2', 'ABC-3']
    for expected_item in expected_items:
      assert {'key': expected_item} in items
    keys = execute_query(test_db, "SELECT * FROM item_keys")
    print("keys", keys)
    for expected_item in expected_items:
      assert {'key': expected_item} in keys
    stems = execute_query(test_db, "SELECT * FROM item_stems")
    print("stems", stems)
    expected_stems = [
      {"stem": "ABC", "next": "ABC-4"},
      {"stem": "ABC-1", "next": "ABC-1-1"},
      {"stem": "ABC-2", "next": "ABC-2-2"},
      {"stem": "ABC-2-1", "next": "ABC-2-1-1"},
      {"stem": "XYZ", "next": "XYZ-3"},
      {"stem": "XYZ-1", "next": "XYZ-1-1"},
      {"stem": "XYZ-2", "next": "XYZ-2-1"},
      {"stem": "ABC-3", "next": "ABC-3-1"}
    ]
    for expected_stem in expected_stems:
      assert expected_stem in stems
    

  def test_state_update_columns(self, kb_a):
    """The ETL has to carry start_line/end_line/level, including the NULL end_line on the
    last Item of a document."""
    print("\n--test_state_update_columns--")
    test_db = get_kb_db(Path(kb_a))
    rows = {row["key"]: row for row in execute_query(test_db, "SELECT key, start_line, end_line, level FROM items")}
    assert rows["ABC-1"]["start_line"] == 1
    assert rows["ABC-1"]["end_line"] == 4
    assert rows["ABC-1"]["level"] == 1
    assert rows["ABC-2-1"]["level"] == 2
    # the last Item in a document has no following heading to bound it
    assert rows["ABC-2-1"]["end_line"] is None
    assert rows["ABC-3"]["end_line"] is None

  def test_state_update_shuffled_order(self, kb_b):
    print("\n--test_state_update_shuffled--")
    test_db = get_kb_db(Path(kb_b))
    items = execute_query(test_db, "SELECT key FROM items")
    print("items", items)
    expected_items = [
      {'key': 'DOC-2'},
      {'key': 'DOC-2-1'},
      {'key': 'DOC-2-1-3'},
      {'key': 'DOC-2-1-1'},
      {'key': 'DOC-2-1-2'},
      {'key': 'DOC-5'},
      {'key': 'DOC-1'},
      {'key': 'DOC-1-1'},
      {'key': 'DOC-4'}
    ]
    keys = execute_query(test_db, "SELECT * FROM item_keys")
    print("keys", keys)
    for expected_item in expected_items:
      assert expected_item in items
      assert expected_item in keys
    
    stems = execute_query(test_db, "SELECT * FROM item_stems")
    print("stems", stems)
    expected_stems = [
      {'stem': 'DOC', 'next': 'DOC-6'},
      {'stem': 'DOC-2', 'next': 'DOC-2-2'},
      {'stem': 'DOC-2-1', 'next': 'DOC-2-1-4'},
      {'stem': 'DOC-2-1-3', 'next': 'DOC-2-1-3-1'},
      {'stem': 'DOC-2-1-1', 'next': 'DOC-2-1-1-1'},
      {'stem': 'DOC-2-1-2', 'next': 'DOC-2-1-2-1'},
      {'stem': 'DOC-5', 'next': 'DOC-5-1'},
      {'stem': 'DOC-1', 'next': 'DOC-1-2'},
      {'stem': 'DOC-1-1', 'next': 'DOC-1-1-1'},
      {'stem': 'DOC-4', 'next': 'DOC-4-1'}
    ]
    for expected_stem in expected_stems:
      assert expected_stem in stems

  def test_key_already_exists(self, request):
    with pytest.raises(ValueError):
      request.getfixturevalue("kb_d")

  def test_json_adapter(self, kb_a):
    pass