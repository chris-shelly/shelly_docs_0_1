from pathlib import Path
import re
import json
import sqlite3
from typing import Union
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO
from mistletoe import Document
from mistletoe.ast_renderer import ASTRenderer
from rich import print

from ..shelly_docs_config.config import get_config
from ...db.kb import get_kb_db
from ...db import execute_query, execute_query_many
from .shelly_doc_processing import process_shelly_docs_items, prep_new_shelly_doc_items_from_document_update, process_shelly_doc_item, get_item_level

class MyYAML(YAML):
  def dump(self, data, stream=None, **kw):
    inefficient = False
    if stream is None:
      inefficient = True
      stream = StringIO()
    YAML.dump(self, data, stream, **kw)
    if inefficient:
      return stream.getvalue()

yaml = MyYAML()
def get_items(path: str, config: dict) -> list[dict]:
  """Check the directory for items"""
  dir = Path(path)
  items = []
  if dir.is_dir():
    docs = get_md_docs_in_dir(dir)

  for doc in docs:
    items = items + process_shelly_docs_items(doc, path, config)
  return items

class JsonAdapter:
    __slots__ = ("obj",)
    def __init__(self, obj):
        self.obj = obj
    def __conform__(self, protocol):
        if protocol is sqlite3.PrepareProtocol:
            return json.dumps(self.obj)

