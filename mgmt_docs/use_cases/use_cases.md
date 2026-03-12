# USECASE-1 Human gets list of Items
Human uses the TUI to view the Items in their Knowledge Base.
```yaml (data)
status: done
```
# USECASE-2 Human reads an Item
Human uses the TUI to view a specific Item in the Knowledge Base.
```yaml (data)
status: done
```
# USECASE-3 Human sets the Knowledge Base Config
Human opens a project in the TUI by specifying the directory for the Knowledge Base.
```yaml (data)
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
```yaml (data)
status: done
```
# USECASE-5 Human updates an Item
Human uses the TUI to update an existing Item
```yaml (data)
status: done
```
# USECASE-6 Human deletes an Item
Human uses TUI to delete an Item
```yaml (data)
status: done
```

# USECASE-7 Get List of Items via CLI
```yaml (data)
status: done
```
```bash
shelly-docs items list --path "path"
```
# USECASE-8 Get an Item via CLI
```yaml (data)
status: done
```
```bash
shelly-docs item get "item_key"
```
# USECASE-9 Set Knowledge Base Config via CLI
```yaml (data)
status: done
```
```bash
shelly-docs kb set --path "path_to_kb_directory" # reads the `shellydocs.yaml` file at the directory pathto setup the Knowledge Base config
# defaults to the current directory if no directory is provided
```
# USECASE-10 Add/Update an Item via CLI
```yaml (data)
status: done
```
Generally, we'd expect an agent to write Items by using markdown, but we should also allow a way to update items using json. 
```bash
shelly-docs item put "file.md" "# DESIGN-3 Capture Data
Capture Data from user input" 
# put an item to the KB using JSON
```
Format of an item
- filepath is relative to the Knowledge Base Path
```json
{
  "filepath": "file.md",
  "markdown": "# DESIGN-3 Capture Data \n Capture Data from user input"
}
```

# USECASE-11 Delete an Item via CLI
```yaml (data)
status: done
depends_on: USECASE-15
```
```bash
shelly-docs item delete "item_key"
```

# USECASE-12 Add Data to Items
```yaml (data)
status: done
related_to: DESIGN-2-2
```
As seen above, allow Items to have structured data that can be analyzed and queried.

Data on a given item is provided using a yaml `data` code block.

Data is then saved in the state of the knowledge base, where the item has a field called `"data"`, which contains the object defined from the yaml code block.

By default, at least the 'type' will be added to the data object, but it can be overwritten by a type specified in the code fence.


# USECASE-13 Query Items based on `Item.data`
```yaml (data)
status: done
```
Search for Items based on their `data` field.
An Item object has data from codefences stored in the 'data' object in the state file.

We can then query that data from the state file by iterating through the items and checking logical conditions

A query can be formatted with mongodb-like objects
```yaml
# format
<field>: <query_obj> # scalar for a single value, or a mapping for checking several conditions

# query for status of done
status: done
# ...
# query conditionals
points:
  $gte: 3
  $lte: 8
$or:
  - status: drafting
  - winner: true
```

# USECASE-14 Semantic Search for Items
```yaml (data)
status: future
```
Search for Items based on semantic similarity to a question. (effectively do RAG)

# USECASE-15 Refresh Knowledge Base State
```yaml (data)
status: done
```
Read all the Items in the Knowledge Base.
```bash
shelly-docs kb update
```

# USECASE-16 Enter TUI
```yaml (data)
status: done
```
Enter the TUI from a CLI Command
```bash
shelly-docs tui
```

# USECASE-17 Aggregate Queried Items
```yaml (data)
status: done
related_to: DESIGN-2-2
```
Given a user has queried some items, let them aggregate that data.

For example, if the user wants to know how many items are of a certain "status" value.

How about we enable "pipelines", where each part of the query is run in sequence.

```yaml
# status_query.yaml
- status: done # gets the items that have a status done
- $count # then, counts those items
```

```bash
# query the items
shelly-docs items query --query "$(cat status_query.yaml)"

```