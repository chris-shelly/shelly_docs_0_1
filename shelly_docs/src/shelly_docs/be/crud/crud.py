from pathlib import Path
import re
import json
from ruamel.yaml import YAML
from mistletoe import Document
from mistletoe.ast_renderer import ASTRenderer
from ..shelly_docs_config.config import get_config

from .shelly_doc_processing import process_shelly_docs_items, prep_new_shelly_doc_items_from_document_update

yaml = YAML()
def get_items(path: str, config: dict) -> list[dict]:
  """Check the directory for items"""
  dir = Path(path)
  items = []
  if dir.is_dir():
    docs = get_md_docs_in_dir(dir)

  for doc in docs:
    items = items + process_shelly_docs_items(doc, path, config)
  return items

def write_items_to_state(path: str) -> None:
  """
  Checks the updated items and then updates the state.
  Write `items` to the `state.yaml`

  
  """
  state = {"items":{}}
  state_path = Path(f"{path}/state.yaml")
  items = get_items(path, get_config(path))
  # given an array of items, write them to state
  for item in items:
    item_key = item['title'].split(' ')[0]
    state["items"][item_key] = item
  yaml.dump(state, state_path)

def get_state(path: str) -> dict:
  state_path = Path(f"{path}/state.yaml")
  state = yaml.load(state_path.read_text())
  return state
def get_item(path: str, item_key: str):
  # given an Item Key (the first part of the Title), get a specific item
  state = get_state(path)
  return state["items"][item_key]

def put_item(path: str, item_key: str, item: dict, config: dict):
  """Add or update an Item in the Markdown document.

  Args:
    path: KB directory path
    item_key: e.g. "USECASE-4"
    item: dict with 'title', 'content', 'path' (target .md file)
    config: config dict containing 'item_tags'

  Raises:
    ValueError: if item_key tag prefix not in config item_tags
    ValueError: if item_key already exists in a different file
  """

  state: dict = get_state(path)
  state_items: dict = state['items']

  # Validate item type — match the longest configured tag that the key starts with
  tag_prefix = None
  for tag in config['item_tags']:
    if item_key.startswith(tag + '-'):
      if tag_prefix is None or len(tag) > len(tag_prefix):
        tag_prefix = tag
  if tag_prefix is None:
    raise ValueError(f"Item key '{item_key}' does not match any configured item_tags: {config['item_tags']}")

  # Validate key uniqueness across files
  existing_items = get_items(path, config)
  item_path_resolved = (Path(path) / item['path'].split('#')[0]).resolve()
  for existing in existing_items:
    existing_key = existing['title'].split(' ')[0]
    existing_file_resolved = (Path(path) / existing['path'].split('#')[0]).resolve()
    if existing_key == item_key and existing_file_resolved != item_path_resolved:
      raise ValueError(
        f"Item '{item_key}' already exists in a different file: {existing['path']}"
      )

  # Build the new heading + content block
  target_path = Path(path) / item['path'].split('#')[0] # split off the md anchor

  new_block = f"{item['markdown']}\n"

  if not target_path.exists():
    target_path.parent.mkdir(exist_ok=True)
    target_path.write_text(new_block)
    state = get_state(path)
    state['items'][item_key] = item
    state_path = Path(f"{path}/state.yaml")
    yaml.dump(state,state_path)
    return

  lines = target_path.read_text().splitlines(keepends=True)

  # Look for existing heading matching the item_key
  heading_pattern = re.compile(rf'^(#+)\s+{re.escape(item_key)}\b')
  heading_idx = None
  heading_level = None
  for i, line in enumerate(lines):
    m = heading_pattern.match(line)
    if m:
      heading_idx = i
      heading_level = len(m.group(1))
      break

  if heading_idx is not None:
    # Update the item: find end boundary (next heading at same or higher level, or EOF)
    end_idx = len(lines)
    for i in range(heading_idx + 1, len(lines)):
      m = re.match(r'^(#+)\s', lines[i])
      if m and len(m.group(1)) <= heading_level:
        end_idx = i
        break

    # Add the new markdown block
    new_lines = [f"{item['markdown']}\n"]
    # Ensure a blank line before next section if not at EOF
    if end_idx < len(lines) and not new_lines[-1].endswith('\n\n'):
      new_lines.append('\n')
    lines[heading_idx:end_idx] = new_lines
    target_path.write_text(''.join(lines))
  else:
    # Add the item:
    # look up the parent in the state and check if its at the same path
    
    parent = state_items.get(item['parent'])
    # if parent exists in the target path, write to the parent
    if parent:
      # insert the child item after the parent item, after all existing sibling items
      # check the state for siblings

      insert_idx = get_sibling_positioning(state, item)
      if insert_idx >= 0: # insert after siblings of the same level
        lines.insert(insert_idx,new_block)
      elif insert_idx == -1:
        # sibling is at the end of the file
        lines.append(new_block)
      else: # no siblings, insert after parent
        lines.insert(parent['end_line'],new_block)
        

      target_path.write_text(''.join(lines))
      
    # else, append to end of file
    else:
      text = target_path.read_text()
      if text and not text.endswith('\n'):
        text += '\n'
      text += f"\n{new_block}"
      target_path.write_text(text)

  write_items_to_state(path)

