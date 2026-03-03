from pathlib import Path
import re

def get_items(path: str, config: dict) -> list[dict]:
  dir = Path(path)
  # confirm that 'dir' is a directory
  items = []
  if dir.is_dir():
    pass
    docs = get_md_docs_in_dir(dir)
    print(docs)
  return docs
  #for doc in docs:
  #  items = items + read_items_in_doc(doc, config['item_tags'])
  #print(items)
  #return items

def get_md_docs_in_dir(dir: Path) -> list[Path]:
  docs = []
  for child in dir.iterdir():
    if child.suffix == ".md":
      docs.append(child)
    elif child.is_dir():
      docs = docs + get_md_docs_in_dir(child)
  return docs

def read_items_in_doc(doc: Path, item_tags: list[str]) -> list[dict]:
  pass



