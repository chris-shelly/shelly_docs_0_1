# SYSTEM-2 TUI
```yaml (data)
status: done
relates_to:
  - ACTOR-1
depends_on:
  - SYSTEM-3
```
Provides a `textual` TUI for the user to interact with.

Primarily intended for HUmans, since Agents will be more efficient interacting with Shelly Docs via the CLI (`shelly-docs`)

Allows user to view and edit the items in the knowledge base.

## SYSTEM-2-1 Home Screen
Lets the user specify a Knowledge Base Path to open the app with respect to.

## SYSTEM-2-2 Knowledge Base Screen
Lets the user view their Items in the Knowledge Base, see the current config of the Knowledge Base, as well as select items to update/delete, or create New Items.

## SYSTEM-2-3 Create New Item Screen
Lets user write A new item with a basic markdown editor and specify a filepath to locate the item. 
- if the path is an existing file, then SHelly DOcs tries to place it in order amongst its siblings.
## SYSTEM-2-4 Delete Item Screen
Gives the User a confirmation screen asking them to confirm if they want to delete an item.
## SYSTEM-2-5 Update Item Screen
Gives the User a basic markdown editor to update the contents of a specific item.
