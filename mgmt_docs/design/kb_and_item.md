# DESIGN-1 Knowledge Base
```yaml (data)
status: done
```
The Knowledge Base is the directory in which Shelly Docs is initialized.

Shelly Docs scans markdown documents within that directory to read, update, create and delete [`Item`s](#design-2-item).

## DESIGN-1-1 Knowledge Base `state.yaml`
Within the Knowledge Base is a `state.yaml` file that stores the data on the `Item`s like a very simplistic kind of database collection.
```yaml
items:
  ABC-32:
    title: "ABC-32 Retrieve Data",
    content: "Retrieve data so we can display it to the user",
    parent_title: "" #empty if there is no parent item
  ABC-33:
    title: "ABC-33 Display Data"
    # ...
```

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
## DESIGN-2-2 `Item.data`
An `Item` can have structured data attached to it within the markdown document.

A yaml code block with the `yaml (data)` around it is then parsed and saved alongside the item in state.

This data can later be queried from the `state.yaml` to provide information to the user about the items.
## DESIGN-2-3 `Item.data.type`
```yaml (data)
status: done
type: whatever I want
```
By default, the item `type` is retrieved based on the Item Tag of the Item's title/declaration, and then stored within the Item's `data` field so it can be queried.

The user can overide the ``type`` with whatever content they have in the fenced `yaml (data)` code block.
## DESIGN-2-4 Item Hierarchy - `Item.parent` and Child `Item`s
```yaml (data)
status: done
```
Items can be nested within eachother in a hierarchy based on their Item Key declarations. For example, this item (DESIGN-2-4) is nested within DESIGN-2, indicated by the extra `-` in the Item Key number.

Within the `state.yaml` of a knowledge base, an `Item` will have a `parent` field indicating the key of its parent `Item`