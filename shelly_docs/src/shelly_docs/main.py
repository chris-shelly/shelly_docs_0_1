import typer
import json as jsn
from pathlib import Path
from rich import print
from rich.markdown import Markdown
from ruamel.yaml import YAML

from .tui.tui import ShellyDocs
from .be.crud.crud import get_items, get_item, get_state, put_item, convert_new_item_md, delete_item, write_items_to_state
from .be.crud.query import query_items, query_pipeline
from .be.shelly_docs_config.config import get_config

app = typer.Typer()

kb_app = typer.Typer()
app.add_typer(kb_app, name="kb")

items_app = typer.Typer()
app.add_typer(items_app, name="items")

item_app = typer.Typer()
app.add_typer(item_app, name ="item")

APP_NAME = "shelly_docs"

DEFAULT_KB_PATH = "."


def get_kb_path():
  app_dir = typer.get_app_dir(APP_NAME)
  config_path = Path(app_dir) / "kb_path.txt"
  kb_path = config_path.read_text()
  return kb_path
@app.callback()
def callback():
  """
  Shelly Docs
  """

@app.command()
def tui():
  """
  Open the Shelly Docs TUI
  """
  typer.echo("Opening Shelly Docs TUI")
  tui_app = ShellyDocs()
  tui_app.run()

@kb_app.command("set")
def kb_set(path: str = "", json: bool = True):
  """
  Set a directory to read the knowledge base from.
  """
  if not json:
    typer.echo("setting Knowledge Base Path")
  app_dir = typer.get_app_dir(APP_NAME)
  config_path = Path(app_dir) / "kb_path.txt"
  if not config_path.is_file():
    if not json:
      typer.echo("Knowledge Base Path doesn't exist yet, creating path")
    # ensure parent directories exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
  # puts the kb path to the 'kb_path.txt' file
  if path:
    if not json:
      typer.echo(f"Setting {path} as Knowledge Base Path")
    config_path.write_text(path)
  else:
    if not json:
      typer.echo(f"Setting default Knowledge Base Path, {DEFAULT_KB_PATH}")
    config_path.write_text(DEFAULT_KB_PATH)
  if not json:
    typer.echo("Knowledge Base Path has been set")
  else:
    print({"message": "Knowledge Base Path has been set", "kb_path": config_path.read_text()})


@kb_app.command("get")
def kb_get(json: bool = True):
  """
  Get the current knowledge base path setting.
  """
  kb_path = get_kb_path()
  if json:
    print(jsn.dumps({"kb_path": kb_path}))
  else:
    typer.echo(kb_path)

@kb_app.command("update")
def kb_update(json: bool = True):
  """
  Update the the state of the Knowledge Base.

  Captures all items from the current Knowledge Base.
  """
  kb_path = get_kb_path()
  write_items_to_state(kb_path)
  if json:
    print(jsn.dumps({ "message": f"state updated for knowledge base {kb_path}"}))
  else:
    typer.echo(f"state updated for knowledge base {kb_path}")
  
@items_app.command("list")
def items_list(path: str = "", json: bool = True):
  """
  List all Items in a knowledge base
  """
  kb_path = get_kb_path()
  items_path = Path(kb_path) / path
  if json:
    print(jsn.dumps({"items": get_items(path=items_path,config=get_config(kb_path))}))
  else:
    print(get_items(path=items_path,config=get_config(kb_path)))

@items_app.command("query")
def items_query(query: str = typer.Option(..., help="YAML query string, e.g. 'status: done'"), json: bool = True):
  """
  Query Items by their data fields. Uses MongoDB-inspired query syntax for each query object.

  Can optionally chain a list of queries together as a pipeline

  Examples:
    shelly-docs items query --query "status: done"
    shelly-docs items query --query "priority: {$gt: 3}"
    shelly-docs items query --query '$or: [{status: done}, {status: drafting}]'
    shelly-docs items query --query "- status: done\n - $count"
    shelly-docs items query --query "$(cat my_query.yaml)"
  """
  kb_path = get_kb_path()
  yaml = YAML()
  try:
    parsed_query = yaml.load(query)
  except Exception as e:
    print(f"Error parsing query YAML: {e}")
    raise typer.Exit(code=1)
  if not ((isinstance(parsed_query, dict)) or (isinstance(parsed_query, list))) :
    print("Error: query must be a YAML mapping (e.g. 'status: done') or YAML sequence (e.g. '- status: done\n- related_to: DESIGN-2-2')")
    raise typer.Exit(code=1)
  state = get_state(kb_path)
  try:
    if isinstance(parsed_query, dict):
      results = query_items(state["items"], parsed_query)
    elif isinstance(parsed_query, list):
      results = query_pipeline(state["items"], parsed_query)
  except ValueError as e:
    print(f"Error: {e}")
    raise typer.Exit(code=1)
  if json:
    print(jsn.dumps({"results": results, "query": parsed_query}, indent=2, default=str))
  else:
    print(results)

@item_app.command("get")
def item_get(item_key: str, json: bool = True):
  """
  Get an Item from the Knowldege Base by it's item key. In JSON format.
  """
  kb_path = get_kb_path()
  if json:
    print(jsn.dumps(get_item(kb_path,item_key)))
  else:
    print(get_item(kb_path,item_key))

@item_app.command("put")
def item_put(path: str, markdown: str, json: bool = True):
  """
  Put an Item and some markdown

  - path is the destination path for the Item, relative to the Knowledge Base Path
  - markdown is the markdown content
  """
  kb_path = get_kb_path()
  raw_item = {"filepath": path, "markdown": markdown, "kb_path": kb_path}
  semi_processed_items = convert_new_item_md(raw_item)
  added_item_keys = []
  for item in semi_processed_items:
    item_key = item['key']
    put_item(kb_path, item_key, item, get_config(kb_path))
    added_item_keys.append(item_key)
  if json:
    print(jsn.dumps({"added_items": added_item_keys}))
  else:
    print(f"added items: {added_item_keys}")
    

@item_app.command("delete")
def item_delete(item_key: str, json: bool = True):
  """
  Delete an Item from the Knowldege Base by it's Item Key.
  """
  kb_path = get_kb_path()
  delete_item(kb_path, item_key)
  if json:
    print(jsn.dumps({"message": f"deleted item {item_key}"}))
  else:
    print(f"{item_key} deleted from Knowledge Base {kb_path}")