from shelly_docs.kb import KnowledgeBase, Item
import os
from pathlib import Path
from rich import print
import pytest


class TestKnowledgeBaseGetItem:
  def test_get_item(self, kb_a):
    print("kb_path", kb_a)
    print("kb_path::contents (ls)", os.listdir(kb_a))
    kb = KnowledgeBase(kb_a)
    
    item = kb.get_item("ABC-2")
    print("retrieved item", item)
    assert isinstance(item, Item)
    assert item.heading == '# ABC-2 Beta'
    assert item.data == {'field1': 8, 'field2': "value", 'type': "ABC"}
    assert item.content == 'I have some more text here.\n\n## My Subheading\n\nyo'
    assert str(item.file).split("#")[0] == str(Path('input_a.md'))
    assert item.parent_key == None

  def test_get_item_with_parent(self, kb_a):
    print("kb_path", kb_a)
    print("kb_path::contents (ls)", os.listdir(kb_a))
    kb = KnowledgeBase(kb_a)
    
    item = kb.get_item("ABC-2-1")
    print("retrieved item", item)
    assert isinstance(item, Item)
    assert item.heading == '## ABC-2-1 Beta - Bruh'
    assert item.data == None
    assert item.content == ''
    assert str(item.file).split("#")[0] == str(Path('input_a.md'))
    assert item.parent_key == 'ABC-2'


class TestKnowledgeBaseCreateItem:
  def test_create_item_existing_file(self, kb_a):
    print("kb_path", kb_a)
    kb = KnowledgeBase(kb_a)
    # create item as ABC-4
    kb.create_item(
      "input_a.md",
      "ABC",
      "Making stuff",
      {"status": "todo"},
      "I have some content here",
      #"PROCESS-1"
    )

    # check for the item after creating it
    created_item = kb.get_item("ABC-4")
    print("created_item", created_item)
    print("kb_state", kb.state)
    assert created_item.heading == "# ABC-4 Making stuff"

  def test_create_item_existing_file_same_as_prev_sibling(self, kb_a):
    print("kb_path", kb_a)
    kb = KnowledgeBase(kb_a)
    # create item as ABC-4
    kb.create_item(
      "input_b.md",
      "ABC",
      "Making stuff",
      {"status": "todo"},
      "I have some content here",
      #"PROCESS-1"
    )

    # check for the item after creating it
    created_item = kb.get_item("ABC-4")
    print("created_item", created_item)
    print("kb_state", kb.state)
    assert created_item.heading == "# ABC-4 Making stuff"

  def test_create_item_with_sibling_gap(self, kb_b):
    print("kb_path", kb_b)
    kb = KnowledgeBase(kb_b)
    # create item as ABC-4
    kb.create_item(
      "input_b.md",
      "DOC",
      "Silver",
      {"status": "todo"},
      "I have some content here",
      #"PROCESS-1"
    )

    # check for the item after creating it
    created_item = kb.get_item("DOC-6")
    print("created_item", created_item)
    print("kb_state", kb.state)
    assert created_item.heading == "# DOC-6 Silver"

  def test_create_item_new_file(self, kb_a):
    print("kb_path", kb_a)
    kb = KnowledgeBase(kb_a)
    # create item as ABC-4
    kb.create_item(
      "test_a.md",
      "ABC",
      "Making stuff",
      {"status": "todo"},
      "I have some content here",
      #"PROCESS-1"
    )

    # check for the item after creating it
    created_item = kb.get_item("ABC-4")
    print("created_item", created_item)
    print("kb_state", kb.state)
    assert created_item.heading == "# ABC-4 Making stuff"

  def test_create_item_as_child_existing_file(self, kb_a):
    print("kb_path", kb_a)
    kb = KnowledgeBase(kb_a)
    # create item as ABC-4
    kb.create_item(
      "input_b.md",
      "ABC",
      "Making stuff",
      {"status": "todo"},
      "I have some content here",
      "ABC-3"
    )

    # check for the item after creating it
    created_item = kb.get_item("ABC-3-1")
    print("created_item", created_item)
    print("kb_state", kb.state)
    assert created_item.heading == "## ABC-3-1 Making stuff"

  def test_create_item_as_child_new_file(self, kb_a):
    print("kb_path", kb_a)
    kb = KnowledgeBase(kb_a)
    # create item as ABC-3-1
    kb.create_item(
      "input_a.md",
      "ABC",
      "Making stuff",
      {"status": "todo"},
      "I have some content here",
      "ABC-3"
    )
    # check for the item after creating it
    created_item = kb.get_item("ABC-3-1")
    print("created_item", created_item)
    print("kb_state", kb.state)
    assert created_item.heading == "# ABC-3-1 Making stuff"
  

