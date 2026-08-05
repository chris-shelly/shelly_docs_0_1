# `state.yaml`
A Shelly Docs Knowledge Base is a file folder that has:
- `{kb_path}/shellydocs.yaml`
- **`{kb_path}/state.yaml`**
  - after running `shelly-docs kb update` or `KnowledgeBase.update_state()`, a `state.yaml` file is created in the Knowledge Base
  - holds data on the `items` and `ids`
    - includes item content, keys, structured data, and what IDs are used in them

The `state.yaml` is what the Shelly Docs CLI and Python Library use when doing item CRUD operations. Almost all Knowledge Base operations must make updates to `state.yaml` in order to properly organize Items and handle updates.

**NEVER directly manipulate `state.yaml`**
- instead, use `shelly-docs kb update`(CLI) or `shelly_docs.kb.KnowledgeBase.update_state()`(python) yo keep the state updated
- CRUD operations (like `shelly_docs.kb.KnowledgeBase.create_item()`) will automatically make the appropriate updates to `state.yaml`