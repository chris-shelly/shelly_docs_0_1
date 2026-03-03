from pathlib import Path
import re
import json
from pprint import pprint

from mistletoe import Document
from mistletoe.ast_renderer import ASTRenderer

def get_items(path: str, config: dict) -> list[dict]:
  dir = Path(path)
  # confirm that 'dir' is a directory
  items = []
  if dir.is_dir():
    pass
    docs = get_md_docs_in_dir(dir)
    #print(docs)
  
  for doc in docs:
    # parse the doc to an AST so we can read the items
    parsed_doc = parse_md_doc(doc)
    #print("---get_items()::parsed_doc--")
    #pprint(parsed_doc)
    # read the items
    items = items + read_items_in_doc(parsed_doc, config['item_tags'])
    print("-- loop items--")
    pprint(items)
  print("---get_items()::items---")
  pprint(items)
  return items

def get_md_docs_in_dir(dir: Path) -> list[Path]:
  docs = []
  for child in dir.iterdir():
    if child.suffix == ".md":
      docs.append(child)
    elif child.is_dir():
      docs = docs + get_md_docs_in_dir(child)
  return docs

def read_items_in_doc(doc: dict, item_tags: list[str]) -> list[dict]:
  print(f"--- read_items_in_doc(rendered,{item_tags})---")
  # detect items
  item_tag_base = '^(ABC-\\d+.*)\\s*$'
  items = []
  for item_tag in item_tags:
    item_tag_pattern = re.compile(item_tag_base.replace('ABC', item_tag))
    # go through the document and find all headings matching this pattern
    #print("item_tag_pattern", item_tag_pattern)
    print("items")
    pprint(items)
    print(f"---traverse_for_items()---")
    #NOTE: must include the empty array, otherwise it will use the existing items value
    new_items = traverse_for_items(doc, item_tag_pattern,[]) 
    
    items = items + new_items
    print("items")
    pprint(items)
  return items

def get_text_from_children(node:dict, text: str ="", mode: str = "normal"):
  for child in node['children']:
    if child['type'] == 'RawText':
      if mode == 'normal':
        text += child['content']
      elif mode == 'code':
        text += f"`{child['content']}`"
    
    elif child['type'] == 'InlineCode':
      print("-- curr text--",text)
      print("--recursing child--")
      pprint(child)
      text = get_text_from_children(child, text, mode="code")
  print("--text at call exit--", text)
  return text

def traverse_for_items(doc: dict, item_tag_pattern: re.Pattern, items: list =[]):
  if doc['type'] == "Heading":
    # find the content within the header
    title = ""
    title = get_text_from_children(doc, title)
    item_match = item_tag_pattern.findall(title)
    if item_match:
      #print("-- item match found", item_match[0])
      items.append({"title": item_match[0]})
  for key, value in doc.items():
    #print(key, value)
    if key == "children":
      for child in value:
        traverse_for_items(child, item_tag_pattern, items = items)
  return items



def parse_md_doc(path: Path):
  md_doc_text = path.read_text()
  md_doc_tree = Document(md_doc_text)
  with ASTRenderer() as renderer:
    rendered = renderer.render(md_doc_tree)
  rendered = json.loads(rendered)
  return rendered

if __name__ == "__main__":
  #get_items("../../experiment_code",{"item_tags": ["YO"]})
  get_items("../../mgmt_docs",{"item_tags": ['ACTOR', 'DESIGN', 'USECASE']})