class TestKnowledgeBaseUpdateItem:
  def test_set_data_existing_file(self, kb_a):
    #print("kb_path", kb_a)
    kb = KnowledgeBase(kb_a)
    # Update Item 'ABC-2'
    item = kb.get_item('ABC-2')
    item.set_data({"status": "updated"})
    # check for the item after creating it
    updated_item = kb.get_item("ABC-2")
    print("updated_item", updated_item)
    assert updated_item.data == {"status": "updated", 'type': 'ABC'}
 
  def test_set_content_existing_file(self, kb_a):
    #print("kb_path", kb_a)
    kb = KnowledgeBase(kb_a)
    # Update Content of Item 'ABC-2'
    item = kb.get_item('ABC-2')
    item.set_content("I updated the text here.")
    # check for the item after creating it
    updated_item = kb.get_item("ABC-2")
    print("updated_item", updated_item)
    assert updated_item.content == "I updated the text here."

  def test_move_item_to_existing_file(self, kb_a):
    kb = KnowledgeBase(kb_a)
    item = kb.get_item('ABC-2')
    item.set_file("input_b.md")
    assert item.file == "input_b.md"
    assert str(kb.get_item('ABC-2').file).split("#")[0] == "input_b.md"
    actual_file=kb.path / "input_b.md"
    print("test_move_item_to_existing_file::actual_file\n", actual_file.read_text())
  def test_move_item_to_new_file(self, kb_a):
    kb = KnowledgeBase(kb_a)
    item = kb.get_item('ABC-2')
    item.set_file("input_c.md")
    assert item.file == "input_c.md"
    assert str(kb.get_item('ABC-2').file).split("#")[0] == "input_c.md"
    actual_file=kb.path / "input_c.md"
    print("test_move_item_to_existing_file::actual_file\n", actual_file.read_text())

class TestKnowledgeBaseDeleteItem:
  def test_delete_item_existing_file(self, kb_a):
    kb = KnowledgeBase(kb_a)
    kb.delete_item("ABC-2")
    assert kb.get_item("ABC-2") == None

class TestKnowledgeBaseReparentItem:
  def test_reparent_item(self, kb_a):
    kb = KnowledgeBase(kb_a)
    item = kb.get_item('ABC-2-1')
    item.reparent("ABC-3",None)
    print("test_reparent_item::item.markdown",item.markdown)
    actual_file=kb.path / "input_a.md"
    print("test_reparent_item::actual_file\n", actual_file.read_text())
    state = kb.state
    print("test_reparent_item::kb.state",state)
    item_in_state = state.get('items').get('ABC-3-1')
    assert item_in_state.get('parent') == 'ABC-3'
    assert item_in_state.get('title') == 'ABC-3-1 Beta - Bruh'
    assert item_in_state.get('key') == 'ABC-3-1'

class TestKnowledgeBaseRenameItem:
  def test_rename_item(self, kb_a):
    kb = KnowledgeBase(kb_a)
    item = kb.get_item('ABC-2-1')
    item.rename("Super Sonic Speed")
    print("test_reparent_item::item.markdown",item.markdown)
    actual_file=kb.path / "input_a.md"
    print("test_reparent_item::actual_file\n", actual_file.read_text())
    state = kb.state
    print("test_reparent_item::kb.state",state)
    item_in_state = state.get('items').get('ABC-2-1')
    assert item_in_state.get('title') == 'ABC-2-1 Super Sonic Speed'
    assert item_in_state.get('key') == 'ABC-2-1'


class TestKnowledgeBaseQuery:
  def test_query_yaml_str(self, kb_a):
    kb = KnowledgeBase(kb_a)
    query="""field1: 5
"""
    query_out = kb.query(query)
    print("test_query_yaml_str::query_out\n",query_out)
    assert query_out.get('results')[0].get('key') == 'XYZ-1'
  def test_query_logic_yaml_str(self, kb_a):
    kb = KnowledgeBase(kb_a)
    query="""
$or:
- field1: 5
- field1: 8
"""
    query_out = kb.query(query)
    print("test_query_yaml_str::query_out\n",query_out)
    assert len(query_out.get('results')) == 2 # ABC-2 and XYZ-1
  def test_query_dict(self, kb_a):
    kb = KnowledgeBase(kb_a)
    query={"field1": 5}
    query_out = kb.query(query)
    print("test_query_dict::query_out\n",query_out)
  def test_query_pipeline(self, kb_a):
    kb = KnowledgeBase(kb_a)
    query=[{'field2': 'value'},{'type':'ABC'}]
    query_out = kb.query(query)
    print("test_query_pipeline::query_out\n",query_out)
    keys = [x.get('key') for x in query_out.get('results')]
    print("test_query_pipeline::keys\n",keys)
    assert 'ABC-3' in keys