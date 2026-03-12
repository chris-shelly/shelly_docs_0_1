# PROMPT-12 Update `state.yaml` Paths
## `Role`
You are a Senior Python Engineer with expertise in creating markdown-based dev tools.
## `Background`
We updated the way `Item.path` is calculated, now using relative path from the Knowledge Base, so that absolute paths aren't forcibly stored within the the markdown documents.
Now we have 6 failing tests in `test_crud.py`
```
================ short test summary info ================
FAILED shelly_docs/tests/test_crud.py::TestPutItem::test_update_existing_item - ValueError: Item 'ABC-1' already exists in a differen...
FAILED shelly_docs/tests/test_crud.py::TestGetSiblingPositioning::test_finds_sibling_end_line - assert None is not None
FAILED shelly_docs/tests/test_crud.py::TestDeleteItem::test_removes_item_from_file - FileNotFoundError: Document not found: input_a.md
FAILED shelly_docs/tests/test_crud.py::TestDeleteItem::test_state_updated - FileNotFoundError: Document not found: input_a.md
FAILED shelly_docs/tests/test_crud.py::TestConvertNewItemMD::test_converts_single_item - KeyError: 'kb_path'
FAILED shelly_docs/tests/test_crud.py::TestConvertNewItemMD::test_converts_multiple_items - KeyError: 'kb_path'
============= 6 failed, 34 passed in 0.71s ==============
```
## `Goal`
Identify the root cause of the issue and plan a fix.

## `Root Cause Analysis`
-`crud.py`
  - in `put_item()` path resolves against current working directory instead of the directory from within knowledge base
    - fix by prepending KB path before resolving
  - in `get_sibling_positioning()`, path is comparing between absolute and relative paths
    - fix, normalize both paths
  - in `delete_item()`, Path is checked against the current workign directory
    - fix by prepending KB Path
- `shelly_doc_processing.py`
  - ``config['kb_path']`` doesn't exist
  - use `new_item_obj['kb_path']` instead
- tests
  - tests need updating to pass relative paths, rather than absolute ones.

