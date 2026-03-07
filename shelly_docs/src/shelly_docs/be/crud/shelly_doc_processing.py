"""
Module for processing Shelly Docs Items in a Document
"""
from pathlib import Path
import re
import json
from ruamel.yaml import YAML
from typing import Union

from rich import print

from mistletoe import Document
from mistletoe.ast_renderer import ASTRenderer
from mistletoe.block_token import CodeFence
from mistletoe.token import Token
yaml = YAML()

def parse_md_ast(path: Path) -> dict:
  """
  Get the AST of a Markdown document
  """
  md_doc_text = path.read_text()
  md_doc_tree = Document(md_doc_text)
  with ASTRenderer() as renderer:
    rendered = renderer.render(md_doc_tree)
  rendered = json.loads(rendered)
  return rendered

def parse_md_doc_from_path(path: Path) -> Document:
  """
  Get the AST of a Markdown document
  """
  md_doc_text = path.read_text()
  return Document(md_doc_text)

def parse_md_doc_from_string(md_string: str) -> Document:
  return Document(md_string)

ITEM_TAGS = ["ABC"]

def parse_token_ast(token: Token):
  with ASTRenderer() as renderer:
    rendered = renderer.render(token)
  rendered = json.loads(rendered)
  return rendered


def get_item_key(item: dict):
  """
  Given an Item Title (ex. "ABC-2 Hi `there`"), get the item key ("ABC-2")
  """
  title: str = item.get("title")
  return title.split(' ')[0]


def get_raw_shelly_docs_items(path: Path):
  """
  Read the Markdown mistletoe.Document and determine the raw items.
  Provides the 'start' and 'end' lines delineating the Items.
  """
  document = parse_md_doc_from_path(path)
  # get the token as a dict
  token_dict = parse_token_ast(document)
  items = []

  # go through the token's children
  # a markdown document is flat as far as we're concerned, so we can get add items linearly
  item = {"heading": None, "content": []}
  for child in token_dict['children']:
    if child['type'] == "Heading":
      # push the last item to the items list
      if item.get("heading"):
        item["end_line"] = child["line_number"] - 1
        items.append(item)
      item = {"heading": child, "start_line": child["line_number"], "path": str(path)}
  # add last item at end
  if item.get("heading"):
    items.append(item)

  return items


def get_item_markdown(item: dict):
  start = item.get("start_line")
  end = item.get("end_line")
  path = item.get("path")
  item_markdown = get_string_section(path, start, end)
  return item_markdown

def get_item_title(item: dict) -> str:
  markdown: str = item.get("markdown")
  if markdown:
    title_pattern = r'^(#{1,6})\s+(.*?)(?:\s+#+\s*)?$'
    title = re.match(title_pattern,markdown.splitlines()[0].strip()).group(2)
    return title
  else:
    raise ValueError("item markdown has not been retrieved. Cannot determine title.")
def get_string_section(path: str , start: int = 1, end: Union[int, None] = None) -> str:
  """
  Get a section of string from a document by lines. 
  We can use this to get the markdown of an Item
  """
  string = Path(path).read_text().splitlines(keepends=True)
  if start < 1:
    start = 1
  if end != None:
    return ''.join(string[start-1:end])
  else:
    return ''.join(string[start-1:])
  


def get_codefenced_data(item: dict):
  """
  Take an Item's markdown, and retrieve the codefenced
  """
  # parse the item to a mistletoe document
  item_document = parse_md_doc_from_string(item['markdown'])
  # iterate through children of the item, return the data from inside the "yaml (data)" code fence
  # assumes that the code fence is a direct child of the Document object
  for child in item_document.children:
    if isinstance(child, CodeFence):
      if child.info_string == "yaml (data)":
        return yaml.load(child.content)
  

def get_item_parent(item: dict):
  """
  Given an Item, determine it's parent
  
  an item's parent item is determined solely by the Item key.
  ex. "ABC-2-1" has a parent of "ABC-2"

  we should be able to find the parent from the key. 
  
  if the parent doesn't exist, 
  """
  key: str = item.get('key')
  # split off the item tag from the key (separate "2-1" from "ABC-2-1")
  # assume the item tag connects to the key number via a hyphen
  item_tag_connector = "-"
 

  hierarchy_delimiter = "-"
  item_tag = key.split(item_tag_connector)[0]
  key_num = hierarchy_delimiter.join(key.split(item_tag_connector)[1:])
  # split off the last part of the delimiter
  parent_key_num = hierarchy_delimiter.join(key_num.split(hierarchy_delimiter)[0:-1])
  if parent_key_num:
    parent_key = item_tag + item_tag_connector + parent_key_num
    return parent_key
  else: 
    return None

def heading_to_anchor(title: str) -> str:
  anchor = title.lower()
  anchor = re.sub(r'[^\w\s-]', '', anchor)
  anchor = re.sub(r'\s+', '-', anchor.strip())
  return anchor

def process_shelly_docs_items(path: str) -> list[dict]:
  """"""
  path = Path(path)
  items = get_raw_shelly_docs_items(path)
  for item in items:
    item['markdown'] = get_item_markdown(item)
    #print(item['markdown'])
    item['title'] = get_item_title(item)
    item['data'] = get_codefenced_data(item)
    item['key'] = get_item_key(item)
    item['parent'] = get_item_parent(item)
    item['path'] += "#" + heading_to_anchor(item['title'])
    # heading object no longer needed
    del item['heading']
  return items


if __name__ == "__main__":
  path = "data.md"
  print(process_shelly_docs_items(path))