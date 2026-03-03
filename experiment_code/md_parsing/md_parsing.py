# use a python markdown parsing library to get an AST, then process it

from pprint import pprint
import json
import re

from pathlib import Path

from mistletoe import Document
from mistletoe.ast_renderer import ASTRenderer

md_doc_text = Path("simple_md.md").read_text()
md_doc_tree = Document(md_doc_text)
with ASTRenderer() as renderer:
  rendered = renderer.render(md_doc_tree)

rendered = json.loads(rendered)
print("--- AST of 'simple_md.md'")
pprint(rendered)

# given some item tags, take the AST and detect content

item_tags = ["YO"]


def read_items_in_doc(doc: dict, item_tags: list[str]) -> list[dict]:
  print(f"--- read_items_in_doc(rendered,{item_tags})---")
  # detect items
  item_tag_base = '^(ABC-\\d+.*)\\s*$'
  items = []
  for item_tag in item_tags:
    item_tag_pattern = re.compile(item_tag_base.replace('ABC', item_tag))
    # go through the document and find all headings matching this pattern
    print("item_tag_pattern", item_tag_pattern)
    items = items  + traverse_for_items(doc, item_tag_pattern)
    print("items", items)
  return items

def get_text_from_children(node:dict, text: str ="", mode: str = "normal"):
  for child in node['children']:
    if child['type'] == 'RawText':
      if mode == 'normal':
        text += child['content']
      elif mode == 'code':
        text += f"`{child['content']}`"
    
    elif child['type'] == 'InlineCode':
      text += get_text_from_children(child, text, mode="code")

  return text

def traverse_for_items(doc: dict, item_tag_pattern: re.Pattern, items: list =[]):
  if doc['type'] == "Heading":
    # find the content within the header
    title = ""
    title = get_text_from_children(doc, title)
    item_match = item_tag_pattern.findall(title)
    if item_match:
      print("-- item match found", item_match[0])
      items.append({"title": item_match[0]})
  for key, value in doc.items():
    #print(key, value)
    if key == "children":
      for child in value:
        traverse_for_items(child, item_tag_pattern, items = items)
  return items
items = read_items_in_doc(rendered, item_tags)
print(items)

