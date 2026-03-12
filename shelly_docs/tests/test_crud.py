from pathlib import Path
import pytest
from ruamel.yaml import YAML

import src.shelly_docs.be.crud.crud as crud

yaml = YAML()


class TestGetMDDocsInDir:
    def test_finds_md_files(self, kb_path):
        docs = crud.get_md_docs_in_dir(Path(kb_path))
        names = sorted([d.name for d in docs])
        assert names == ["input_a.md", "input_b.md"]

    def test_ignores_non_md(self, kb_path):
        (Path(kb_path) / "notes.txt").write_text("not markdown")
        docs = crud.get_md_docs_in_dir(Path(kb_path))
        names = [d.name for d in docs]
        assert "notes.txt" not in names

    def test_recursive(self, kb_path):
        sub = Path(kb_path) / "subdir"
        sub.mkdir()
        (sub / "nested.md").write_text("# Nested\n")
        docs = crud.get_md_docs_in_dir(Path(kb_path))
        names = [d.name for d in docs]
        assert "nested.md" in names

    def test_empty_dir(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        docs = crud.get_md_docs_in_dir(empty)
        assert docs == []


class TestGetItems:
    def test_returns_items_from_all_files(self, kb_path, config):
        items = crud.get_items(kb_path, config)
        keys = [i['title'].split(' ')[0] for i in items]
        # template has ABC-1, ABC-2, ABC-2-1 in input_a.md and XYZ-1, XYZ-2, ABC-3 in input_b.md
        assert "ABC-1" in keys
        assert "XYZ-1" in keys
        assert "ABC-3" in keys

    def test_filters_by_config_tags(self, kb_path):
        items = crud.get_items(kb_path, {"item_tags": ["ABC"]})
        keys = [i['title'].split(' ')[0] for i in items]
        assert "ABC-1" in keys
        assert "XYZ-1" not in keys
        assert "XYZ-2" not in keys

    def test_empty_dir(self, tmp_path):
        empty = tmp_path / "empty_kb"
        empty.mkdir()
        # Need a shellydocs.yaml for get_items to work (it calls get_config internally
        # only if we use write_items_to_state; get_items takes config directly)
        items = crud.get_items(str(empty), {"item_tags": ["ABC"]})
        assert items == []


class TestWriteItemsToState:
    def test_creates_state_yaml(self, kb_path):
        crud.write_items_to_state(kb_path)
        assert (Path(kb_path) / "state.yaml").exists()

    def test_state_contains_all_items(self, kb_path, config):
        crud.write_items_to_state(kb_path)
        state = yaml.load((Path(kb_path) / "state.yaml").read_text())
        keys = list(state["items"].keys())
        assert "ABC-1" in keys
        assert "ABC-2" in keys
        assert "XYZ-1" in keys
        assert "ABC-3" in keys

    def test_overwrites_existing_state(self, kb_path):
        crud.write_items_to_state(kb_path)
        crud.write_items_to_state(kb_path)
        state = yaml.load((Path(kb_path) / "state.yaml").read_text())
        # Should not have duplicated items
        keys = list(state["items"].keys())
        assert len(keys) == len(set(keys))


class TestGetState:
    def test_reads_state(self, kb_with_state):
        state = crud.get_state(kb_with_state)
        assert "items" in state
        assert isinstance(state["items"], dict)

    def test_missing_state_raises(self, kb_path):
        with pytest.raises(Exception):
            crud.get_state(kb_path)


class TestGetItem:
    def test_gets_existing_item(self, kb_with_state):
        item = crud.get_item(kb_with_state, "ABC-1")
        assert "Alpha" in item["title"]

    def test_missing_item_raises(self, kb_with_state):
        with pytest.raises(KeyError):
            crud.get_item(kb_with_state, "NOPE-99")


class TestPutItem:
    def test_append_new_item_no_parent(self, kb_with_state, config):
        path = kb_with_state
        new_item = {
            "path": "input_a.md",
            "markdown": "# ABC-99 Brand New\nSome content here.\n",
            "title": "ABC-99 Brand New",
            "parent": None,
        }
        crud.put_item(path, "ABC-99", new_item, config)
        text = (Path(path) / "input_a.md").read_text()
        assert "ABC-99 Brand New" in text
        # Verify state updated
        state = crud.get_state(path)
        assert "ABC-99" in state["items"]

    def test_update_existing_item(self, kb_with_state, config):
        path = kb_with_state
        updated_item = {
            "path": "input_a.md",
            "markdown": "# ABC-1 Alpha Updated\nNew content for ABC-1.\n",
            "title": "ABC-1 Alpha Updated",
            "parent": None,
        }
        crud.put_item(path, "ABC-1", updated_item, config)
        text = (Path(path) / "input_a.md").read_text()
        assert "Alpha Updated" in text
        assert "New content for ABC-1." in text

    def test_create_new_file(self, kb_with_state, config):
        path = kb_with_state
        new_item = {
            "path": "brand_new.md",
            "markdown": "# ABC-50 Fresh\nFresh content.\n",
            "title": "ABC-50 Fresh",
            "parent": None,
        }
        crud.put_item(path, "ABC-50", new_item, config)
        assert (Path(path) / "brand_new.md").exists()
        text = (Path(path) / "brand_new.md").read_text()
        assert "ABC-50 Fresh" in text

    def test_invalid_tag_raises(self, kb_with_state, config):
        path = kb_with_state
        bad_item = {
            "path": "input_a.md",
            "markdown": "# NOPE-1 Bad Tag\n",
            "title": "NOPE-1 Bad Tag",
            "parent": None,
        }
        with pytest.raises(ValueError, match="does not match any configured item_tags"):
            crud.put_item(path, "NOPE-1", bad_item, config)

    def test_duplicate_key_different_file_raises(self, kb_with_state, config):
        path = kb_with_state
        # ABC-1 exists in input_a.md, try to add it to input_b.md
        dup_item = {
            "path": "input_b.md",
            "markdown": "# ABC-1 Duplicate\nDuplicated.\n",
            "title": "ABC-1 Duplicate",
            "parent": None,
        }
        with pytest.raises(ValueError, match="already exists in a different file"):
            crud.put_item(path, "ABC-1", dup_item, config)

    def test_insert_child_after_parent(self, kb_with_state, config):
        path = kb_with_state
        child_item = {
            "path": "input_a.md",
            "markdown": "## ABC-2-2 New Child\nChild content.\n",
            "title": "ABC-2-2 New Child",
            "parent": "ABC-2",
            "level": 2,
        }
        crud.put_item(path, "ABC-2-2", child_item, config)
        text = (Path(path) / "input_a.md").read_text()
        assert "ABC-2-2 New Child" in text

    def test_state_updated_after_put(self, kb_with_state, config):
        path = kb_with_state
        new_item = {
            "path": "input_a.md",
            "markdown": "# ABC-77 State Check\nChecking state.\n",
            "title": "ABC-77 State Check",
            "parent": None,
        }
        crud.put_item(path, "ABC-77", new_item, config)
        state = crud.get_state(path)
        assert "ABC-77" in state["items"]


class TestGetSiblingPositioning:
    def test_finds_sibling_end_line(self, kb_with_state):
        state = crud.get_state(kb_with_state)
        # ABC-2-1 is a child of ABC-2; inserting a new ABC-2-2 should find sibling position
        new_item = {
            "parent": "ABC-2",
            "path": "input_a.md",
            "level": 2,
        }
        pos = crud.get_sibling_positioning(state, new_item)
        assert pos is not None
        assert isinstance(pos, int)

    def test_no_siblings_returns_none(self, kb_with_state):
        state = crud.get_state(kb_with_state)
        # XYZ-1 has no children, so a new XYZ-1-1 should find no siblings
        new_item = {
            "parent": "XYZ-1",
            "path": "input_b.md",
            "level": 2,
        }
        pos = crud.get_sibling_positioning(state, new_item)
        assert pos is None


class TestDeleteItem:
    def test_removes_item_from_file(self, kb_with_state):
        path = kb_with_state
        crud.delete_item(path, "ABC-1")
        text = (Path(path) / "input_a.md").read_text()
        assert "ABC-1 Alpha" not in text

    def test_state_updated(self, kb_with_state):
        path = kb_with_state
        crud.delete_item(path, "ABC-1")
        state = crud.get_state(path)
        assert "ABC-1" not in state["items"]

    def test_missing_key_raises(self, kb_with_state):
        with pytest.raises(KeyError):
            crud.delete_item(kb_with_state, "NOPE-99")

    def test_missing_file_raises(self, kb_with_state):
        path = kb_with_state
        state = crud.get_state(path)
        # Manually add a fake item pointing to a nonexistent file
        state["items"]["FAKE-1"] = {
            "title": "FAKE-1 Ghost",
            "path": "ghost.md#fake-1-ghost",
        }
        yaml.dump(state, Path(path) / "state.yaml")
        with pytest.raises(FileNotFoundError):
            crud.delete_item(path, "FAKE-1")

    def test_heading_not_found_raises(self, kb_with_state):
        path = kb_with_state
        state = crud.get_state(path)
        # Add a fake item pointing to a real file but with wrong heading
        state["items"]["FAKE-2"] = {
            "title": "FAKE-2 Phantom",
            "path": "input_a.md#fake-2-phantom",
        }
        yaml.dump(state, Path(path) / "state.yaml")
        with pytest.raises(ValueError, match="not found in"):
            crud.delete_item(path, "FAKE-2")


class TestConvertNewItemMD:
    def test_converts_single_item(self, kb_path, config):
        new_item_obj = {
            "kb_path": kb_path,
            "filepath": "input_a.md",
            "markdown": "# ABC-10 Single\nSingle item content.\n",
        }
        result = crud.convert_new_item_md(new_item_obj)
        assert len(result) == 1
        assert "ABC-10" in result[0]["key"]

    def test_converts_multiple_items(self, kb_path, config):
        # Write a file whose content matches the markdown we'll pass,
        # so that heading validation against the file succeeds for all items.
        multi_md = "# ABC-10 First\nContent one.\n# ABC-11 Second\nContent two.\n"
        (Path(kb_path) / "multi.md").write_text(multi_md)
        new_item_obj = {
            "kb_path": kb_path,
            "filepath": "multi.md",
            "markdown": multi_md,
        }
        result = crud.convert_new_item_md(new_item_obj)
        assert len(result) == 2
        keys = [r["key"] for r in result]
        assert "ABC-10" in keys
        assert "ABC-11" in keys


class TestParseMDText:
    """Test `parse_md_text()`, getting the AST of a Markdown document/snippet, given the markdown string"""

    def test_parse_md_text(self, kb_path):
        parsed_md_doc = crud.parse_md_text(Path(f"{kb_path}/input_a.md").read_text())
        expected = {
            'type': 'Document',
            'footnotes': {},
            'line_number': 1,
            'children': [
                {
                    'type': 'Heading',
                    'line_number': 1,
                    'level': 1,
                    'children': [{'type': 'RawText', 'content': 'ABC-1 Alpha'}],
                },
                {
                    'type': 'Paragraph',
                    'line_number': 2,
                    'children': [
                        {'type': 'RawText', 'content': 'I have some text here.'}
                    ],
                },
                {
                    'type': 'Heading',
                    'line_number': 5,
                    'level': 1,
                    'children': [{'type': 'RawText', 'content': 'ABC-2 Beta'}],
                },
                {
                    'type': 'CodeFence',
                    'line_number': 6,
                    'language': 'yaml',
                    'children': [
                        {'type': 'RawText', 'content': 'field1: 8\nfield2: value\n'}
                    ],
                },
                {
                    'type': 'Paragraph',
                    'line_number': 10,
                    'children': [
                        {
                            'type': 'RawText',
                            'content': 'I have some more text here.',
                        }
                    ],
                },
                {
                    'type': 'Heading',
                    'line_number': 12,
                    'level': 2,
                    'children': [{'type': 'RawText', 'content': 'My Subheading'}],
                },
                {
                    'type': 'Paragraph',
                    'line_number': 14,
                    'children': [{'type': 'RawText', 'content': 'yo'}],
                },
                {
                    'type': 'Heading',
                    'line_number': 16,
                    'level': 2,
                    'children': [
                        {'type': 'RawText', 'content': 'ABC-2-1 Beta - Bruh'}
                    ],
                },
            ],
        }
        assert parsed_md_doc == expected


class TestParseMDDoc:
    """Test `parse_md_doc()`, getting the AST of a Markdown document, given its path"""

    def test_parse_md_doc(self, kb_path):
        parsed_md_doc = crud.parse_md_doc(Path(f"{kb_path}/input_a.md"))
        expected = {
            'type': 'Document',
            'footnotes': {},
            'line_number': 1,
            'children': [
                {
                    'type': 'Heading',
                    'line_number': 1,
                    'level': 1,
                    'children': [{'type': 'RawText', 'content': 'ABC-1 Alpha'}],
                },
                {
                    'type': 'Paragraph',
                    'line_number': 2,
                    'children': [
                        {'type': 'RawText', 'content': 'I have some text here.'}
                    ],
                },
                {
                    'type': 'Heading',
                    'line_number': 5,
                    'level': 1,
                    'children': [{'type': 'RawText', 'content': 'ABC-2 Beta'}],
                },
                {
                    'type': 'CodeFence',
                    'line_number': 6,
                    'language': 'yaml',
                    'children': [
                        {'type': 'RawText', 'content': 'field1: 8\nfield2: value\n'}
                    ],
                },
                {
                    'type': 'Paragraph',
                    'line_number': 10,
                    'children': [
                        {
                            'type': 'RawText',
                            'content': 'I have some more text here.',
                        }
                    ],
                },
                {
                    'type': 'Heading',
                    'line_number': 12,
                    'level': 2,
                    'children': [{'type': 'RawText', 'content': 'My Subheading'}],
                },
                {
                    'type': 'Paragraph',
                    'line_number': 14,
                    'children': [{'type': 'RawText', 'content': 'yo'}],
                },
                {
                    'type': 'Heading',
                    'line_number': 16,
                    'level': 2,
                    'children': [
                        {'type': 'RawText', 'content': 'ABC-2-1 Beta - Bruh'}
                    ],
                },
            ],
        }
        assert parsed_md_doc == expected
