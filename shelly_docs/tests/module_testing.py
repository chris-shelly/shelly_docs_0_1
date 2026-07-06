from shelly_docs.kb import KnowledgeBase

kb = KnowledgeBase("../../mgmt_docs")

item_a = kb.get_item("SYSTEM-2-4")
print("item_a", item_a)
item_b = kb.create_item(
  "test_a.md",
  "ACTOR",
  "Making stuff",
  {"status": "todo"},
  "I have some content here",
  #"PROCESS-1"
)
