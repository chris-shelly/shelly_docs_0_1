# given a directory path, read all the markdown docs, returning a list of objects representing information about those docs
from pathlib import Path
import re
from ruamel.yaml import YAML

yaml = YAML()

def get_config():
  # a project is initialized in a directory by reading from a shellydocs.yaml file
  # that yaml file provides
    # the path to read from to search for docs
    # the title tags
  print(f"--- get_config()")
  shelly_docs_config = yaml.load(Path("shellydocs.yaml").read_text())
  return shelly_docs_config
