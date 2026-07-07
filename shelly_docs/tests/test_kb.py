from shelly_docs.kb import KnowledgeBase
import os

class TestKnowledgeBaseGetItem:
  def test_get_item(self, kb_with_state):
    print("kb_path", kb_with_state)
    print("kb_path::contents (ls)", os.listdir(kb_with_state))
    kb = KnowledgeBase(kb_with_state)
    
    item = kb.get_item("ABC-2")
    print("retrieved item", item)
    assert item.get("key") == "ABC-2"

class TestKnowledgeBaseCreateItem:
  def test_create_item_existing_file(self, kb_with_state):
    print("kb_path", kb_with_state)
    kb = KnowledgeBase(kb_with_state)
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
    assert created_item.get("key") == "ABC-4"

  def test_create_item_new_file(self, kb_with_state):
    print("kb_path", kb_with_state)
    kb = KnowledgeBase(kb_with_state)
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
    assert created_item.get("key") == "ABC-4"

  def test_create_item_as_child_existing_file(self, kb_with_state):
    print("kb_path", kb_with_state)
    kb = KnowledgeBase(kb_with_state)
    # create item as ABC-4
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
    assert created_item.get("key") == "ABC-3-1"

  def test_create_item_as_child_new_file(self, kb_with_state):
    print("kb_path", kb_with_state)
    kb = KnowledgeBase(kb_with_state)
    # create item as ABC-4
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
    assert created_item.get("key") == "ABC-3-1"
  

class TestKnowledgeBaseUpdateItem:
  def test_update_item_existing_file(self, kb_with_state):
    #print("kb_path", kb_with_state)
    kb = KnowledgeBase(kb_with_state)
    # Update Item 'ABC_2'
    kb.update_item(
      'ABC-2',
      {"status": "updated"},
      "I updated the text here."
    )

    # check for the item after creating it
    updated_item = kb.get_item("ABC-2")
    print("updated_item", updated_item)
    #print("kb_state", kb.state)
    assert updated_item.get("content") == "I updated the text here."
    assert updated_item.get("data") == {"status": "updated", 'type': 'ABC'}