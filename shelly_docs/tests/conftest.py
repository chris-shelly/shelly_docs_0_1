import shutil
from pathlib import Path
import pytest


TEMPLATES_DIR = Path(__file__).parent / "templates" / "a"


@pytest.fixture
def kb_path(tmp_path):
    """Copy template KB into a fresh temp directory and return its string path."""
    dest = tmp_path / "kb"
    shutil.copytree(TEMPLATES_DIR, dest)
    return str(dest)


@pytest.fixture
def config():
    """Default config matching the template KB's shellydocs.yaml."""
    return {"item_tags": ["ABC", "XYZ"]}


@pytest.fixture
def kb_with_state(kb_path):
    """KB path with state.yaml already written."""
    import src.shelly_docs.be.crud.crud as crud
    crud.write_items_to_state(kb_path)
    return kb_path
