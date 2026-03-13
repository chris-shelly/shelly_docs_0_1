# given a directory path, read all the markdown docs, returning a list of objects representing information about those docs
from pathlib import Path
from ruamel.yaml import YAML

yaml = YAML()

def get_config(path: str):
  # a project is initialized in a directory by reading from a shellydocs.yaml file
  # that yaml file provides
    # the path to read from to search for docs
    # the title tags
  if path[-1] == '/':
    path = path[:-1]
  elif path[-1] == '\\':
    path = path[:-1]
  config_path = Path(path + "/shellydocs.yaml")
  try:
    shelly_docs_config = yaml.load(config_path.read_text())
  except FileNotFoundError:
    raise FileNotFoundError(f"shellydocs.yaml not found at '{config_path}'. Is this a valid Knowledge Base directory?")
  except Exception as e:
    raise ValueError(f"Failed to parse shellydocs.yaml at '{config_path}': {e}")
  return shelly_docs_config
