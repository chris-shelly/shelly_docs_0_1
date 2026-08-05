# Queries
Queries in Shelly Docs let you use YAML and MongoDB-like syntax to search and aggregate items in a KnowledgeBase based on the Item's data block (`Item.data`).

Queries go through the state file and iterating through the items to check logical conditions

## Basic Querying Format
A query can be formatted with mongodb-like objects
```yaml
# format
<field>: <query_obj> # scalar for a single value, or a mapping for checking several conditions

# query for status of done
status: done
# ...
# query conditionals
points: # implied AND
  $gte: 3
  $lte: 8
$or:
  - status: drafting
  - winner: true
```
## Query Conditionals
Query Conditionals are used to apply logic to the data fields.


## Checking if a value is in an array
```yaml (data)
status: done
```
We allow searching for values in an array
When a query criteria applies to an array, it needs to check for the value.

Say we had an Item with an array of some 'DAY' keys.
```yaml
# example 'Item.data'
days: # days array
- DAY-19
- DAY-20
- DAY-21
```

We could then check if a specific key is in `Item.data.days` array
```yaml
# query to get items that have 'DAY-20' in their 'days' array
days: DAY-20
# field: value
```

If the 'field' we're querying is an array, but the 'value' we're checking for is not an array, then we search return items with that 'value' in the array
- this makes it so we can still search for exact match arrays, AND we can also search for specific values in an array.

## Query Pipelines
Queries can be chained together by making the query object an array (AKA YAML sequence) at the top level.

```yaml
# num_of_done_items.yaml
- status: done # gets the items that have a status done
- $count # then, counts those items
```

### Aggregations
Given a Query Pipeline, you can use one of the aggregation keywords to condense values.
- `$count`
- `$sum`
- `$concat`
