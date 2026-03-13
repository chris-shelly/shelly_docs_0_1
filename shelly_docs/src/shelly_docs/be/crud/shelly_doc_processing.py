"""
Module for processing Shelly Docs Items in a Document
"""
from pathlib import Path
import re
import json
from ruamel.yaml import YAML
from typing import Union

from mistletoe import Document
from mistletoe.ast_renderer import ASTRenderer
from mistletoe.block_token import CodeFence
from mistletoe.token import Token


from ..shelly_docs_config.config import get_config
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


def get_raw_shelly_docs_items_from_md(md: str, filepath: str, kb_path: Union[str, Path],  tags: list[str]):
  """
  For parsing new Shelly Doc Items created from the TUI or CLI
  """
  document = parse_md_doc_from_string(md)
  token_dict = parse_token_ast(document)
  return parse_token_dict(token_dict, Path(filepath), Path(kb_path) , tags)

def parse_token_dict(token_dict: dict, filepath: Path, kb_path: Union[str, Path], tags: list[str]) -> list[dict]:
  """
  Take a dict representation of a Markdown AST and return all of the Shelly Doc items
  """
  items = []
  # go through the token's children
  # a markdown document is flat as far as we're concerned, so we can get add items linearly
  item = {"heading": None, "content": []}
  for child in token_dict['children']:
    if child['type'] == "Heading":
      # check the line to make sure it's a valid heading
      potential_item_title = get_string_section_from_path(kb_path / filepath, child['line_number'],child['line_number'])
      if title_is_valid_item_decl(potential_item_title, tags):
        # look back and push the last item to the items list
        if item.get("heading"):
          item["end_line"] = child["line_number"] - 1
          items.append(item)
        item = {"heading": child, "start_line": child["line_number"], "path": str(filepath.relative_to(kb_path)), "level": child["level"]}
  # add last item at end
  if item.get("heading"):
    items.append(item)
  return items

def title_is_valid_item_decl(potential_title: str, tags: list[str]) -> Union[re.Match, None]:
  for tag in tags:
    title_pattern_base = r'^(#{1,6})\s+(ABC-\d+.*)\s*$'
    title_pattern = title_pattern_base.replace('ABC',tag)
    match = re.match(title_pattern, potential_title)
    if match:
      return match
  # if haven't matched with a tag, return None
  return None

def get_raw_shelly_docs_items_from_path(filepath: Path, kb_path: Union[str, Path], tags: list[str]) -> list[dict]:
  """
  Read the Markdown mistletoe.Document and determine the raw items.
  Provides the 'start' and 'end' lines delineating the Items.
  """
  document = parse_md_doc_from_path(filepath)
  # get the token as a dict
  token_dict = parse_token_ast(document)
  return parse_token_dict(token_dict, filepath, kb_path, tags)


def get_item_markdown(item: dict, kb_path: Union[Path, str], markdown_string: Union[str, None] = None ):
  start = item.get("start_line")
  end = item.get("end_line")
  if markdown_string:
    item_markdown = get_string_section_from_md(markdown_string, start, end)
    return item_markdown
  else:
    path = item.get("path")
    item_markdown = get_string_section_from_path(Path(kb_path) / Path(path) , start, end)
    return item_markdown

def get_item_title(item: dict) -> str:
  markdown: str = item.get("markdown")
  if markdown:
    title_pattern = r'^(#{1,6})\s+(.*?)(?:\s+#+\s*)?$'
    title = re.match(title_pattern,markdown.splitlines()[0].strip()).group(2)
    return title
  else:
    raise ValueError("item markdown has not been retrieved. Cannot determine title.")
  

def get_tag_from_title(title: str):
  """
  Determine the Item Tag from a title string ("ABC-2-1 Johnathan")
  """
  item_tag_connector = "-"
  item_tag = title.split(item_tag_connector)[0]
  return item_tag

def get_string_section_from_md(markdown: str, start: int= 1, end: Union[int, None] = None) -> str:
  """
  Get a section of string from the markdown string by lines. 
  We can use this to get the markdown of an Item
  """
  string = markdown.splitlines(keepends=True)
  if start < 1:
    start = 1
  if end != None:
    return ''.join(string[start-1:end])
  else:
    return ''.join(string[start-1:])

def get_string_section_from_path(path: str , start: int = 1, end: Union[int, None] = None) -> str:
  """
  Get a section of string from the markdown document (specified by 'path') by lines. 
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
  # iterate through children of the item, return the data from inside the first "yaml (data)" code fence
  # assumes that the code fence is a direct child of the Document object
  for child in item_document.children:
    if isinstance(child, CodeFence):
      if child.info_string == "yaml (data)":
        fenced_data = yaml.load(child.content)
        if isinstance(fenced_data, dict) and (not fenced_data.get("type")): # only overwrites the item type if it doesnt already exist
          fenced_data["type"] = get_tag_from_title(item['title'])
        return fenced_data
  

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

def process_shelly_docs_items(filepath: str, kb_path: Union[str, Path], config: dict) -> list[dict]:
  """
  Process the items within a file
  """
  filepath = Path(filepath)
  items = get_raw_shelly_docs_items_from_path(filepath, kb_path,  config['item_tags'])
  processed_items = []
  for item in items:
    item['markdown'] = get_item_markdown(item, kb_path)
    item['title'] = get_item_title(item)
    # check the title to make sure its a valid item type, only continue parsing if that's the case
    if get_tag_from_title(item['title']) in config['item_tags']:
      
      item['data'] = get_codefenced_data(item)
      item['key'] = get_item_key(item)
      item['parent'] = get_item_parent(item)
      item['path'] += "#" + heading_to_anchor(item['title'])
      # heading object no longer needed
      del item['heading']
      processed_items.append(item)
      
  return processed_items

def prep_new_shelly_doc_items_from_document_update(new_item_obj: dict):
  """
  Used when a user makes an update to items via the GUI.
  Best way to capture updates is to 

  Args:
    new_item: dict with 'kb_path', 'filepath', and 'markdown' keys

  Returns:
    dict with 'path', 'title', 'content', and 'parent_title' keys
  """
  # determine the new items
  # it's not guaranteed that the new_item_obj is only one item, so we capture this in a list of items called 'raw_new_items'
  config = get_config(new_item_obj['kb_path'])
  kb_path = Path(new_item_obj['kb_path'])
  raw_new_items = get_raw_shelly_docs_items_from_md(new_item_obj['markdown'], f"{new_item_obj['kb_path']}/{new_item_obj['filepath']}", new_item_obj['kb_path'], config['item_tags'])
  # each of these raw_new_items should then
  semi_processed_items = []
  for item in raw_new_items:
    item['markdown'] = get_item_markdown(item, kb_path ,new_item_obj['markdown'])
    item['title'] = get_item_title(item)
    # check the title to make sure its a valid item type, only continue parsing if that's the case
    if get_tag_from_title(item['title']) in config['item_tags']:
      item['data'] = get_codefenced_data(item)
      item['key'] = get_item_key(item)
      item['parent'] = get_item_parent(item)
      item['path'] += "#" + heading_to_anchor(item['title'])
      # heading object no longer needed
      del item['heading']
      semi_processed_items.append(item)

  # recall that 'start' and 'end' are only for that snippet, and none of the items have actually been added to a file yet
  return semi_processed_items
  

  #return processed_items

