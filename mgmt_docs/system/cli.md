# SYSTEM-1 `shelly-docs` CLI
```yaml (data)
status: done
relates_to:
  - ACTOR-1
  - ACTOR-2
depends_on:
  - SYSTEM-3
```
Use a `typer` CLI, so that Users can work with docs from the command-line, enabling scripting, and automation with structured output.

## SYSTEM-1-1 `shelly-docs kb`
```yaml (data)
status: done
```
For working with the Knowledge Base
- Setting the Knowledge Base Path (`kb set`)
- Getting the current Knowledge Base Path (`kb get`)
- Updating the state of the Knowledge base (`kb update`)
## SYSTEM-1-2 `shelly-docs items`
```yaml (data)
status: done
```
For viewing Data of multiple items
- Getting a List of All items (`items list`)
- Querying the items (`items query`)
### SYSTEM-1-2-1 `items query`
```yaml (data)
status: done
```
Recall from DESIGN-2-1 that each item has a data field for saving structured data.

We can query the items based on that structure data with `shelly-docs items query` with a Mongo-DB inspired syntax, written as YAML (and therefore, also can work as JSON).

Can query the Knowledge base for values of certain types
```yaml
# get the items with 'status: done'
status: done
```


Keywords are prefixed with a `$` symbol.
```yaml
# non_done_items.yaml
# get the items with a 'status' field that is not equal to done.
status:
  $ne: done
```

Then we can reference a file to actually run ths query from YAML.
```bash
shelly-docs items query --query "$(cat non_done_items.yaml)"
```

Can make individual queries (a mapping) or can make query pipelines ( a sequence).

Aggregations are kinds of keywords used to get scalar results (number or string).

Aggregation Keywords include:
- `$count`
- `$sum`
- `$concat`

## SYSTEM-1-3 `shelly-docs item`
For working with a specific item, given its item key
- get an item (`item get`)
- put an item (`item put`)
  - Still recommended to write files directly, but can write them programmatically.
- delete an item (`item delete`)
