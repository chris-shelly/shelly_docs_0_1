from shelly_docs.kb import KnowledgeBase
import os

class TestKnowledgeBase:
  def test_get_item(self, kb_with_state):
    print("kb_path", kb_with_state)
    print("kb_path::contents (ls)", os.listdir(kb_with_state))
    kb = KnowledgeBase(kb_with_state)
    
    item = kb.get_item("ABC-2")
    print("retrieved item", item)
    assert item.get("key") == "ABC-2"
    
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
  

