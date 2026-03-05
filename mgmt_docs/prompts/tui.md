# PROMPT-8 Allow user to Delete Item via TUI
## `Role`
You are a Senior Python Developer with extensive expertise using the `textual` python library to create Terminal User Interfaces (TUIs).

You are working on Shelly Docs a TUI & CLI application for managing markdown documentation Items.
## `Goal`
We want to enable the user to Delete Items from the TUI.

## `Design`
### Delete Button
Within the Knowledge Base Screen, add a "Delete Item" button next to the `KnowledgeBaseConfig` widget, so that we can delete the active item.
### DeleteItemScreen
Add a Screen that lets the user confirm if they want to delete the item. On confirmation, extract the `item_key` and use it to make a call to be.crud.delete_item()

# PROMPT-9 Allow user to Update Item via TUI
## `Role`
You are a Senior Python Developer with extensive expertise using the `textual` python library to create Terminal User Interfaces (TUIs).

You are working on Shelly Docs a TUI & CLI application for managing markdown documentation Items.
## `Goal`
We want to enable the user to Update Items from the TUI.

## `Design`
### Update Button
Within the Knowledge Base Screen, add a "Delete Item" button next to the `KnowledgeBaseConfig` widget, so that we can delete the active item.
### UpdateItemScreen
Add a Screen that lets the user write to a Markdown TextArea (similar to the one used for the `NewItemMd` widget) to update the Item.
- loads the TextArea with the existing content.
- loads the item using it's existing filepath.
After making an update, convert yields a `raw_item_md` that can be converted to an `item` dict taht can be passed to `put_item()`, similarly to how the the `CreateNewItemScreen()` handles new items. 

## PROMPT-9-1 Follow-up, Path not calculating correctly
After attempting to edit `USECASE-77-1`, `put_item()` raised a ValueError for it already existing in a different file.

```
ValueError: Item 'USECASE-77-1' already exists in a different file: ..\mgmt_docs\reqs\new.md#usecase-77-1-child-item-being-added
```

IT seems that the path being collected for us to make the updates isn't correct. as it shows as `'path': '../mgmt_docs/..\\mgmt_docs\\reqs\\new.md',`.

Please fix the issue so the Path calculates correctly.

## PROMPT-9-2 Path still broken
Path still broken, need a better check of the paths. seems like the paths aren't matching due to the anchors.

```
ValueError: Item 'USECASE-77-1' already exists in a different file: ..\mgmt_docs\reqs\new.md#usecase-77-1-child-item-being-added
```
