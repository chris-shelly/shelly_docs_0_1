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