def get_sibling_positioning(state: dict, item: str) -> int:
  """
  Check the `state` for siblings, so we can put a new item as the latest of the existing siblings
  """
  state_items: dict = state['items']
  parent_key: str = item['parent'] # we know if this is triggered, that the propsed item to be inserted has a parent
  destination_path: str = item['path'].split('#')[0] # remove anchor from the path
  insert_position = None
  for item_key in state_items.keys():
    if parent_key in item_key:
      family_member_item: dict = state_items.get(item_key)
      # check if sibling item has the same path as the current item
      family_member_item_path: str = family_member_item['path'].split('#')[0]
      family_member_item_level: int = family_member_item['level']
      if (family_member_item_path == destination_path) and (family_member_item_level == item['level']):
        # check if the sibling has an end_line
        # if so, insert position is the sibling's end line
        # else, insert position is the end, because the sibling is at the end of the file
        sibling_end_line = family_member_item.get("end_line")
        if sibling_end_line:
          if (insert_position == None) or (sibling_end_line > insert_position):
            insert_position = sibling_end_line
        else:
          insert_position = -1

  return insert_position

def delete_item(path: str, item_key: str):
  """Remove an Item from its Markdown document.

  Args:
    path: KB directory path
    item_key: e.g. "USECASE-4"

  Raises:
    KeyError: if item_key not found in state
    FileNotFoundError: if the document file doesn't exist
    ValueError: if the heading is not found in the document
  """
  state = get_state(path)
  if item_key not in state["items"]:
    raise KeyError(f"Item '{item_key}' not found in state")

  item = state["items"][item_key]
  doc_path = Path(path) / item['path'].split('#')[0]

  if not doc_path.exists():
    raise FileNotFoundError(f"Document not found: {doc_path}")

  lines = doc_path.read_text().splitlines(keepends=True)

  heading_pattern = re.compile(rf'^(#+)\s+{re.escape(item_key)}\b')
  heading_idx = None
  heading_level = None
  for i, line in enumerate(lines):
    m = heading_pattern.match(line)
    if m:
      heading_idx = i
      heading_level = len(m.group(1))
      break

  if heading_idx is None:
    raise ValueError(f"Heading for '{item_key}' not found in {doc_path}")

  # Find end boundary: next heading at same or higher level, or EOF
  end_idx = len(lines)
  for i in range(heading_idx + 1, len(lines)):
    m = re.match(r'^(#+)\s', lines[i])
    if m and len(m.group(1)) <= heading_level:
      end_idx = i
      break

  del lines[heading_idx:end_idx]
  doc_path.write_text(''.join(lines))
  
  # update the state with the delete
  del state['items'][item_key]
  state_path = Path(f"{path}/state.yaml")
  yaml.dump(state,state_path)

def get_md_docs_in_dir(dir: Path) -> list[Path]:
  docs = []
  for child in dir.iterdir():
    if child.suffix == ".md":
      docs.append(child)
    elif child.is_dir():
      docs = docs + get_md_docs_in_dir(child)
  return docs


def convert_new_item_md(new_item_obj: dict) -> dict:
  """Convert a new_item_md object into a list of item dicts, where we can pass each to put_item().

  Args:
    new_item_obj: dict with 'kb_path', 'filepath', and 'markdown' keys

  Returns:
    dict with 'path', 'title', 'content', and 'parent_title' keys
  """
  return prep_new_shelly_doc_items_from_document_update(new_item_obj)

def parse_md_text(md_text: str) -> dict:
  md_doc_tree = Document(md_text)
  with ASTRenderer() as renderer:
    rendered = renderer.render(md_doc_tree)
  return json.loads(rendered)

def parse_md_doc(path: Path) -> dict:
  """
  Get the AST of a Markdown document
  """
  md_doc_text = path.read_text()
  return parse_md_text(md_doc_text)

if __name__ == "__main__":
  path = "../../mgmt_docs"
  items = get_items(path, {"item_tags": ['ACTOR', 'USECASE', 'DESIGN']})
  write_items_to_state(path,items)
  item = get_item(path, "ACTOR-2")
  
  print(item)
  # update the content field in the item so we can test put_item
  delete_item(path,"ACTOR-3")
  write_items_to_state(path, items)
  