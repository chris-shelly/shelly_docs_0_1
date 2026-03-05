# USECASE-1 Human gets list of Items
Human uses the TUI to view the Items in their Knowledge Base.
```yaml (metadata.yaml)
status: done
```
# USECASE-2 Human reads an Item
Human uses the TUI to view a specific Item in the Knowledge Base.
```yaml (metadata.yaml)
status: done
```
# USECASE-3 Human sets the Knowledge Base Config
Human opens a project in the TUI by specifying the directory for the Knowledge Base.
```yaml (metadata.yaml)
status: done
```
Human sets the configuration for the Knowledge base using a `shellydocs.yaml` file.
```yaml
item_tags: # tags to recognize as items
  - INPUT
  - DESIGN
  - REQ
```
Item Tags are used to detect items.

# USECASE-4 Human adds a new Item
Human uses the TUI to create a new Item
```yaml (metadata.yaml)
status: done
```
# USECASE-5 Human updates an Item
Human uses the TUI to update an existing Item
```yaml (metadata.yaml)
status: done
```
# USECASE-6 Human deletes an Item
Human uses TUI to delete an Item
```yaml (metadata.yaml)
status: done
```

# USECASE-7 Get List of Items via CLI
```bash
shelly_docs items list --path "path"
```
# USECASE-8 Get an Item via CLI
```yaml (metadata)
status: ready
```
```bash
shelly_docs item get "item_key"
```
# USECASE-9 Set Knowledge Base Config via CLI
```yaml (metadata)
status: ready
```
```bash
shelly_docs config set --path "path"
```
# USECASE-10 Add/Update an Item via CLI
```yaml (metadata)
status: drafting
```
Need to determine how tp provide the YAML content via CLI.
- realistically, it would be most efficient to let a User write markdown directly to a file in the directory.
- if it's an agent though, we could perhaps let them write it using a JSON object. 
```bash
shelly_docs item put "item_key"
```
# USECASE-11 Delete an Item Via CLI
```bash
shelly_docs item delete "item_key"
```

# USECASE-12 Add Metadata to Items
```yaml (metadata)
status: drafting
```
# USECASE-13 Query Items based on Metadata
```yaml (metadata)
status: drafting
```

# USECASE-14 Semantic Search for Items
```yaml (metadata)
status: future
```