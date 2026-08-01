# given 'item', extract field1 and write field1 to a text file
from shelly_docs.kb import KnowledgeBase, Item
from pathlib import Path
import os
#kb = KnowledgeBase(".")
#item_obj = kb.get_item(item['key'])
output_filepath = Path(f"{item['key']}.txt")
print("job::add_field1s.py:: current path", output_filepath.absolute())

output_filepath.touch()

output_filepath.write_text(str((item.get("data") or {}).get("field1", "None")))