def write_items_to_state(path: str) -> None:
  """
  Checks the updated items and then updates the state.
  Write `items` and `ids`to the `state.yaml`
  
  used to support querying and item CRUD
  """
  
    
  #print("write_items_to_state()::")
  state = {"items":{}, "ids": {}}
  
  state_path = Path(f"{path}/state.yaml")
  config = get_config(path)
  # start the ids tree based on the item tags
  ids = {}
  for item_tag in config['item_tags']:
    ids[item_tag] = {"next": f"{item_tag}-1"}
  items = get_items(path, config)
  # given an array of items, write them to state
  state["ids"] = ids
  def add_item_id(item_key: str, item_uuid: str):
      """
      Add an Item to `ids` in `state.yaml`
  
      Items must bring their own IDs
      - check for availability
      - insert into the `ids` object
      - updates the appropriate 'next'
        - if top level, updates the `{{item_type}}.next`
        - else, updates the `{{item_parent}}.next`
      - create a 'next' for the prospective child
      """
      # extract the important pieces of the item (ex. 'ABC-2-1-1 Hello')
        # item key (ex. 'ABC-2-1-1')
          # the key used to refer to the item
        # item prefix (ex. 'ABC-2-1')
          # everything before the last part of the item, 
          # used to determine if the item has a parent and which `next` field should be updated
        # item type (ex. 'ABC')
          # used to determine where in the `state.yaml::ids` the item ID lives
      #print("add_item_id()::item_key", item_key)
      item_head = "-".join(item_key.split('-')[:-1])
      item_tail = item_key.split('-')[-1]
      item_type = item_key.split('-')[0]
      has_parent = (item_type != item_head)
  
      # check for availability
        # doesn't conflict with existing IDs (i.e. is not already found in `state.yaml::ids` and not already added to 'state.yaml::items')
      id_available = (state.get("ids").get(item_type).get(item_key) is None)
  
      if id_available:
        # insert into the IDs object
        state.get("ids").get(item_type).update({item_key: {"next": f"{item_key}-1"}})
        # update the 'next' (if no parent, update `ids.{{item_type}}.next` else, update `ids.{{item_type}}.{{item_parent.next}}`)
        old_next = None
        if has_parent:
          # check the current 'next'
          #print("add_item_id()::item_head", item_head)
          #print("add_item_id()::state.get('ids').get(item_type)", state.get("ids").get(item_type))
          #print("add_item_id()::state.get('ids').get(item_type).get(item_head)", state.get("ids").get(item_type).get(item_head))
          # if the child has a parent that has not had its ID registered?
          # recursively add the item ID of the parent
          #add_item_id(item_head)
          parent_id_added = (state.get("ids").get(item_type).get(item_head) is not None)
          if not parent_id_added:
            #print(f"add_item_id()::recursively adding parent {item_head} of item {item_key}")
            def get_item_uuid_from_candidates(item_key_to_check) -> str:
              for item in items:
                if item['key'] == item_key_to_check:
                  return item['uuid']
            add_item_id(item_head, get_item_uuid_from_candidates(item_head))
          old_next = state.get("ids").get(item_type).get(item_head).get("next")
          old_next_head = "-".join(old_next.split('-')[:-1])
          # if the tail of the old next is lte the tail of the inserted key, the new next should be 1 greater than the tail of the inserted key
          old_next_tail = old_next.split('-')[-1]
          if int(old_next_tail) <= int(item_tail):
            new_next_tail = str(int(item_tail) + 1)
            new_next = f"{old_next_head}-{new_next_tail}"
            state.get("ids").get(item_type).get(item_head).update({"next": new_next})
        else:
          #print("add_item_id()::no_parent::state.get('ids).get(item_type)", state.get("ids").get(item_type))
          old_next = state.get("ids").get(item_type).get("next")
          old_next_head = "-".join(old_next.split('-')[:-1])
          # if the tail of the old next is lte the tail of the inserted key, the new next should be 1 greater than the tail of the inserted key
          old_next_tail = old_next.split('-')[-1]
          if int(old_next_tail) <= int(item_tail):
            new_next_tail = str(int(item_tail) + 1)
            new_next = f"{old_next_head}-{new_next_tail}"
            state.get("ids").get(item_type).update({"next": new_next})
        pass
      else:
        # check the UUID if the same item has already been added
        uuid_according_to_items = state.get("items").get(item_key).get("uuid")
        if ((uuid_according_to_items is not None) and (uuid_according_to_items == item_uuid)):
          #print(f"item {item_key} was already added due to child being discovered first")
          pass
        else:
          raise ValueError(f"ID {item_key} is not available according to the state.")
  for item in items:
    item_key = item['key'] # item titles are in the form of "ABC-1 Hello", so splitting like this gives us the item key
    state["items"][item_key] = item # add the item under the item key
    add_item_id(item_key, item['uuid'])
    item["document"] = item['path']
    item["data_block"] = JsonAdapter(item["data"])
    # `parse_token_dict` leaves `end_line` unset on the last Item in a document, since there is
    # no following heading to bound it. `executemany` needs every named placeholder present.
    item.setdefault("end_line", None)
    item.setdefault("level", None)
    #print("---")
  
  # database ETL
  # write items to the 'items' table
  # get the database_connection
  
  conn = get_kb_db(Path(path))
  # clear the existing table of items
  delete_items_qry = "DELETE FROM items"
  execute_query(conn, delete_items_qry)
  # clear the existing table of item_keys
  delete_item_keys_qry = "DELETE FROM item_keys"
  execute_query(conn, delete_item_keys_qry)
  delete_item_stems_qry = "DELETE FROM item_stems"
  execute_query(conn, delete_item_stems_qry)

  # for each item, build out the item_keys table
  for item in items:
    #print(item)
    # check that the key is valid
      # (a) key is not already in item_keys
      # (we have already confirmed that the item type is valid)
    # make sure the next available programmatically created item is valid.
      # (b) set next available child key of parent (key.next) to be AT LEAST f"{item_stem}-{item_tail + 1}"
        # if an item being processed here is less than f"{item_stem}-{item_tail + 1}", it can still be valid as long as the key does not already exist
    
    # (a) - check key uniqueness
    key_valid_qry = "SELECT * FROM item_keys WHERE key = :key"

    results = execute_query(conn, key_valid_qry, item)
    if len(results) > 0:
      print("key_valid_qry::results", results)
      print("current item", item)

      raise ValueError("write_items_to_state::key already found")
   
    # (b) - setup key stems so we can programmatically create valid child keys
    item_stem = "-".join(item['key'].split('-')[:-1])
    item_tail = int(item['key'].split('-')[-1])
    # check if the stem exists
    stem_dict = {"stem": item_stem}
    stem_exists_qry = "SELECT stem, next FROM item_stems WHERE stem =:stem"
    results = execute_query(conn, stem_exists_qry, stem_dict)
    # if so, check if the key is greater than or equal to stem.next
    if len(results) == 1:
      #print("stem_exists_qry_results",results)
      #print("item", item)
      #print("item_tail", item_tail)
      stem_next_stem = "-".join(results[0]['next'].split('-')[:-1])
      stem_next_tail = int(results[0]['next'].split('-')[-1])
      if (item_stem == stem_next_stem):
        update_qry ="""
          UPDATE item_stems
            SET next = :new_next
            WHERE stem = :stem
          """
        if (item_tail >= stem_next_tail):
          #print("_increase stem.next to be one greater than item_tail_")
          update_stem_dict = {"stem": item_stem, "new_next": f"{item_stem}-{item_tail + 1}"}
          execute_query(conn, update_qry, update_stem_dict)
        # else, continue, nothing else needed
    else: # stem doesn't exist, we need to create it
      insert_stem_dict = {"stem": item_stem, "new_next": f"{item_stem}-{item_tail + 1}"}
      execute_query(conn, "INSERT INTO item_stems VALUES(:stem, :new_next)", insert_stem_dict)  
    


    item_key_record = {"key": item["key"], "stem": item_stem, "next": f"{item_stem}-{item_tail+1}"}
    item_stem_record = {
      "key": item["key"],
      "next": f"{item["key"]}-{1}"
    }
    # given a unique item, we also need to add a stem for it
    stem_insert_qry = "INSERT INTO item_stems VALUES(:key, :next)"
    execute_query(conn, stem_insert_qry, item_stem_record)
    key_insert_qry = "INSERT INTO item_keys VALUES(:key)"
    execute_query(conn, key_insert_qry, item_key_record)

  # we want an item_keys table so that we can add valid items programmatically without having to read the entire existing knowledge base

  # insert each of the items into the items table
  qry = (
    "INSERT INTO items (key, name, parent, data, content, document, type, uuid, start_line, end_line, level) "
    "VALUES(:key, :name, :parent, :data_block, :content, :document, :type, :uuid, :start_line, :end_line, :level)"
  )
  execute_query_many(conn, qry, items)
  conn.commit()
  # remove the JSON adapter 'data_block' field from each item
  for item in items:
    del item["data_block"]
  yaml.dump(state, state_path)

