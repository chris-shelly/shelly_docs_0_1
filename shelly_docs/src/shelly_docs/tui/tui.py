# TUI Entry point

from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widget import Widget
from textual.widgets import Header, Static, Input, Label, Button, Pretty, OptionList, Markdown, TextArea, Footer
from textual.screen import Screen
from textual.message import Message
from textual.reactive import reactive

from rich.markdown import Markdown as RichMD
from ..be.shelly_docs_config.config import get_config
from ..be.crud.crud import get_items, convert_new_item_md, put_item, delete_item, write_items_to_state

from pathlib import Path

class ShellyDocsHeader(Header):
  pass


class InputWithLabel(Widget):
  """An input with a label."""
  DEFAULT_CSS = """\
  InputWithLabel {
    layout: horizontal;
    height: auto;
    content-align: center middle;
  }
  InputWithLabel Label {
    text-align: right;
    padding: 1 2;
  }
  InputWithLabel Input {
    text-align: left;
  }
  """

  def __init__(self, input_label: str, placeholder: str = "") -> None:
    self.input_label = input_label
    self.placeholder = placeholder
    super().__init__()

  def compose(self) -> ComposeResult:
    yield Label(self.input_label)
    if self.placeholder:
      yield Input(placeholder=self.placeholder, id="path-input")
    else:
      yield Input(id="path-input")


class TextAreaWithLabel(Widget):
  def __init__(self, input_label: str, placeholder: str="") -> None:
    self.input_label = input_label
    self.placeholder = placeholder
    super().__init__()

  def compose(self) -> ComposeResult:
    yield Label(self.input_label, id="new-item-id-label")
    if self.placeholder:
      text_area = TextArea.code_editor(id="new-item-md")
      text_area.can_focus=True
      text_area.language = "markdown"
      text_area.placeholder = self.placeholder
      yield text_area
    else:
      text_area = TextArea.code_editor(id="new-item-md")
      text_area.can_focus=True
      text_area.language = "markdown"
      text_area.text = "# ABC-1 Title Is Here\n"
      yield text_area
  def key_space(self):
    # access the text area by dom query
    text_area = self.query_one("#new-item-md", TextArea)
    # insert a space at the current cursor position/selection
    text_area.insert(" ")

class NewItemMd(TextAreaWithLabel):
  """TextArea input for user to enter the markdown for creating a new item."""

class NewItemPath(InputWithLabel):
  """
  Input for user to enter the filepath for a new item, relative to the config path

  Assumes a user can only drill down, not up
  """

class ConfigPath(InputWithLabel):
  """Input used to let the user point the app to the location for the shellydocs.yaml folder"""
  pass


class InitializeProjectButton(Button):
  """Button used to initialize project"""
  pass

class Home(Widget):
  class PathProvided(Message):
    def __init__(self, path: str) -> None:
      self.path = path
      super().__init__()
  def compose(self) -> ComposeResult:
    with Vertical():
      yield ConfigPath(
        input_label="Knowledge Base Path",
        placeholder="../mgmt_docs"
      )
      yield InitializeProjectButton("Open Knowledge Base", id="init-project")
  def on_button_pressed(self):
    # react to the button press
    # post a message to the app
    # get the Knowledge base path from the ConfigPath via dom query
    path_input = self.query_one("#path-input", Input)
    self.post_message(self.PathProvided(path_input.value))
    

class KnowledgeBasePath(Static):
  """Used to open up a page for the Knowledge Base"""
  path = reactive("n/a")
  def render(self) -> str:
    return self.path



class KnowledgeBaseConfig(Pretty):
  """Use Pretty to show the JSON representation of the `shellydocs.yaml` config"""
  def on_mount(self):
    self.border_title = "Config"
    self.styles.border_title_align = "left"

class KnowledgeBaseMenu(Widget):
  """Widget holding the `KnowledgeBaseItems` and the Options Bar, which allows for creating new `Item`s"""
  class CreateNewItem(Message):
    """Create a New Message"""
    pass

  class DeleteItem(Message):
    """Delete an Item"""
    pass

  class UpdateItem(Message):
    """Update an Item"""
    pass

  def __init__(self, items: list[dict], item_index: int, kb_path: str):
    super().__init__()
    self.item_index = item_index
    self.kb_path = kb_path
    self.items = items

  def compose(self) -> ComposeResult:
    # pass the items as a list of strings to yield an Options List of the KB Items
    with Horizontal(id="kb-menu-options"):
      yield Button("New Item", id="new-item-btn", compact=True, classes="kb-menu-option")
      yield Button("Update Item", id="update-item-btn", compact=True, classes="kb-menu-option")
      yield Button("Delete Item", id="delete-item-btn", compact=True, classes="kb-menu-option")
    yield KnowledgeBaseItems(self.items, self.item_index)
  
  def on_button_pressed(self, event: Button.Pressed) -> None:
    if event.button.id == "new-item-btn":
      self.post_message(self.CreateNewItem())
    elif event.button.id == "delete-item-btn":
      self.post_message(self.DeleteItem())
    elif event.button.id == "update-item-btn":
      self.post_message(self.UpdateItem())

