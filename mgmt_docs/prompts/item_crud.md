# PROMPT-1 Reading Item Content
## `Role`
You are a Senior Python Developer with extensive experience parsing and extending markdown. You are familiar with the `mistletoe` library for parsing and manipulating the AST of Markdown Documents.
## `Background on Goal`
In `crud.py`, we want to update the `get_items()` function to parse documentation Items. Letting us determine the `title`, `content`, and `parent_title` (if applicable).
## `Design` - Documentation `Item`s
An `Item` is a piece of markdown documentation content within a [Knowledge Base](#design-1-knowledge-base).

An `Item` is defined as a markdown heading with content under it.

For example ...


```md
<!-- Item starts with the Heading-->
## ABC-32 Retrieve Data
Retrieve data so we can display it to the user
<!-- Item ends either with end of the document or another Heading with the same or higher level -->
<!--New Item, separate from ABC-32-->
## ABC-33 Display Data
Display the data to the user
...
```
Aside from headings of the same or higher level (which would indicate another `Item`), any sort of content can be within a given `Item`, including paragraphs, code blocks, images, etc.

## `Goal`
In `crud.py`, update the `get_items()` function to parse documentation Items. A documentation item must be made available as json.
```yaml
{
"title": "ABC-32 Retrieve Data",
"content": "Retrieve data so we can display it to the user",
"parent_title": "" #empty because there is no parent `Item`
}
```
## ``Claude Plan``
- Recursive traversal should be replaced with a linear scan approach
- Add a `node_to_markdown` helper
- Cleaning up debug prints

# PROMPT-2 Put Items
## `Role`
You are a Senior Python Developer with extensive experience parsing and extending markdown. You are familiar with the `mistletoe` library for parsing and manipulating the AST of Markdown Documents.
## `Goal`
In `crud.py`, we want an `put_item()` function to idempotently add/update an item's content in the markdown document.

Add logic that ensures:
- the item key is unique
- the item type is one of the valid types defined in `shellydocs.yaml` config
## `Summary of Claude's Plan`
- replace `update_item()` stub with `put_item()`
- add validation logic
  - type
  - key uniqueness
- write to markdown file, have to use raw text

# PROMPT-3 Update `Item.path` so that it represents the path to the `Item`
## `Role`
You are a Senior Python Developer with extensive experience parsing and extending markdown. You are familiar with the `mistletoe` library for parsing and manipulating the AST of Markdown Documents.
## `Goal`
Update the generation of `Item.path` so that it presents a path directly to the markdown (includes the anchors, ex. [Link to DESIGN-2 Item](../design/item.md#design-2-item'))

# PROMPT-4 Delete Item
## `Role`
You are a Senior Python Developer with extensive experience parsing and extending markdown. You are familiar with the `mistletoe` library for parsing and manipulating the AST of Markdown Documents.
## `Goal`
Add a `delete_item()` method that removes an Item from a Markdown Document.

# PROMPT-5 Convert `new_item_md` objects into `item`
## `Role`
You are a Senior Python Developer with extensive experience parsing and extending markdown. You are familiar with the `mistletoe` library for parsing and manipulating the AST of Markdown Documents.
## `Goal
Create a function in `be/crud.py` that reads/parses a `new_item_md` object to convert it into our typical `item` object, so that we can use pass it to the `put_item()` function to actually write the `Item`.

We will use this so that Humans can create Items via the TUI.
## `Design`
### example `new_item_md` dict object
```python
{
  "kb_path": "../mgmt_docs"
  "filepath": "reqs/reqs.md",
  "markdown": "# REQ-2 Verify Data\n I have some content here."
}
```
### expected output `item` dict object from above example
```python
{
  "path": "../mgmt_docs/reqs/reqs.md",
  "title": "# REQ-2 Verify Data",
  "content": "I have some content here.",
  "parent_title": "" # detect parent if applicable
}
```
## Output Summary
- Created a `convert_new_item_md(new_item_md: dict)` function
  - joins the `kb_path` and `file_path`
  - Prases the markdown via a new helper `parse_md_text()`
  - extracts the first heading as `title`, everything after it as content
  - if the target file already exists, reads it to detect the last heading that would be a parent

# PROMPT-6 Better Handling of Item Hierarchies
## `Role`
You are a Senior Python developer working on Shelly Docs. A TUI/CLI tool for managing documentation items using markdown.
## `Background on Issue`
On trying to add an item with a key of `USECASE-77-1`, we get this error.
```
ValueError: Tag 'USECASE-77' not in configured item_tags: ['USECASE', 'DESIGN', 'ACTOR']
```

It seems that we are not correctly pattern matching to get the tag prefix.
## `Goal`
Update the pattern matching approach in `put_item()` so that the item type (aka `tag_prefix`) is correctly determined.

## Output Summary
- replace `rsplit('-', 1)` with a loop checking if the item_key starts with any configured tag followed by `-`.
- this correctly identifies the item types.

# PROMPT-7 - Items are written as Heading 2s, even if they are set at a different level.
## `Role`
You are a Senior Python developer working on Shelly Docs. A TUI/CLI tool for managing documentation items using markdown.

You have extensive experience parsing and extending markdown. You are familiar with the `mistletoe` library for parsing and manipulating the AST of Markdown Documents.
## `Background on Issue`
In Line 72 of `be/crud.py` within `put_item()` it looks like we are assuming that all Items should be written as Heading 2s (starting with '##') instead of whatever was directly in their heading.
## `Goal`
Update the `item` objects so that we properly store and write the heading levels based on what was initially written in markdown, allowing users to hierachically model their items.
## Output summary
- updated `traverse_for_items()` to store `level` in each item dict
- `put_item` now uses `item.get()` to generate the correct heading prefix
- `convert_new_item` captures the `level` from the parsed heading node and includes it in the returned dict


