# PROMPT-11 Build Unit Tests for `crud` functions
Working on Creating Unit Tests for our `be.crud` functions
## PROMPT-11-1 Research how `crud` module is Used
### Role
You are Senior Python Engineer with extensive experience developing tests for Python applications using `pytest`.
### Goal
Research how the functions are used in `be/crud.py`.
### Research Summary (output)
#### Functions
- ``get_items()``
  - entry point to find .md files, and extract items
  - calls `process_shelly_docs_items()`
- `write_items_to_state(path)`
  - builds the state dictionary and writes `state.yaml`
  - calls `get_items()`
- `get_state(path)`
  - reads `state.yaml`, returinign it as a dict
- `get_item()`
  - gets a single item from the state by key
- `put_item()`
  - adds or updates an item in the markdown file, and updates state
- `delete_item()`
  - removes item from markdown, updates state
- `convert_new_item_md()`
  - wrapper around `prep_new_shelly_doc_items_from_document_update()`
- `get_sibling_positioning(state, item)`
  - finds the insert position among siblings for new child ites
- `get_md_docs_in_dir()`
  - recursively finds `.md` files
- `parse_md_text()` and `parse_md_doc()`
  - markdown-to-ast parsing
#### Key Obsevations for testing
- most functions depend on filesystem state
- existing test scaffold
- two consumers of `crud.py`, ``main.py`` and ``tui.py``
- `put_item()` is among the most complex functions
- `write_items_to_state()` is called with only `path`
#### Changes since prompt was ran
- `crud.heading_to_anchor()` has been deleted since it's not used and is a duplicates `shelly_doc_processing.heading_to_anchor()`

## PROMPT-11-2 Plan Testing for `crud`
### Role
You are Senior Python Engineer with extensive experience developing tests for Python applications using `pytest`.
### Background, Research from PROMPT-11-1
#### Functions
- ``get_items()``
  - entry point to find .md files, and extract items
  - calls `process_shelly_docs_items()`
- `write_items_to_state(path)`
  - builds the state dictionary and writes `state.yaml`
  - calls `get_items()`
- `get_state(path)`
  - reads `state.yaml`, returinign it as a dict
- `get_item()`
  - gets a single item from the state by key
- `put_item()`
  - adds or updates an item in the markdown file, and updates state
- `delete_item()`
  - removes item from markdown, updates state
- `convert_new_item_md()`
  - wrapper around `prep_new_shelly_doc_items_from_document_update()`
- `get_sibling_positioning(state, item)`
  - finds the insert position among siblings for new child ites
- `get_md_docs_in_dir()`
  - recursively finds `.md` files
- `parse_md_text()` and `parse_md_doc()`
  - markdown-to-ast parsing
#### Key Obsevations for testing
- most functions depend on filesystem state
- existing test scaffold
- two consumers of `crud.py`, ``main.py`` and ``tui.py``
- `put_item()` is among the most complex functions
- `write_items_to_state()` is called with only `path`
### Goal
Develop a plan for testing `crud.py` as a Markdown file.


## PROMPT-11-3 Develop Tests for `crud`
### Notes on Updates/Bugs discovered during testing
Bug fixes in shelly_doc_processing.py
- Missing `tags` argument
- Off-by-one in heading validation
- Config ordering, we need to call get_config() before the function that needs the tags