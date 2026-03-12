# PROMPT-10 Data Querying
## `Role`
You are a Senior Python Developer with experience making CLI apps that allow users to query data.
## `Background`
You are working on Shelly Docs, a TUI/CLI app that lets users organize and analyze documentation in markdown files.
### Knowledge Base
A "Knowledge Base" is a directory users set to capture Documentation Items.

Configuration for item types is captured in a `shellydocs.yaml` file in the Knowledge Base directory.

The Knowledge Base stores item state and metadata in the `state.yaml` file in the Knowledge Base directory.
### Items
"Items" are chunks of markdown documents, written by human or AI agent users that write sections of markdown starting with an item tag markdown header.

Each Item may have a `yaml (data)` codefence for storing data about that item, useful for analyzing/querying later.
## `Goal`
Plan a Feature that lets users query and analyze their Shelly Docs Items.
- for example, determining tasks that are in progress, requirements linked to specific tests, etc. 
## Example `state.yaml` file
```yaml
items:
  ABC-1:
    start_line: 1
    path: ..\experiment_code\md_data_parsing\data.md#abc-1-yo
    level: 1
    end_line: 9
    markdown: "# ABC-1 Yo\nThis is a markdown document with a data block in it.\n\n\
      ```yaml (data)\nfield1: yo\nfield2: 27\n```\nSee ya later.\n\n"
    title: ABC-1 Yo
    data:
      field1: yo
      field2: 27
    key: ABC-1
    parent:
  ABC-1-1:
    start_line: 10
    path: ..\experiment_code\md_data_parsing\data.md#abc-1-1-brodie
    level: 2
    end_line: 13
    markdown: "## ABC-1-1 Brodie\nKostecki be sending it down the mountain.\n\n\n"
    title: ABC-1-1 Brodie
    data:
    key: ABC-1-1
    parent: ABC-1
  ABC-2:
    start_line: 14
    path: ..\experiment_code\md_data_parsing\data.md#abc-2-hi-there
    level: 1
    end_line: 19
    markdown: "# ABC-2 Hi **`there`**\nWhat's up.\n```yaml (data)\nfield3: bruh\n\
      ```\n\n"
    title: ABC-2 Hi **`there`**
    data:
      field3: bruh
    key: ABC-2
    parent:
  #...
```