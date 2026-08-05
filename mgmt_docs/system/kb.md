# SYSTEM-4 Knowledge Base Module (`kb/knowledge_base.py`)
```yaml (data)
depends_on:
- SYSTEM-3
```
Module for interacting with a Knowledge Base and Items.

## SYSTEM-4-1 `KnowledgeBase`
```yaml (data)
depends_on:
- SYSTEM-4-3
related_to:
- SYSTEM-5
component_type: class
attrs:
- yaml
- path
- path_str
- shelly_docs_obj
- state_file
- state
methods:
- create_item()
- get_item()
- update_state()
- update_item()
- delete_item()
- run_jobs()
- run_job()
- query()
```
Class for working with a Shelly Docs Knowledge Base


## SYSTEM-4-2 `Item`
```yaml (data)
component_type: class
depends_on: 
- SYSTEM-4-1
- SYSTEM-4-3
attrs:
- heading
- data
- type
- content
- markdown
- title
- file
- parent_key
- kb
methods:
- set_data()
- set_content()
- set_file()
- reparent()
- rename()
```
Class for working with Shelly Docs Items


## SYSTEM-4-3 `make_item_key()`
```yaml (data)
component_type: function
related_to:
- SYSTEM-5
```
Function used to read a knowledge base and determine the correct key for a new item being created that does not yet have one (i.e. if an item is being creaetd via kb.create_item())

Reads from the `KnowledgeBase.state` (`state.yaml::ids`), and then returns the next available ID
- If an Item has a parent, we check for the next available key under that parent
- else, we check for the next available key under that item type.


# SYSTEM-5 Knowledge Base (`{kb_path}/`)
```yaml (data)
component_type: data # data per user
```
A Shelly Docs Knowledge Base is a file folder that has:
- [`{kb_path}/shellydocs.yaml`](#system-5-1-shellydocsyaml)
  - acts as the root of the knowledge base folder
  - specifies the item types and jobs available in that knowledge base
- [`{kb_path}/state.yaml`](#system-5-2-stateyaml)
  - after running `shelly-docs kb update` or `KnowledgeBase.update_state()`, a `state.yaml` file is created in the Knowledge Base
  - holds data on the `items` and `ids`

## SYSTEM-5-1 `shellydocs.yaml`

## SYSTEM-5-2 `state.yaml`
