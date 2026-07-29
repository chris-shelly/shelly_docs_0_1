import shutil
from pathlib import Path
import pytest


TEMPLATES_DIR = Path(__file__).parent / "templates" / "a"
TEMPLATES_DIR_2 = Path(__file__).parent / "templates" / "b"

def set_template_kb(template_key: str) -> Path:
    """
    Choose a shelly-docs knowledge base to execute the test on
    """
    
    template_dir = Path(__file__).parent / "templates" / template_key
    if template_dir.is_dir():
        return template_dir
    raise ValueError("Template KB Issue, incorrect template kb directory")


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
