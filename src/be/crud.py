from pathlib import Path
import re
import json
from pprint import pprint

from mistletoe import Document
from mistletoe.ast_renderer import ASTRenderer

def get_items(path: str, config: dict) -> list[dict]:
  dir = Path(path)
  items = []
  if dir.is_dir():
    docs = get_md_docs_in_dir(dir)

  for doc in docs:
    parsed_doc = parse_md_doc(doc)
    items = items + read_items_in_doc(parsed_doc, config['item_tags'])
  return items

def get_item(path):
  # given an ID, get a specific item
  pass

def get_md_docs_in_dir(dir: Path) -> list[Path]:
  docs = []
  for child in dir.iterdir():
    if child.suffix == ".md":
      docs.append(child)
    elif child.is_dir():
      docs = docs + get_md_docs_in_dir(child)
  return docs

def read_items_in_doc(doc: dict, item_tags: list[str]) -> list[dict]:
  item_tag_base = '^(ABC-\\d+.*)\\s*$'
  items = []
  for item_tag in item_tags:
    item_tag_pattern = re.compile(item_tag_base.replace('ABC', item_tag))
    new_items = traverse_for_items(doc, item_tag_pattern, [])
    items = items + new_items
  return items

def get_text_from_children(node: dict, text: str = "", mode: str = "normal"):
  for child in node['children']:
    if child['type'] == 'RawText':
      if mode == 'normal':
        text += child['content']
      elif mode == 'code':
        text += f"`{child['content']}`"
    elif child['type'] == 'InlineCode':
      text = get_text_from_children(child, text, mode="code")
    elif child['type'] == 'Strong':
      text += '**'
      text = get_text_from_children(child, text)
      text += '**'
    elif child['type'] == 'Emphasis':
      text += '*'
      text = get_text_from_children(child, text)
      text += '*'
  return text

def node_to_markdown(node: dict) -> str:
  node_type = node['type']

  if node_type == 'Paragraph':
    text = get_text_from_children(node)
    return text + '\n\n'

  elif node_type == 'CodeFence':
    lang = node.get('language', '')
    content = get_text_from_children(node)
    return f"```{lang}\n{content}```\n\n"

  elif node_type == 'BlockCode':
    content = get_text_from_children(node)
    lines = content.split('\n')
    indented = '\n'.join('    ' + line for line in lines)
    return indented + '\n\n'

  elif node_type == 'Heading':
    prefix = '#' * node.get('level', 1)
    text = get_text_from_children(node)
    return f"{prefix} {text}\n\n"

  elif node_type == 'List':
    result = ''
    for i, child in enumerate(node.get('children', [])):
      if child['type'] == 'ListItem':
        item_text = ''
        for sub in child.get('children', []):
          item_text += node_to_markdown(sub).strip()
        if node.get('start') is not None:
          result += f"{node['start'] + i}. {item_text}\n"
        else:
          result += f"- {item_text}\n"
    return result + '\n'

  else:
    # Best-effort fallback
    if 'children' in node:
      return get_text_from_children(node) + '\n\n'
    return ''

def traverse_for_items(doc: dict, item_tag_pattern: re.Pattern, items: list = []):
  children = doc.get('children', [])
  current_item = None
  # Stack of (level, title) for tracking parent headings
  parent_stack = []

  for node in children:
    if node['type'] == 'Heading':
      level = node.get('level', 1)
      title = get_text_from_children(node)
      item_match = item_tag_pattern.findall(title)

      if item_match:
        # Finalize previous item
        if current_item is not None:
          current_item['content'] = current_item['content'].strip()
          items.append(current_item)

        # Update parent stack: pop anything at same or deeper level
        while parent_stack and parent_stack[-1][0] >= level:
          parent_stack.pop()

        # Determine parent_title from the stack
        parent_title = parent_stack[-1][1] if parent_stack else ""

        current_item = {
          "title": item_match[0],
          "content": "",
          "parent_title": parent_title,
        }

        # Push this item onto the parent stack for potential children
        parent_stack.append((level, item_match[0]))

      else:
        # Non-matching heading: ends current item if same or higher level
        if current_item is not None:
          current_level = None
          # Find what level the current item was at
          for lvl, ttl in reversed(parent_stack):
            if ttl == current_item['title']:
              current_level = lvl
              break
          if current_level is not None and level <= current_level:
            current_item['content'] = current_item['content'].strip()
            items.append(current_item)
            current_item = None
          else:
            # Sub-heading within current item — include as content
            current_item['content'] += node_to_markdown(node)

        # Update parent stack for non-matching headings too
        while parent_stack and parent_stack[-1][0] >= level:
          parent_stack.pop()
        parent_stack.append((level, title))

    else:
      # Non-heading node: append content to current item
      if current_item is not None:
        current_item['content'] += node_to_markdown(node)

  # Finalize last item
  if current_item is not None:
    current_item['content'] = current_item['content'].strip()
    items.append(current_item)

  return items

def parse_md_doc(path: Path):
  md_doc_text = path.read_text()
  md_doc_tree = Document(md_doc_text)
  with ASTRenderer() as renderer:
    rendered = renderer.render(md_doc_tree)
  rendered = json.loads(rendered)
  return rendered

if __name__ == "__main__":
  items = get_items("../../mgmt_docs", {"item_tags": ['ACTOR', 'USECASE', 'DESIGN']})
  for item in items:
    print(f"\n--- {item['title']} ---")
    if item['parent_title']:
      print(f"  parent: {item['parent_title']}")
    if item['content']:
      print(f"  content: {item['content'][:120]}...")
    else:
      print("  content: (empty)")
