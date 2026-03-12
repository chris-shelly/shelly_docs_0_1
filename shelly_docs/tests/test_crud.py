from pathlib import Path
import src.shelly_docs.be.crud.crud as crud
from rich import print
def scaffold_crud_test_directory():
  """
  Setup the `test_data` directory to conduct crud testing
  """
  test_data_path = Path("./test_data")
  # make `/test_data` directory if it doesnt exist
  test_data_path.mkdir(parents=True, exist_ok=True)
  # clear existing files from the directory
  def clear_directory(dir: Path):
    for item in dir.iterdir():
      if item.is_file():
        try:
          item.unlink()
        except Exception as e:
          print(f"Failed to delete file {item}, due to: {e}")
      elif item.is_dir():
        clear_directory(item)
        item.rmdir()
        
  clear_directory(test_data_path)
  # copy the files from the `/test_data_templates` directory into the `/test_data` directory
  test_data_templates_path = Path("./templates/a")
  test_data_templates_path.copy_into(test_data_path)

class TestGetItems:
  pass

class TestWriteItemstoState:
  pass

class TestGetState:
  pass

class TestGetItem:
  pass

class TestPutItem:
  pass

class TestGetSiblingPositioning:
  pass

class TestDeleteItem:
  pass

class TestHeadingToAnchor:
  pass

class TestGetMDDocsInDir:
  pass

class TestConvertNewItemMD:
  """
  Test `convert_new_item_md()`, for converting a new_item_md objec into a list of new Shelly Doc Items
  """

class TestParseMDText:
  """
  Test `parse_md_text()`, getting the AST of a Markdown document/snippet, given the markdown string
  """
  scaffold_crud_test_directory()
  def test_parse_md_text(self):
    parsed_md_doc = crud.parse_md_text(Path("./test_data/a/input_a.md").read_text())
    expected = {
      'type': 'Document',
      'footnotes': {},
      'line_number': 1,
      'children': [
        {
          'type': 'Heading',
          'line_number': 1,
          'level': 1,
          'children': [{'type': 'RawText', 'content': 'ABC-1 Alpha'}]
        },
        {
          'type': 'Paragraph',
          'line_number': 2,
          'children': [
            {'type': 'RawText', 'content': 'I have some text here.'}
          ]
        },
        {
          'type': 'Heading',
          'line_number': 5,
          'level': 1,
          'children': [{'type': 'RawText', 'content': 'ABC-2 Beta'}]
        },
        {
          'type': 'CodeFence',
          'line_number': 6,
          'language': 'yaml',
          'children': [
            {'type': 'RawText', 'content': 'field1: 8\nfield2: value\n'}
          ]
        },
        {
          'type': 'Paragraph',
          'line_number': 10,
          'children': [
            {'type': 'RawText', 'content': 'I have some more text here.'}
          ]
        },
        {
          'type': 'Heading',
          'line_number': 12,
          'level': 2,
          'children': [{'type': 'RawText', 'content': 'My Subheading'}]
        },
        {
          'type': 'Paragraph',
          'line_number': 14,
          'children': [{'type': 'RawText', 'content': 'yo'}]
        },
        {
          'type': 'Heading',
          'line_number': 16,
          'level': 2,
          'children': [
            {'type': 'RawText', 'content': 'ABC-2-1 Beta - Bruh'}
          ]
        }
      ]
    }
    assert parsed_md_doc == expected

class TestParseMDDoc:
  """
  Test `parse_md_doc()`, getting the AST of a Markdown document, given it's path
  """
  scaffold_crud_test_directory()
  def test_parse_md_doc(self):
    parsed_md_doc = crud.parse_md_doc(Path("./test_data/a/input_a.md"))
    expected = {
      'type': 'Document',
      'footnotes': {},
      'line_number': 1,
      'children': [
        {
          'type': 'Heading',
          'line_number': 1,
          'level': 1,
          'children': [{'type': 'RawText', 'content': 'ABC-1 Alpha'}]
        },
        {
          'type': 'Paragraph',
          'line_number': 2,
          'children': [
            {'type': 'RawText', 'content': 'I have some text here.'}
          ]
        },
        {
          'type': 'Heading',
          'line_number': 5,
          'level': 1,
          'children': [{'type': 'RawText', 'content': 'ABC-2 Beta'}]
        },
        {
          'type': 'CodeFence',
          'line_number': 6,
          'language': 'yaml',
          'children': [
            {'type': 'RawText', 'content': 'field1: 8\nfield2: value\n'}
          ]
        },
        {
          'type': 'Paragraph',
          'line_number': 10,
          'children': [
            {'type': 'RawText', 'content': 'I have some more text here.'}
          ]
        },
        {
          'type': 'Heading',
          'line_number': 12,
          'level': 2,
          'children': [{'type': 'RawText', 'content': 'My Subheading'}]
        },
        {
          'type': 'Paragraph',
          'line_number': 14,
          'children': [{'type': 'RawText', 'content': 'yo'}]
        },
        {
          'type': 'Heading',
          'line_number': 16,
          'level': 2,
          'children': [
            {'type': 'RawText', 'content': 'ABC-2-1 Beta - Bruh'}
          ]
        }
      ]
    }
    assert parsed_md_doc == expected


if __name__ == "__main__":
  scaffold_crud_test_directory()
  parsed_md_doc = crud.parse_md_doc(Path("./test_data/a/input_a.md"))
  print(parsed_md_doc)