def get_state(path: str) -> dict:
  """
  Return the dictionary that lives in `state.yaml`
  """
  state_path = Path(f"{path}/state.yaml")
  state = yaml.load(state_path.read_text())
  return state
def get_item(path: str, item_key: str):
  """
  Get a specific item within the state by `item_key`
  """
  # given an Item Key (the first part of the Title), get a specific item
  state = get_state(path)
  return state["items"][item_key]

def document_relpath(document: Union[str, None]) -> str:
  """
  Reduce an `items.document` value (or an incoming `item['path']`) to a plain KB-relative
  markdown path.

  Both forms turn up: 'notes.md' from a fresh caller, and 'notes.md#abc-1-alpha' from
  anything that has been through `state.yaml` or `process_shelly_doc_item`.
  """
  if not document:
    return ""
  return str(Path(document.split('#')[0]))

def resolve_document(kb_path: str, document: Union[str, None]) -> Union[Path, None]:
  """
  The absolute, comparable location of a document, ignoring any '#anchor' suffix
  """
  relative_path = document_relpath(document)
  if not relative_path:
    return None
  return (Path(kb_path) / relative_path).resolve()

def append_block(lines: list[str], new_block: str, blank_line_before: bool = False) -> tuple[int, int]:
  """
  Append an Item's markdown to the end of a document's lines, in place.

  Documents don't always end in a newline, so guard against welding the new block onto the
  last existing line. Returns the Item's 1-based, inclusive line range.
  """
  if lines and not lines[-1].endswith('\n'):
    lines[-1] += '\n'
  if blank_line_before:
    lines.append('\n')
  start_line = len(lines) + 1
  lines.append(new_block)
  return start_line, start_line + len(new_block.splitlines()) - 1

