from shelly_docs.kb import KnowledgeBase, Item
import shelly_docs.be.crud.md_handling as mdh
import os



class TestParseItem:
  pass
class TestGetDataBlock:
  def test_get_data_block(self):
    item_markdown="""
# ABC-2 Beta
```yaml (data)
field1: 8
field2: value
```
I have some more text here.

## My Subheading

yo
"""
    data = mdh.get_data_block(item_markdown)
    assert data == {'field1': 8, 'field2': 'value'}

class TestSetDataBlock:
  def test_set_data_block(self):
    item_markdown="""
# ABC-2 Beta
```yaml (data)
field1: 8
field2: value
```
I have some more text here.

## My Subheading

yo
"""
    new_md = mdh.set_data_block(item_markdown, {'status': 'updated'})
    data = mdh.get_data_block(new_md)
    assert data == {'status': 'updated'}

class TestGetContent:
  def test_get_content(self):
    item_markdown="""# ABC-2 Beta
```yaml (data)
field1: 8
field2: value
```
I have some more text here.

## My Subheading

yo
"""
    new_md = mdh.get_content(item_markdown)
    assert new_md == """I have some more text here.

## My Subheading

yo"""

class TestSetContent:
  def test_set_content(self):
    item_markdown="""# ABC-2 Beta
```yaml (data)
field1: 8
field2: value
```
I have some more text here.

## My Subheading

yo
"""
    new_content = "Hey, what's up"
    new_md = mdh.set_content(item_markdown, new_content)
    assert new_md == """# ABC-2 Beta
```yaml (data)
field1: 8
field2: value
```
Hey, what's up"""


