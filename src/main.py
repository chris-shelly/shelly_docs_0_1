# TUI Entry point

from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widget import Widget
from textual.widgets import Header, Static, Input, Label, Button, Pretty, OptionList, Markdown, TextArea
from textual.screen import Screen
from textual.message import Message
from textual.reactive import reactive

from rich.markdown import Markdown as RichMD
from be.config import get_config
from be.crud import get_items

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
      text_area = TextArea(id="new-item-md")
      text_area.language = "markdown"
      text_area.placeholder = self.placeholder
      yield text_area
    else:
      text_area = TextArea(id="new-item-md")
      text_area.language = "markdown"
      text_area.text = "# ABC-1 Title Is Here\n"

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


  def __init__(self, items: list[dict], item_index: int, kb_path: str):
    self.items = items
    self.item_index = item_index
    self.kb_path = kb_path
    super().__init__()

  def compose(self) -> ComposeResult:
    # pass the items as a list of strings to yield an Options List of the KB Items
    with Horizontal(id="kb-menu-options"):
      yield Static(f"{self.kb_path}/", classes="kb-menu-option")
      yield Button("New Item", compact=True, classes="kb-menu-option") # set to 'compact=True' so it fits at the top of the menu
    yield KnowledgeBaseItems([RichMD(item['title']) for item in self.items], self.item_index)

  def on_button_pressed(self) -> None:
    self.post_message(self.CreateNewItem())

class KnowledgeBaseItems(Widget):
  """Use an OptionList to show the Items"""
  def __init__(self, items: list[dict], item_index: int):
    self.items = items
    self.item_index = item_index
    super().__init__()
  def compose(self) -> ComposeResult:
    options = OptionList(*self.items, classes="box")
    options.highlighted = self.item_index
    yield options
class KnowledgeBase(Widget):
  DEFAULT_CSS = Path("knowledge_base_widget.tcss").read_text()
  item = reactive({}, recompose=True)
  item_index = reactive(0)
  def __init__(self, path: str):
    self.path = path
    self.items = []
    self.kb_config = get_config(self.path)
    # get the Items
    self.items = get_items(self.path, self.kb_config)
    super().__init__() # call before setting reactives (in this case, 'self.item')
    # get a specific item, by default, just get the first one
    self.item = self.items[0]
    
  def compose(self) -> ComposeResult:    
    # pass the items as a list of strings to yield an Options List of the KB Items
    yield KnowledgeBaseMenu(self.items, self.item_index, self.path)
    # render markdown content of a single item
    yield Item(self.item['content'], item_title=self.item['title'], document_path=self.item['path'])
    # pretty print the JSON representation of the Config
    yield KnowledgeBaseConfig(self.kb_config, classes="box")

  def on_option_list_option_selected(self, message: OptionList.OptionSelected):
    self.item_index = message.option_index
    self.item = self.items[message.option_index]
    


  
class KnowledgeBaseScreen(Screen):
  def __init__(self, path: str):
    self.path = path
    super().__init__()

  def compose(self) -> ComposeResult:
    yield ShellyDocsHeader()
    yield KnowledgeBase(self.path)


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

class ShellyDocs(App):
  CSS_PATH="styles.tcss"
  SCREENS = {"kb": KnowledgeBaseScreen}
  kb_path = reactive("n/a")
  def compose(self) -> ComposeResult:
    yield ShellyDocsHeader()
    yield Home()
    
  def on_mount(self) -> None:
    self.title = "Shelly Docs"

  def on_home_path_provided(self, path: Home.PathProvided) -> None:
    self.kb_path = path.path
    self.push_screen(KnowledgeBaseScreen(self.kb_path))
  def on_knowledge_base_menu_create_new_item(self, msg: KnowledgeBaseMenu.CreateNewItem) -> None:
    def create_new_item(item_md_obj: dict):
      print(item_md_obj)
    self.push_screen(CreateNewItemScreen(), create_new_item) # call `create_new_item()` once we `dismiss` the Create New Item Screen 


if __name__ == "__main__":
  app = ShellyDocs()
  app.run()