class KnowledgeBaseItems(Widget):
  """Use an OptionList to show the Items"""
  def __init__(self, items: list[dict], item_index: int):
    self.item_index = item_index
    super().__init__()
    self.items = items
    self.item_options = [RichMD(item['title']) for item in self.items]
  def compose(self) -> ComposeResult:
    options = OptionList(*self.item_options, classes="box", id="options")
    options.highlighted = self.item_index
    yield options

class KnowledgeBase(Widget):
  DEFAULT_CSS = """\
  KnowledgeBase {
    layout: grid;
    grid-size: 3;
    grid-columns: 3fr 3fr 3fr; 
  }

  KnowledgeBaseMenu {
    row-span: 3;
  }

  Item {
    column-span: 2;
    row-span: 2;
  }

  KnowledgeBaseConfig {
    column-span: 2;
    row-span: 1;
  }

  .box {
    border: solid white;
    height: 100%;

  }

  KnowledgeBaseMenu {
    layout: grid;
    grid-size: 1 2;
    grid-rows: 2fr 6fr;
  }

  #kb-menu-options {
    border: solid white;
  }

  #kb-menu-options .kb-menu-option {
    content-align: center middle;
  }

  .kb-menu-option {
    width: 1fr;
    height: 100%;
  }

  """
  item = reactive({})
  items = reactive([])
  item_index = reactive(0)
  def __init__(self, path: str):
    self.path = path
    self.kb_config = get_config(self.path)
    super().__init__() # call before setting reactives
    
  def compose(self) -> ComposeResult:
    # pass the items as a list of dicts to yield an Options List of the KB Items
    # get the Items
    self.items = get_items(self.path, self.kb_config)
    write_items_to_state(self.path)
    # get a specific item, by default, just get the first one
    self.item = self.items[0]
    yield KnowledgeBaseMenu(self.items, self.item_index, self.path)
    # render markdown content of a single item
    yield Item(self.item['markdown'], item_title=self.item['title'], document_path=self.item['path'])
    # pretty print the JSON representation of the Config
    yield KnowledgeBaseConfig(self.kb_config, classes="box")
  
  def update_items(self) -> None:
    self.items = get_items(self.path, self.kb_config)
    kb_menu = self.query_one("KnowledgeBaseMenu", KnowledgeBaseMenu)
    kb_menu.items = self.items
    kb_items = kb_menu.query_one("KnowledgeBaseItems", KnowledgeBaseItems)
    kb_items.items = kb_menu.items
    kb_items.item_options = [RichMD(item['title']) for item in kb_items.items]
    optionlist = kb_items.query_one("OptionList",OptionList)
    optionlist = optionlist.set_options(kb_items.item_options)
  def on_option_list_option_selected(self, message: OptionList.OptionSelected):
    self.item_index = message.option_index
    self.item = self.items[message.option_index]
    item_display = self.query_one("Item", Item)
    # update item content, border title, and subtitle
    item_display.border_title = self.item['title']
    item_display.border_subtitle = self.item['path']
    markdown = item_display.query_one("Markdown", Markdown)
    markdown.update(self.item['markdown'])


  
class KnowledgeBaseScreen(Screen):
  def __init__(self, path: str):
    self.path = path
    super().__init__()

  def compose(self) -> ComposeResult:
    yield ShellyDocsHeader()
    yield KnowledgeBase(self.path)

  def on_screen_resume(self) -> None:
    kb = self.query_one("KnowledgeBase", KnowledgeBase)
    write_items_to_state(self.path)
    kb.update_items()


class Item(Widget):
  """Show the Item as Markdown, takes a Markdown string as input."""
  def __init__(self, markdown: str, item_title: str, document_path: str = ""):
    self.markdown = markdown
    self.item_title = item_title
    self.document_path = document_path
    super().__init__()

  def compose(self) -> ComposeResult:
    yield Markdown(self.markdown)

  def on_mount(self) -> None:
    self.classes = "box"
    self.border_title = self.item_title
    self.styles.border_title_align = "left"
    if self.document_path:
      self.border_subtitle = self.document_path
      self.styles.border_subtitle_align = "right"

class CreateNewItemScreen(Screen):
  """Screen for creating new items"""
  def compose(self) -> ComposeResult:
    yield ShellyDocsHeader()
    yield Static("Create New Item")
    # accept a file input using `InputWithLabel`
    yield NewItemPath("filepath")
    # accept a Markdown TextArea input using `TextAreaWithLabel`
    yield NewItemMd("Markdown","# ABC-1 New Item Title")
    # button to dismiss the window, triggering the creation
    yield Button("Create")

  def on_button_pressed(self, event: Button.Pressed) -> None:
    # query content of the filepath
    filepath = self.query_one("#path-input", Input).value
    # query content of the markdown text area
    md_text = self.query_one("#new-item-md", TextArea).text
    # condense into a dict
    new_item_md = {"filepath": filepath, "markdown": md_text}
    # pass the dict up
    self.dismiss(new_item_md)

