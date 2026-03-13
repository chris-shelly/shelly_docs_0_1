# SYSTEM-3 Backend (`be/`)
```yaml (data)
status: done
```
## SYSTEM-3-1 CRUD (`crud/crud.py`)
```yaml (data)
depends_on:
  - SYSTEM-3-3
```
Module for making updates to items and keeping the state updated.
### SYSTEM-3-1-1 `get_items()`
Get a List of items
### SYSTEM-3-1-2 `write_items_to_state()`
```yaml (data)
depends_on:
  - SYSTEM-3-1-1
```
Get the Items and then write the updates to `state.yaml`
### SYSTEM-3-1-3 `get_state()`
Read the state file to get a python dict of the item state
### SYSTEM-3-1-4 `get_item()`
```yaml (data)
depends_on:
  - SYSTEM-3-1-4
```

### SYSTEM-3-1-5 `put_item()`
```yaml (data)
depends_on:
  - SYSTEM-3-1-3
  - SYSTEM-3-1-1
  - SYSTEM-3-1-6
```
Create or Update Items, intended to be idempotent.

### SYSTEM-3-1-6 `get_sibling_positioning()`
Determine where exactly to put an it

### SYSTEM-3-1-7 `delete_item()`
Delete a given item from the markdown docs and state

### SYSTEM-3-1-8 `get_md_docs_in_dir()`
Recursively detect Markdown DOcuments to check for `Item`s


## SYSTEM-3-2 Query (`crud/query.py`)
Query Engine/Module for filtering and/or aggregating `Item`s by their `data` field.

### SYSTEM-3-2-1 `query_items()`
```yaml (data)
depends_on:
  - SYSTEM-3-2-3
  - SYSTEM-3-2-4
```
Apply a query step to the items against their `data` field.

### SYSTEM-3-2-2 `query_pipeline()`
```yaml (data)
depends_on:
  - SYSTEM-3-2-1
```
Evaluate a list (AKA YAML sequence, AKA JSON array) of queries on the Items based on the order the query steps are declared.

### SYSTEM-3-2-3 `match_item()`
Evaluates Logical Conditions to filter Items

Important Query logical keywords:
- `$ne`
- `$gt`
- `$gte`
- `$lt`
- `$lte`
- `$in`

### SYSTEM-3-2-4 `aggregate_items()`
Evaluates a list of Items to return a scalar result.

Important Query aggregating keywords:
- `$count`
- `$sum`
- `$concat`
## SYSTEM-3-3 Docs Processing (`crud/shelly_doc_processing.py`)
### SYSTEM-3-3-1 `process_shelly_docs_items()`
```yaml (data)
subject_to_future_refactor: true
```
Given a file path process the `Item`s within a file.

### SYSTEM-3-3-2 `prep_new_shelly_doc_items_from_document_update()`
```yaml (data)
related_to:
  - SYSTEM-3-3-1
subject_to_future_refactor: true
```
Used to convert a New Item object, which holds a kb path, filepath, and the raw markdown, into fully processable items.



## SYSTEM-3-4