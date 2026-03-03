# TUI Entry point

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Header, Static, Input, Label, Button, Pretty
from textual.screen import Screen
from textual.message import Message
from textual.reactive import reactive

from be.config import get_config


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


class KnowledgeBase(Widget):
  def __init__(self, path: str):
    self.path = path
    super().__init__()
  def compose(self) -> ComposeResult:
    # use the path to read the config and read the items
    yield Static(f"path: {self.path}")
    kb_config = get_config(self.path)
    yield KnowledgeBaseConfig(kb_config)

  
class KnowledgeBaseScreen(Screen):
  def __init__(self, path: str):
    self.path = path
    super().__init__()

  def compose(self) -> ComposeResult:
    yield KnowledgeBase(self.path)

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


if __name__ == "__main__":
  app = ShellyDocs()
  app.run()
