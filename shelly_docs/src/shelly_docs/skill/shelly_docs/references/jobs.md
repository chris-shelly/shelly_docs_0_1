# Jobs
Jobs are used to run scripts against Items or Query results, either automatically when a KnowledgeBase's state updates, or when manually invoked.

Jobs are specified in the `shellydocs.yaml::jobs` array

```yaml (shellydocs.yaml)
item_tags:
- DOC
- DAY
jobs:
  - name: add_date_to_data_block # optional
    script: add_date.py
    active: true
    item_types:
    - DAY
    job_type: item
  - name: task_summary
    job_type: query
    query: task_summary.yaml
```

## Item jobs
Evaluated on every Item within the specified `item_types`
```yaml (the 'item_job' object)
name: !!str
script: !!str ## filepath to the script
item_types: !!seq # the types of items to trigger the job on
```

This provides a `shelly_docs.kb.Item` object as a modules global to the specified python `script`.


## Query Jobs
Evaluated on the results of a [Query](queries.md) 
```yaml (the 'query_job' object)
name: !!str
script: !!str # filepath to the script
query: !!str # filepath to the query
```

This provides a query output `dict` as a modules global to the specified python `script`.
```python (query output object)
{'results': <query_result>, 'query': <query>}
```

## `Job.active`
By default, all jobs are `active`, meaning they run everytime a Knowledge Base is updated (via `shelly-docs kb update`, `shelly_docs.kb.KnowledgeBase.update_state()` or related create/update operations), AND they run whenever `KB.run_jobs` is invoked (via `shelly-docs jobs run_all` or `shelly_docs.kb.KnowledgeBase.run_jobs()`)

Set `active:false` to make it so that jobs must be manually invoked via `shelly-docs jobs run <job_name>` or `shelly_docs.kb.KnowledgeBase.run_job(<job_name>)`