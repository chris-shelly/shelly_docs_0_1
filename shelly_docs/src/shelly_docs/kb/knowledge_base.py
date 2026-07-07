from pathlib import Path
import sys
from rich import print

from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

from ..be.crud import crud as crud
from ..be.crud import shelly_doc_processing as sdoc


class MyYAML(YAML):
  def dump(self, data, stream=None, **kw):
    inefficient = False
    if stream is None:
      inefficient = True
      stream = StringIO()
    YAML.dump(self, data, stream, **kw)
    if inefficient:
      return stream.getvalue()

class KnowledgeBase:
  """
  A knowledge base for a given directory
  """
  def __init__(self, kb_path: str):
    self.yaml = MyYAML()
    self.path = Path(kb_path)
    self.path_str = kb_path
    shelly_docs_file = self.path / "shellydocs.yaml"
    self.shelly_docs_obj = self.yaml.load(shelly_docs_file.read_text())
    #print(self.shelly_docs_obj)
    self.state_file = self.path / "state.yaml"
    self.state = self.yaml.load(self.state_file.read_text())
  
  def create_item(self, file, item_type, item_name: str, item_data, item_content, parent_key=None):
    """
    Create an Item, adding it to the Knowledge Base
    """
    # given the item type (and parent) determine what the key should be
    def make_item_key():
      """
      Determine the correct key for this item to prevent key overlap
      """
      # if the item has a parent, find the next available item key under that parent
      print('checking/making item key')
      next_key_num = 1
      keys = self.state.get('items').keys()
      if parent_key:
        # check the parent type is the same as the child type
        parent_item = self.state.get('items').get(parent_key)
        if sdoc.get_tag_from_title(parent_item.get("title")) != item_type:
          return None
        # get keys that start with the item key
        
        
        for key in keys:
          if (key[:len(parent_key)] == parent_key) and (key != parent_key):
            print(key, "matched to parent", parent_key)
            print("key num", key.split("-")[-1])
            if int(key.split("-")[-1]) == next_key_num:
              next_key_num += 1
        print(next_key_num)
        return f"{parent_key}-{next_key_num}"
      else:
        # no parent, check for next available key num of that type
        for key in keys:
          if (key[:len(item_type)] == item_type):
            if int(key.split("-")[-1]) == next_key_num:
              next_key_num += 1
        return f"{item_type}-{next_key_num}"

    def make_item_dict(item_key):
      """
      to create the item, we need to make a python dictionary out of the data

      needs:
      - 'title' (includes key and name, ex. "ABC-99 Brand New")
      - 'markdown' ()
      - 'path' (target .md file)
      """
      # build the correct title
      return {
        "title": f"{item_key} {item_name.strip("\n")}", # strip new lines
        "markdown": f"# {item_key} {item_name.strip("\n")}\n```yaml (data)\n{self.yaml.dump(item_data)}```\n{item_content}", # raw content
        "path": file
        } 
    def valid_item_type():
      return (item_type in self.shelly_docs_obj.get('item_tags'))
    # config refers to the shellydocs.yaml we use to verify item types
    
    item_key = make_item_key()
    item_dict = make_item_dict(item_key)
    #print(item_dict)
    if valid_item_type():
      print("creating item")
      crud.put_item(self.path_str, item_key, item_dict, self.shelly_docs_obj)

    # update state after writing
    crud.write_items_to_state(self.path_str)
    self.state = self.yaml.load(self.state_file.read_text())

  def get_item(self, item_key: str) -> dict:
    """
    Given the item key (ex. 'TASK-11'), get an existing Item from the KB
    """
    return self.state.get('items',{}).get(item_key,None)

    
  
  def update_item(self, item_key, item_data=None, item_content=None):
    """
    Used to update an entire item
    - implemented by preparing new item markdown to be passed to `crud.put_item()`

    If wanting to update specific keys in the data block: recommended to use `Item.set_data()`

    If wanting to add to the item content: recommended to use `Item.set_content()`
    """
    #TODO: In the future, make it so 'item_content' templating can specify where the structured data can be placed
    old_item = self.get_item(item_key)
    def item_exists():
      if old_item:
        return True
      else:
        return False
    def update_item_data() -> str:
      """
      return a string with the yaml (data) block
      """
      pass
    def update_item_content() -> str:
      """
      return a string with the updated content
      - note that item.content does not include the title
      """
      pass
    def form_updated_item_markdown(new_item_data: str, new_item_content: str) -> str:
      """
      return the updated markdown string to be passed into the item.
      
      markdown = "#"*level + title + new_item_data + new_item_content
      """
      return f"{'#'*old_item['level']} {old_item['title']}\n{new_item_data}\n{new_item_content}"
    # validate item exists
    if item_exists():
      print(f"\nitem {item_key} exists")
      print("update_item::old_item",old_item)
      new_item = {"title": old_item['title'], "markdown": old_item['markdown'], "path": old_item['path']}
      if item_data is not None:
        print("update_item_data::item_data", item_data)
        # update the structured data of the item
          # find the structured data block token
          # replace the old data content with the new data content
        # open the markdown of the existing item, find the structured data block, and replace the content
        new_item_data = sdoc.set_codefenced_data(new_item, item_data)
        print("update_item::new_item_data", new_item_data)
        pass
      if item_content is None:
        new_item_content = "" 
      else:
        new_item_content = item_content
      
      new_item['markdown'] = form_updated_item_markdown(new_item_data,new_item_content)
      print("update_item::new_item", new_item)
      crud.put_item(self.path_str, item_key, new_item, self.shelly_docs_obj)
      self.state = self.yaml.load(self.state_file.read_text())

    else:
      raise ValueError(f"Item {item_key} does not exist")
  
  def delete_item(self, item_key):
    pass

  def reparent_item(self, item_key, new_parent_item_key):
    pass

  def query(self, query_obj):
    """
    Run a shelly docs query. uses the mongodb like syntax
    Accepts a string (formatted as YAML), python list, or python dict
    """
    pass
  
class Item:
  def __init__(self, key):
    self.key = key
    self.data
    self.content