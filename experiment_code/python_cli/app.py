import typer

app = typer.Typer()

@app.command()
def greet(name: str, formal: bool = False):
  """Greet a user by name"""
  if formal:
    typer.echo(f"Good day, {name}.")
  else:
    typer.echo(f"Hello, {name}!")
  
if __name__ == "__main__":
  app()