def put_item(path: str, item_key: str, item: dict, config: dict):
  """Add or update an Item in the Markdown document.

  Reads its view of the Knowledge Base from `<kb>/kb.db`, and writes the result back there.
  It does not touch `state.yaml` — refreshing that is the caller's job, via
  `write_items_to_state()` or `KnowledgeBase.update_state()`.

  Args:
    path: KB directory path
    item_key: e.g. "USECASE-4"
    item: dict with 'markdown' and 'path' (target .md file, with or without a '#anchor')
    config: config dict containing 'item_tags'

  Raises:
    ValueError: if item_key tag prefix not in config item_tags
    ValueError: if item_key already exists in a different file
  """
  conn = get_kb_db(Path(path))

  # Validate item type — match the longest configured tag that the key starts with
  tag_prefix = None
  for tag in config['item_tags']:
    if item_key.startswith(tag + '-'):
      if tag_prefix is None or len(tag) > len(tag_prefix):
        tag_prefix = tag
  if tag_prefix is None:
    raise ValueError(f"Item key '{item_key}' does not match any configured item_tags: {config['item_tags']}")

  # Callers hand us either 'notes.md' or 'notes.md#anchor' (`state.yaml` stores the anchored
  # form). Strip it once, here: everything below wants the bare relative path, and
  # `process_shelly_doc_item` appends the anchor again at the end.
  item['path'] = document_relpath(item['path'])
  item_path_resolved = resolve_document(path, item['path'])

  # Heading depth of the incoming markdown. `get_sibling_positioning` matches on it and the
  # `items` table stores it, but callers generally don't supply it.
  item['level'] = get_item_level(item)

  # Validate key uniqueness across files — one indexed read, rather than re-parsing every
  # markdown document in the Knowledge Base
  existing_rows = execute_query(
    conn,
    "SELECT key, document FROM items WHERE key = :key",
    {"key": item_key},
  )
  for existing in existing_rows:
    if resolve_document(path, existing['document']) != item_path_resolved:
      raise ValueError(
        f"Item '{item_key}' already exists in a different file: {existing['document']}"
      )

  # Build the new heading + content block
  target_path = Path(path) / item['path']

  new_block = f"{item['markdown']}\n"
  block_length = len(new_block.splitlines())

  if not target_path.exists():
    # the Item is the whole document
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(new_block)
    item['start_line'] = 1
    item['end_line'] = block_length
  else:
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
      new_lines = [new_block]
      # Ensure a blank line before next section if not at EOF
      if end_idx < len(lines) and not new_lines[-1].endswith('\n\n'):
        new_lines.append('\n')
      lines[heading_idx:end_idx] = new_lines
      # `start_line`/`end_line` are 1-based and inclusive, matching `parse_token_dict`
      item['start_line'] = heading_idx + 1
      item['end_line'] = heading_idx + len(''.join(new_lines).splitlines())
      target_path.write_text(''.join(lines))
    else:
      # Add the item:
      # look up the parent in the database, and only use it if it's in the same document
      parent = None
      parent_key = item.get('parent')
      if parent_key:
        parent_rows = execute_query(
          conn,
          "SELECT key, document, start_line, end_line, level FROM items WHERE key = :parent_key",
          {"parent_key": parent_key},
        )
        for parent_row in parent_rows:
          if resolve_document(path, parent_row['document']) == item_path_resolved:
            parent = parent_row
            break

      # if parent exists in the target path, write to the parent
      if parent:
        # insert the child item after the parent item, after all existing sibling items
        # check the database for siblings
        insert_idx = get_sibling_positioning(conn, item)
        if insert_idx is None:
          # no siblings, insert after the parent
          parent_end_line = parent['end_line']
          if parent_end_line is None:
            # a NULL end_line means the parent is the last Item in the document, so append
            item['start_line'], item['end_line'] = append_block(lines, new_block)
          else:
            lines.insert(parent_end_line, new_block)
            item['start_line'] = parent_end_line + 1
            item['end_line'] = item['start_line'] + block_length - 1
        elif insert_idx == -1:
          # the last sibling is at the end of the file
          item['start_line'], item['end_line'] = append_block(lines, new_block)
        else:
          # insert after siblings of the same level. `insert_idx` is the last sibling's
          # 1-based end_line, which as a 0-based index lands just after that line.
          lines.insert(insert_idx, new_block)
          item['start_line'] = insert_idx + 1
          item['end_line'] = item['start_line'] + block_length - 1

        target_path.write_text(''.join(lines))

      # else, append to end of file
      else:
        item['start_line'], item['end_line'] = append_block(lines, new_block, blank_line_before=True)
        target_path.write_text(''.join(lines))

  # Re-read the Item back off disk, so that name/type/data/content/parent/anchor all agree
  # with the document we just wrote.
  # NOTE: this mutates `item` in place and hands back that same object.
  processed_item = process_shelly_doc_item(item, path, config)
  if processed_item['key'] != item_key:
    raise ValueError("key not assigned correctly")
  processed_item["document"] = processed_item['path']
  processed_item["data_block"] = yaml.dump(processed_item["data"])
  processed_item.setdefault("end_line", None)
  processed_item.setdefault("level", None)

  if existing_rows:
    # the same key in the same document — a different one would have raised above
    update_item_qry = """
    UPDATE items
      SET
        name = :name,
        parent = :parent,
        data = :data_block,
        content = :content,
        document = :document,
        type = :type,
        uuid = :uuid,
        start_line = :start_line,
        end_line = :end_line,
        level = :level
      WHERE key = :key
    """
    execute_query(conn, update_item_qry, processed_item)
  else:
    insert_item_qry = (
      "INSERT INTO items (key, name, parent, data, content, document, type, uuid, start_line, end_line, level) "
      "VALUES(:key, :name, :parent, :data_block, :content, :document, :type, :uuid, :start_line, :end_line, :level)"
    )
    execute_query(conn, insert_item_qry, processed_item)
  conn.commit()

