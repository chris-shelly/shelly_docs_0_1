import typer
from pathlib import Path
from rich import print

from .tui.tui import ShellyDocs
from .be.crud.crud import get_items
from .be.shelly_docs_config.config import get_config

app = typer.Typer()

kb_app = typer.Typer()
app.add_typer(kb_app, name="kb")

items_app = typer.Typer()
app.add_typer(items_app, name="items")

APP_NAME = "shelly_docs"

DEFAULT_KB_PATH = "."


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
def kb_set(path: str = ""):
  """
  Set a directory to read the knowledge base from.
  """
  typer.echo("setting Knowledge Base Path")
  app_dir = typer.get_app_dir(APP_NAME)
  config_path = Path(app_dir) / "kb_path.txt"
  if not config_path.is_file():
    typer.echo("Knowledge Base Path doesn't exist yet, creating path")
    # ensure parent directories exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
  # puts the kb path to the 'kb_path.txt' file
  if path:
    typer.echo(f"Setting {path} as Knowledge Base Path")
    config_path.write_text(path)
  else:
    typer.echo(f"Setting default Knowledge Base Path, {DEFAULT_KB_PATH}")
    config_path.write_text(DEFAULT_KB_PATH)
  typer.echo("Knowledge Base Path has been set")
  
@items_app.command("list")
def items_list(path: str = ""):
  """
  List all Items in a knowledge base
  """
  app_dir = typer.get_app_dir(APP_NAME)
  config_path = Path(app_dir) / "kb_path.txt"
  kb_path = config_path.read_text()
  items_path = Path(kb_path) / path
  print(get_items(path=items_path,config=get_config(kb_path)))

