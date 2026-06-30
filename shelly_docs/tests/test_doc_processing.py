import shelly_docs.be.crud.shelly_doc_processing as sdp


class TestGetItemContent:
  def test_item_with_data_block(self):
    item = {
      "start_line": 171,
      "path": "use_cases\\use_cases.md#usecase-16-enter-tui",
      "level": 1,
      "end_line": 181,
      "markdown": "# USECASE-16 Enter TUI\n```yaml (data)\nstatus: done\n```\nEnter the TUI from a CLI Command\n\n\n```bash\nshelly-docs tui\n```\n\n",
      "title": "USECASE-16 Enter TUI",
      "data": {
        "status": "done",
        "type": "USECASE"
      },
      "key": "USECASE-16",
      "parent": None
    }
    content = sdp.get_item_content(item)
    expected ="Enter the TUI from a CLI Command\n\n\n```bash\nshelly-docs tui\n```\n"
    assert content == expected
  def test_item_with_no_data_block(self):
    item = {
      "start_line": 64,
      "path": "system\\be.md#system-3-2-3-match_item",
      "level": 3,
      "end_line": 74,
      "markdown": "### SYSTEM-3-2-3 `match_item()`\nEvaluates Logical Conditions to filter Items\n\nImportant Query logical keywords:\n- `$ne`\n-`$gt`\n- `$gte`\n- `$lt`\n- `$lte`\n- `$in`\n\n",
      "title": "SYSTEM-3-2-3 `match_item()`",
      "data": None,
      "key": "SYSTEM-3-2-3",
      "parent": "SYSTEM-3-2"
    }
    content = sdp.get_item_content(item)
    expected = "Evaluates Logical Conditions to filter Items\n\nImportant Query logical keywords:\n- `$ne`\n-`$gt`\n- `$gte`\n- `$lt`\n- `$lte`\n- `$in`\n"
    assert content == expected