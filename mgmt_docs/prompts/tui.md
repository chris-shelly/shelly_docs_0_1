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

