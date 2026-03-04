# DESIGN-1 Knowledge Base
The Knowledge Base is the directory in which Shelly Docs is initialized.

Shelly Docs scans markdown documents within that directory to read, update, create and delete [`Item`s](#design-2-item).

# DESIGN-2 `Item`
An `Item` is a piece of markdown documentation content within a [Knowledge Base](#design-1-knowledge-base).

An `Item` is defined as a markdown heading with content under it.
## DESIGN-2-1 `Item` Example
For example,
```md
<!-- Item starts with the Heading-->
## ABC-32 Retrieve Data
Retrieve data so we can display itto the user
<!-- Item ends either with end of the document or another Heading with the same or higher level -->
<!--New Item, separate from ABC-32-->
## ABC-33 Display Data
Display the data to the user
...
```
Aside from headings of the same or higher level (which would indicate another `Item`), any sort of content can be within a given `Item`, including paragraphs, code blocks, images, etc.