def get_sibling_positioning(conn: sqlite3.Connection, item: dict) -> Union[int, None]:
  """
  Check the database for siblings, so we can put a new item as the latest of the existing siblings.

  Siblings are the direct children of `item['parent']`: `items.parent` holds the parent key
  derived from the child's own key ("ABC-2-1" -> "ABC-2"), so an equality match is exact.

  Returns:
    an int, the 1-based `end_line` of the last sibling, used directly as a 0-based
      `list.insert()` index so the new Item lands immediately after it
    -1, when a sibling has no `end_line`, meaning it is the last Item in the document and
      the new Item has to be appended instead
    None, when the parent has no children in this document at this heading level
  """
  parent_key: str = item['parent'] # we know if this is triggered, that the proposed item to be inserted has a parent
  destination_path: str = document_relpath(item['path'])
  item_level = item.get('level')
  insert_position = None
  siblings = execute_query(
    conn,
    "SELECT key, document, level, end_line FROM items WHERE parent = :parent_key",
    {"parent_key": parent_key},
  )
  for sibling in siblings:
    # `document` carries a '#anchor' and OS-native separators, so compare these in Python
    if document_relpath(sibling['document']) != destination_path:
      continue
    if sibling['level'] != item_level:
      continue
    # if the sibling has an end_line, the insert position is that end line
    # else, the insert position is the end, because the sibling is at the end of the file
    sibling_end_line = sibling['end_line']
    if sibling_end_line is None:
      # this sibling is the last Item in the document, so appending is the right answer
      # whatever any other sibling's end_line says
      return -1
    if (insert_position is None) or (sibling_end_line > insert_position):
      insert_position = sibling_end_line

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

  # update the database with the delete. `put_item` reads its view of the Knowledge Base from
  # `items`, so a stale row for a deleted key would look like a cross-file duplicate to it.
  # `item_stems` is deliberately left alone: clearing a stem resets its `next`, which would let
  # a deleted key be handed out again.
  conn = get_kb_db(Path(path))
  execute_query(conn, "DELETE FROM items WHERE key = :key", {"key": item_key})
  execute_query(conn, "DELETE FROM item_keys WHERE key = :key", {"key": item_key})
  conn.commit()

  # update the state with the delete
  del state['items'][item_key]
  state_path = Path(f"{path}/state.yaml")
  yaml.dump(state,state_path)

def get_md_docs_in_dir(dir: Path) -> list[Path]:
  """
  Recursively retrieve all markdown documents in a directory
  - used for us to check for items in the KnowledgeBase
  """
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
    dict with 'path', 'title', 'markdown', and 'parent_title' keys
  """
  return prep_new_shelly_doc_items_from_document_update(new_item_obj)

def parse_md_text(md_text: str) -> dict:
  """
  Use Mistletoe to get the `dict` AST of a Markdown document (passed in as a string)
  """
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
  write_items_to_state(path)
  item = get_item(path, "ACTOR-2")
  
  print(item)
  # update the content field in the item so we can test put_item
  delete_item(path,"ACTOR-3")
  write_items_to_state(path)
  