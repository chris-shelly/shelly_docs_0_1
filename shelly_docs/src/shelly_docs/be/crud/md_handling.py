
from mistletoe import Document
from mistletoe.ast_renderer import ASTRenderer
from mistletoe.block_token import BlockToken, Paragraph, SetextHeading, Heading, CodeFence
from mistletoe.span_token import SpanToken, RawText, InlineCode
from mistletoe.token import Token
from mistletoe.markdown_renderer import MarkdownRenderer
from rich import print

from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

class MyYAML(YAML):
  def dump(self, data, stream=None, **kw):
    inefficient = False
    if stream is None:
      inefficient = True
      stream = StringIO()
    YAML.dump(self, data, stream, **kw)
    if inefficient:
      return stream.getvalue()
yaml = MyYAML()

def update_text(token: SpanToken, new_text: str):
  """Update the text contents of a span token and its children.
  `InlineCode` tokens are left unchanged."""
  if isinstance(token, RawText):
    token.content = new_text

def update_block(token: BlockToken, new_text: str):
  """Update the text contents of paragraphs and headings within this block,
  and recursively within its children."""
  if isinstance(token, (Paragraph, SetextHeading, Heading, CodeFence)):
    for child in token.children:
      update_text(child, new_text)

  for child in token.children:
    if isinstance(child, BlockToken):
      update_block(child, new_text)


def parse_item(item_markdown: str):
  """
  Given a Shelly Docs 'Item' markdown, identify the blocks (data_block, content)
    - 'data_block'
        - the structured "yaml (data)" codefence
    - 'content'
        - all other block tokens
  """
  # parse to markdown
  # read through each top level block token, identify
  document = Document(item_markdown)
  for child in document.children:
    if isinstance(child, CodeFence) and child.info_string == "yaml (data)":
      print("parse_item()::data block found")
      print(child.content)
      
def get_data_block(item_markdown: str) -> dict:
  document = Document(item_markdown)
  for child in document.children:
    if isinstance(child, CodeFence) and child.info_string == "yaml (data)":
      return yaml.load(child.content)
  return None

def get_data_block_str(item_markdown: str) -> str:
  document = Document(item_markdown)
  for child in document.children:
    if isinstance(child, CodeFence) and child.info_string == "yaml (data)":
      return child.content
  return None

def set_data_block(item_markdown: str, data: dict) -> str:
  """
  Update the data block and return the new item markdown
  """
  with MarkdownRenderer() as renderer:
    document = Document(item_markdown)
    for child in document.children:
      if isinstance(child, CodeFence) and child.info_string == "yaml (data)":
        new_data_block_content = yaml.dump(data)
        update_block(child, new_data_block_content)
    new_item_markdown = renderer.render(document)[:-1]
    print(new_item_markdown)
    return new_item_markdown
  
def get_content(item_markdown: str) -> str:
  """
  Get the markdown content, excluding the 'title' and 'data block'
  """
  document = Document(item_markdown)
  found_data_block = False
  data_block_start = -1
  data_block_end = -1
  for child in document.children:
    if (isinstance(child, CodeFence) and child.info_string == "yaml (data)"):
      found_data_block = True
      data_block_start = child.line_number
    elif found_data_block and data_block_end == -1:
      data_block_end = child.line_number
  content = "\n".join(item_markdown.splitlines()[1:data_block_start - 1])  + "\n".join(item_markdown.splitlines()[data_block_end-1:])
  print(content)
  return content

def set_content(item_markdown: str, new_content: str) -> str:
  """
  Update the content and return the new item markdown
  - by default, item content is placed after the data block
  - future functionality may allow for custom positioning of the data block within the content
  """
  
  document = Document(item_markdown)
  found_data_block = False
  data_block_start = -1
  data_block_end = -1
  for child in document.children:
    if (isinstance(child, CodeFence) and child.info_string == "yaml (data)"):
      found_data_block = True
      data_block_start = child.line_number
    elif found_data_block and data_block_end == -1:
      data_block_end = child.line_number
  
  data_block_str = "\n".join(item_markdown.splitlines()[data_block_start - 1:data_block_end - 1])
  new_item_markdown = f"{item_markdown.splitlines()[0]}\n{data_block_str}\n{new_content}"
  return new_item_markdown
