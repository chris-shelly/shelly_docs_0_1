from contextlib import chdir
from pathlib import Path
import runpy
from rich import print

from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

from ..be.crud import crud as crud
from ..be.crud import md_handling as mdh
from ..be.crud import shelly_doc_processing as sdoc
from ..be.crud import query as qry


class MyYAML(YAML):
  def dump(self, data, stream=None, **kw):
    inefficient = False
    if stream is None:
      inefficient = True
      stream = StringIO()
    YAML.dump(self, data, stream, **kw)
    if inefficient:
      return stream.getvalue()

def make_item_key(kb: KnowledgeBase, parent_key: str, item_type: str) -> str:
  """
  Determine the correct key for a new item being created that does not yet have a key
  """
  ids = kb.state.get('ids')
  if parent_key:
    # check for the parent in 'ids' and find `ids.{{item_type}}.{{parent_key}}.next`
    return ids.get(item_type).get(parent_key).get("next")
  else:
    # check for the next available under that item type (`ids.{{item_type}}.next`)
    return ids.get(item_type).get("next")


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
  
  def create_item(self, file, item_type, item_name: str, item_data, item_content, parent_key=None) -> Item:
    """
    Create an Item, adding it to the Knowledge Base
    """
    # given the item type (and parent) determine what the key should be
    def make_item_dict(item_key):
      """
      to create the item, we need to make a python dictionary out of the data

      needs:
      - 'title' (includes key and name, ex. "ABC-99 Brand New")
      - 'markdown' ()
      - 'path' (target .md file)
      """
      # if there's a parent item in the same file, must add the appropriate number of hashtags to the heading
        # check if there's a parent
        # if so, check if it's in the same file
        # the level of this item will be one deeper than that of its parent
          # recall that 'level' referes to depth in a file, not about the number of parents it has.
      level = 1
      if (parent_key is not None):
        parent = self.state.get('items',{}).get(parent_key,None)
        #print("parent.get('path')", parent.get('path'))
        #print("file",file)
        if parent.get('path').split("#")[0] == file:
          level = parent.get('level') + 1
      # build the correct title
      return {
        "title": f"{item_key} {item_name.strip("\n")}", # strip new lines
        "markdown": f"{"#"*level} {item_key} {item_name.strip("\n")}\n```yaml (data)\n{self.yaml.dump(item_data)}```\n{item_content}", # raw content
        "path": file
        } 
    def valid_item_type():
      return (item_type in self.shelly_docs_obj.get('item_tags'))
    # config refers to the shellydocs.yaml we use to verify item types
    
    item_key = make_item_key(self,parent_key,item_type)
    item_dict = make_item_dict(item_key)
    #print(item_dict)
    if valid_item_type():
      #print("creating item")
      crud.put_item(self.path_str, item_key, item_dict, self.shelly_docs_obj)

    # update state after writing
    crud.write_items_to_state(self.path_str)
    self.state = self.yaml.load(self.state_file.read_text())
    return self.get_item(item_key)

  def get_item(self, item_key: str) -> Item:
    """
    Given the item key (ex. 'TASK-11'), get an existing Item from the KB
    """
    item_dict = self.state.get('items',{}).get(item_key,None)
    if item_dict:
      return Item(item_dict, self)
    else:
      return None

  def update_state(self):
    """
    Update the Knowledge Base State, so that queries and item CRUD use up-to-date data
    """
    crud.write_items_to_state(self.path_str)
    self.state = self.yaml.load(self.state_file.read_text())
  
  def update_item(self, item_key, item_data=None, item_content=None):
    """
    DEPRECATED
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
    def form_updated_item_markdown(new_item_data: str, new_item_content: str) -> str:
      """
      return the updated markdown string to be passed into the item.
      
      markdown = "#"*level + title + new_item_data + new_item_content
      """
      return f"{'#'*old_item['level']} {old_item['title']}\n{new_item_data}\n{new_item_content}"
    # validate item exists
    if item_exists():
      #print(f"\nitem {item_key} exists")
      #print("update_item::old_item",old_item)
      new_item = {"title": old_item['title'], "markdown": old_item['markdown'], "path": old_item['path']}
      if item_data is not None:
        #print("update_item_data::item_data", item_data)
        # update the structured data of the item
          # find the structured data block token
          # replace the old data content with the new data content
        # open the markdown of the existing item, find the structured data block, and replace the content
        new_item_data = sdoc.set_codefenced_data(new_item, item_data)
        #print("update_item::new_item_data", new_item_data)
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
    """
    Delete an Item, letting us remove it from the Knowledge Base and State
    """
    crud.delete_item(self.path_str, item_key)
    self.state = self.yaml.load(self.state_file.read_text())

  def run_jobs(self):
    """
    Run the jobs based on the job objects from `shellydocs.yaml`

    Jobs run with the Knowledge Base directory as the working directory, so
    relative paths inside a job script resolve against the KB rather than
    against wherever `shelly-docs` was invoked. `kb_path` is also injected
    into the script's globals for scripts that prefer absolute paths.
    """
    print("KnowledgeBase::running jobs")
    jobs: list[dict] = self.shelly_docs_obj.get("jobs") or []
    items: dict[str, dict] = self.state.get("items") or {}
    # resolve up front: chdir would change what a relative KB path means
    kb_dir = self.path.resolve()
    for job in jobs:
      if job.get("active") == False:
        continue
      script_path = (kb_dir / job.get("script")).resolve()
      if not script_path.is_file():
        raise FileNotFoundError(f"job '{job.get('name')}': script not found at {script_path}")
      if job.get("job_type") == "item":
        for item in items.values():
          if item.get("type") not in job.get("item_types", []):
            continue
          init_globals = {"item": item, "kb_path": str(kb_dir)}
          with chdir(kb_dir):
            runpy.run_path(str(script_path), init_globals, job.get("name"))
      elif job.get("job_type") == "query":
        # get the query based on the path provided in the job object
        
        with chdir(kb_dir):
          query = self.query(Path(job.get("query")).read_text())
          init_globals = {"query": query, "kb_path": str(kb_dir)}
          runpy.run_path(str(script_path), init_globals, job.get("name"))
  def run_job(self, job_name: str):
    """
    Run a specific job within the knowledge base.

    Runs every job that matches `job_name` within the `state.yaml::jobs` array
    """
    jobs: list[dict] = self.shelly_docs_obj.get("jobs") or []
    items: dict[str, dict] = self.state.get("items") or {}
    # resolve up front: chdir would change what a relative KB path means
    kb_dir = self.path.resolve()
    for job in jobs:
      if job.get("name") == job_name:
        script_path = (kb_dir / job.get("script")).resolve()
        print(f"KnowledgeBase::running job - {job_name}")
        if not script_path.is_file():
          raise FileNotFoundError(f"job '{job.get('name')}': script not found at {script_path}")
        if job.get("job_type") == "item":
          for item in items.values():
            if item.get("type") not in job.get("item_types", []):
              continue
            init_globals = {"item": item, "kb_path": str(kb_dir)}
            with chdir(kb_dir):
              runpy.run_path(str(script_path), init_globals, job.get("name"))
        elif job.get("job_type") == "query":
          # get the query based on the path provided in the job object
          
          with chdir(kb_dir):
            query = self.query(Path(job.get("query")).read_text())
            init_globals = {"query": query, "kb_path": str(kb_dir)}
            runpy.run_path(str(script_path), init_globals, job.get("name"))

  def query(self, query_obj):
    """
    Run a shelly docs query. uses the mongodb like syntax
    Accepts a string (formatted as YAML), python list, or python dict
    """
    if isinstance(query_obj, str):
      parsed_query = self.yaml.load(query_obj)
    else:
      parsed_query = query_obj
    try:
      if isinstance(parsed_query, dict):
        results = qry.query_items(self.state.get("items"), parsed_query)
      elif isinstance(parsed_query, list):
        results = qry.query_pipeline(self.state.get("items"), parsed_query)
    except ValueError as e:
      print(f"Error: {e}")
    return {"results": results, "query": parsed_query}
  
class Item:
  def __init__(self, item_state_dict, kb):
    # we know the markdown must be the first line
    self.heading: str = item_state_dict.get('markdown','').splitlines()[0] # the Markdown Heading that triggers the start of the item
    self.data: dict = item_state_dict.get('data',None) # structured data that we can query
    self.type: str = item_state_dict.get('type', '')
    self.content: str = item_state_dict.get('content','') # other 'unstructured' content
    self.markdown: str = item_state_dict.get('markdown')
    self.title: str = item_state_dict.get('title')
    self.file: Path = Path(item_state_dict.get('path',''))
    self.parent_key = item_state_dict.get('parent', None)
    self.kb: KnowledgeBase = kb
  def set_data(self, new_data: dict):
    """
    Sets the Item's data block
    """
    updated_item_markdown = mdh.set_data_block(self.markdown, new_data)
    updated_item_dict = {
      "title":  self.title,
      "markdown": updated_item_markdown,
      "path": str(self.file)
    }
    print(updated_item_dict)
    crud.put_item(str(self.kb.path),self.title.split(" ")[0],updated_item_dict,self.kb.shelly_docs_obj)
    self.kb.update_state()
  def set_content(self, new_content: str):
    """
    Sets the Item's content
    """
    updated_item_markdown = mdh.set_content(self.markdown, new_content)
    updated_item_dict = {
      "title":  self.title,
      "markdown": updated_item_markdown,
      "path": str(self.file)
    }
    print(updated_item_dict)
    crud.put_item(str(self.kb.path),self.title.split(" ")[0],updated_item_dict,self.kb.shelly_docs_obj)
    self.kb.update_state()
  def set_file(self, new_file: str):
    """
    Moves the Item to a new file
    """
    # moves the item to this file (append to the end of the file by default, recalculates heading level based on parent presence)
      # copy the item dict
      # delete the item from the original file
      # add to the new file
    item_copy_dict = {
      "title": self.title,
      "markdown": self.markdown.strip(),
      "path": new_file
    }
    self.kb.delete_item(self.title.split(" ")[0])
    crud.put_item(str(self.kb.path),self.title.split(" ")[0],item_copy_dict,self.kb.shelly_docs_obj)
    self.file = new_file
    self.kb.update_state()
  def reparent(self, new_parent_key: str|None, new_item_type: str|None):
    """
    Moves an Item to be a child of a different item

    When the Knowledge Base state gets updated this child's items (i.e. the new grandchildren of the new parent item) shall get updated automatically
    """
    # reparents this item, updating this item's key and keys of the children
    # determine new item key
    new_item_key = ""
    if new_parent_key:
      new_item_key = make_item_key(self.kb, new_parent_key, new_parent_key.split("-")[0])
    else:
      new_item_key = make_item_key(self.kb, None, new_item_type)
    new_title = f"{new_item_key} {self.title.split(" ",1)[1]}"
    def determine_item_level():
      """
      to create the item, we need to make a python dictionary out of the data

      needs:
      - 'title' (includes key and name, ex. "ABC-99 Brand New")
      - 'markdown' ()
      - 'path' (target .md file)
      """
      # if there's a parent item in the same file, must add the appropriate number of hashtags to the heading
        # check if there's a parent
        # if so, check if it's in the same file
        # the level of this item will be one deeper than that of its parent
          # recall that 'level' referes to depth in a file, not about the number of parents it has.
      level = 1
      if (new_parent_key is not None):
        parent = self.kb.state.get('items',{}).get(new_parent_key,None)
        #print("parent.get('path')", parent.get('path'))
        #print("file",str(self.file))
        if parent.get('path').split("#")[0] == str(self.file).split("#")[0]:
          level = parent.get('level') + 1
      # build the correct title
      ##print(level)
      return level
    item_copy_dict = {
      "title": f"{new_item_key} {self.title.split(" ",1)[1]}",
      "markdown": f"{'#'*determine_item_level()} {new_title}\n{"\n".join(self.markdown.splitlines()[1:])}",
      "path": str(self.file).split("#")[0]
    }
    self.kb.delete_item(self.title.split(" ")[0])
    self.title = f"{new_item_key} {self.title.split(" ",1)[1]}"
    key = self.title.split(" ")[0]
    self.heading = f"{'#'*determine_item_level()} {new_title}"
    self.markdown = f"{new_title}\n{"\n".join(self.markdown.splitlines()[1:])}"
    self.parent_key = new_parent_key
    print("Item.reparent()::item_copy_dict",item_copy_dict)
    crud.put_item(str(self.kb.path),key,item_copy_dict,self.kb.shelly_docs_obj)
    self.kb.update_state()
  
  def rename(self, new_name: str):
    """
    Update the 'name' of an item
    - does not change the item key
    """
    # updates the 'name' of this item (does not impact the item key. for ex. renaming 'ABC-1 X' to 'ABC-1 Y')
    new_title = f"{self.title.split(" ")[0]} {new_name}"
    item_copy_dict = {
      "title": new_title,
      "markdown": f"{self.heading.split(" ")[0]} {new_title}\n{"\n".join(self.markdown.splitlines()[1:])}",
      "path": str(self.file).split("#")[0]
    }
    self.kb.delete_item(self.title.split(" ")[0])
    self.title = new_title
    key = self.title.split(" ")[0]
    self.heading = f"{self.heading.split(" ")[0]} {new_title}"
    self.markdown = f"{key}\n{"\n".join(self.markdown.splitlines()[1:])}"
    #print("Item.reparent()::item_copy_dict",item_copy_dict)
    crud.put_item(str(self.kb.path),key,item_copy_dict,self.kb.shelly_docs_obj)
    self.kb.update_state()