class DeleteItemScreen(Screen):
  """Screen for Deleting an Item"""
  def __init__(self, item_title: str):
    self.item_title = item_title
    super().__init__()

  def compose(self) -> ComposeResult:
    yield ShellyDocsHeader()
    yield Static(f"Are you sure you want to delete this item?\n\n{self.item_title}")
    with Horizontal(id="delete-confirm-buttons"):
      yield Button("Delete", id="confirm-delete-btn", variant="error")
      yield Button("Cancel", id="cancel-delete-btn")

  def on_button_pressed(self, event: Button.Pressed) -> None:
    if event.button.id == "confirm-delete-btn":
      self.dismiss(True)
    elif event.button.id == "cancel-delete-btn":
      self.dismiss(False)


class UpdateItemMd(TextAreaWithLabel):
  """TextArea input for user to edit the markdown of an existing item."""

class UpdateItemScreen(Screen):
  """Screen for updating an existing Item"""
  def __init__(self, item: dict, kb_path: str):
    self.item = item
    self.kb_path = kb_path
    super().__init__()

  def compose(self) -> ComposeResult:
    yield ShellyDocsHeader()
    yield Static("Update Item")
    # retrieve the markdown of the item
    existing_md = self.item['markdown']
    yield UpdateItemMd("Markdown", existing_md)
    yield Button("Update")

  def on_mount(self) -> None:
    text_area = self.query_one("#new-item-md", TextArea)
    text_area.text = f"{self.item['markdown']}\n"

  def on_button_pressed(self, event: Button.Pressed) -> None:
    md_text = self.query_one("#new-item-md", TextArea).text
    full_filepath = self.item['path'].split('#')[0]
    filepath = str(Path(full_filepath).relative_to(self.kb_path))
    raw_item_md = {"filepath": filepath, "markdown": md_text}
    self.dismiss(raw_item_md)


class ShellyDocs(App):
  CSS_PATH="styles.tcss"
  SCREENS = {"kb": KnowledgeBaseScreen}
  kb_path = reactive("n/a")
  def __init__(self):
    super().__init__()
    self.kb_screen = None
  def compose(self) -> ComposeResult:
    yield ShellyDocsHeader()
    yield Home()
    
  def on_mount(self) -> None:
    self.title = "Shelly Docs"
    


  def on_home_path_provided(self, path: Home.PathProvided) -> None:
    self.kb_path = path.path
    self.kb_screen = KnowledgeBaseScreen(self.kb_path)
    self.push_screen(self.kb_screen)
  def on_knowledge_base_menu_create_new_item(self, msg: KnowledgeBaseMenu.CreateNewItem) -> None:
    def create_new_item(raw_item_obj: dict):
      # add the knowledge base path
      raw_item_obj['kb_path'] = self.kb_path
      new_items = convert_new_item_md(raw_item_obj)
      for new_item in new_items:
        item_key = new_item['key']
        put_item(self.kb_path,item_key, new_item, get_config(self.kb_path))
    self.push_screen(CreateNewItemScreen(), create_new_item) # call `create_new_item()` once we `dismiss` the Create New Item Screen

  def on_knowledge_base_menu_delete_item(self, msg: KnowledgeBaseMenu.DeleteItem) -> None:
    kb_widget = self.kb_screen.query_one("KnowledgeBase",KnowledgeBase)
    item = kb_widget.item
    item_title = item['title']
    item_key = item_title.split(' ')[0]
    def handle_delete(confirmed: bool):
      if confirmed:
        delete_item(self.kb_path, item_key)
        # calling the function automatically pops the screen, no need to pop again
    self.push_screen(DeleteItemScreen(item_title), handle_delete)

  def on_knowledge_base_menu_update_item(self, msg: KnowledgeBaseMenu.UpdateItem) -> None:
    kb_widget = self.kb_screen.query_one("KnowledgeBase", KnowledgeBase)
    item = kb_widget.item
    def handle_update(raw_item_obj: dict):
      if raw_item_obj is None:
        return
      raw_item_obj['kb_path'] = self.kb_path
      updated_items = convert_new_item_md(raw_item_obj)
      for updated_item in updated_items:
        item_key = updated_item['key']
        put_item(self.kb_path,item_key, updated_item, get_config(self.kb_path))
      # calling the function automatically pops the screen, no need to pop again
    self.push_screen(UpdateItemScreen(item, self.kb_path), handle_update)


if __name__ == "__main__":
  app = ShellyDocs()
  app.run()
