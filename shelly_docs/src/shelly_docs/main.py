import typer

from tui.tui import ShellyDocs

app = typer.Typer()

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