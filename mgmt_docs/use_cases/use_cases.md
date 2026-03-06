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
```yaml (metadata)
status: done
```
```bash
shelly-docs items list --path "path"
```
# USECASE-8 Get an Item via CLI
```yaml (metadata)
status: ready
```
```bash
shelly-docs item get "item_key"
```
# USECASE-9 Set Knowledge Base Config via CLI
```yaml (metadata)
status: done
```
```bash
shelly-docs kb set --path "path_to_kb_directory" # reads the `shellydocs.yaml` file at the directory pathto setup the Knowledge Base config
# defaults to the current directory if no directory is provided
```
# USECASE-10 Add/Update an Item via CLI
```yaml (metadata)
status: ready
```
Generally, we'd expect an agent to write Items by using markdown, but we should also allow a way to update items using json. 
```bash
shelly-docs item put "path_to_json" # put an item to the KB using JSON
```
# USECASE-11 Delete an Item Via CLI
```yaml (metadata)
status: ready
```
```bash
shelly-docs item delete "item_key"
```

# USECASE-12 Add Metadata to Items
```yaml (metadata)
status: drafting
```
# USECASE-13 Query Items based on Metadata
```yaml (metadata)
status: drafting
```
Search for Items based on the Metadata

# USECASE-14 Semantic Search for Items
```yaml (metadata)
status: future
```
Search for Items based on semantic similarity to a question. (effectively do RAG)

# USECASE-15 Refresh Knowledge Base State
```yaml (metadata)
status: ready
```
Read all the Items in the Knowledge Base.
```bash
shelly-docs kb update
```

# USECASE-16 Enter TUI
```yaml (metadata)
status: done
```
Enter the TUI from a CLI Command
```bash
shelly-docs tui
```
