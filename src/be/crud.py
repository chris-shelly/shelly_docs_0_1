from config import get_config
from pathlib import Path
import re

def get_items() -> list[dict]:
  print(f"--- get_items() ---")
  config = get_config()
  config['item_tags']
  dir = Path(config['docs_path'])
  # confirm that 'dir' is a directory
  items = []
  if dir.is_dir():
    pass
    docs = get_md_docs_in_dir(dir)
    print(docs)
  for doc in docs:
    items = items + read_items_in_doc(doc, config['item_tags'])
  print(items)
  return items

def get_md_docs_in_dir(dir: Path) -> list[Path]:
  docs = []
  for child in dir.iterdir():
    if child.suffix == ".md":
      docs.append(child)
  return docs

def read_items_in_doc(doc: Path, item_tags: list[str]) -> list[dict]:
  pass



