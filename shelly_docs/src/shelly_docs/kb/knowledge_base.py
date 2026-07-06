from pathlib import Path
import sys

from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

from ..be.crud.crud import put_item
from ..be.crud.shelly_doc_processing import get_tag_from_title


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
    print(self.shelly_docs_obj)
    state_file = self.path / "state.yaml"
    self.state = self.yaml.load(state_file.read_text())
  
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
        if get_tag_from_title(parent_item.get("title")) != item_type:
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
      pass
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
      put_item(self.path_str, item_key, item_dict, self.shelly_docs_obj)

  def get_item(self, item_key: str) -> dict:
    """
    Given the item key (ex. 'TASK-11'), get an existing Item from the KB
    """
    return self.state.get('items').get(item_key)

    
  
  def update_item(self, item_key, item_data, item_content):
    """
    Used to update an entire item

    If wanting to update specific keys in the data block: recommended to use `Item.set_data()`

    If wanting to add to the item content: recommended to use `Item.set_content()`
    """
    pass
  
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