---
name: shelly-docs
description: Use the Shelly Docs CLI and SDK to organize a knowledge base of markdown documents with content and structured data
---
`shelly-docs` is a CLI and Python library used to organize a folder of markdown files with structured, queryable data. This can be used to organize semi-structured information such that it can be queried and edited by agents and humans. 

Example Use Cases:
- Productivity and Notetaking
- Requirements and System Documentation
- Analysis of IT Tasks/Service Tickets
- Log and Telemetry Analysis
- etc.

Best used when working with combined structured/semi-structured and unstructured content, especially if organizing content with hierarchical relationships

## What is a Knowledge Base (KB)?
A Knowledge Base is a folder with its root established given the location of a `shellydocs.yaml` file. See [`references/shellydocs_yaml.md`](references/shellydocs_yaml.md) for additional details 

All markdown (`.md`) files in the Knowledge Base are then checked for Items.

## What is an Item?
An Item is a section of Markdown that holds a Heading, Data Block, and Content
- starts with a markdown Heading that has a valid Item Title format
  - has an item type, a dash-separated sequence of numbers, a space, and then the Name of the Item
  - ex. `# ABC-1 Hello`
- all markdown content under that Heading is part of the Item, until the next Heading
- optionally has a data block, which is a codefenced block of yaml with an info string of exactly `yaml (data)`

Any Item can have a child Item, which are specified by using a lower-level Item heading and/or using a common key prefix.

````md
# TASK-4 Marketing Campaign B
```yaml (data)
status: in_progress
start: 8-1-2026
end: 8-15-2026
product: 937
```
Campaign to introduce product 937 to new customer profile.
## TASK-4-1 Content Marketing
```yaml (data)
status: done
```
Working with influencers to create social media content.
## TASK-4-2 Paid Advertising
```yaml (data)
status: in_progress
```
Running Google Ads to gather web traffic on select keywords
````
## Setting Up a KB

1. Select/Create a file folder at some `<filepath>`
2. Create a `shellydocs.yaml` file in that folder, with an `item_tags` sequence specifying the valid item types.
3. Run `shelly-docs kb set --path <filepath>`. This will be the relative or absolute filepath used for all `shelly-docs` commands/operations
4. Run `shelly-docs kb update` to confirm that the Knowledge Base is configured correctly. A `state.yaml` file should be created within the `<filepath>` of the Knowledge Base.


## Making and Updating Items in a KB
Can either:
- Update Items directly through updating the markdown documents they live in, and then run `shelly-docs kb update` or `shelly_docs.kb.KnowledgeBase.update_state()`
- use the `shelly-docs` CLI or `shelly_docs` python library to edit items.

**NEVER make direct updates to `state.yaml`**
- Additional detail on `state.yaml` is provided in [references/state_yaml.md](references/state_yaml.md)

## Advanced Topics
### Queries
Retrieve Items from the Knowledge Base based on their data blocks. See details in [references/queries.md](references/queries.md)
### Jobs
Run Scripts automatically against Items in a Knowledge Base. See details in [references/jobs.md](references/jobs.md)
### `shelly_docs` python library
Work with Knowledge Bases and Items using a Python libary.
### `shelly-docs` CLI
Work with Knowledge Bases and Items in Bash.