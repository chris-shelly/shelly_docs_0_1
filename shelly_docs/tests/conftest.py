import shutil
from pathlib import Path
import pytest


TEMPLATES_DIR = Path(__file__).parent / "templates"

def setup_template_kb(pytest_temp_path,template_key: str) -> str:
    """
    Choose a shelly-docs knowledge base to execute the test on
    """
    dest = pytest_temp_path / "kb"
    template_dir = Path(__file__).parent / "templates" / template_key
    if template_dir.is_dir():
        shutil.copytree(template_dir, dest)
        kb_path = str(dest)
        from src.shelly_docs.db.kb import init_kb
        init_kb(Path(kb_path))
        import src.shelly_docs.be.crud.crud as crud
        crud.write_items_to_state(kb_path)
        return kb_path
    raise ValueError("Template KB Issue, incorrect template kb directory")


@pytest.fixture
def config():
    """Default config matching the template KB's shellydocs.yaml."""
    return {"item_tags": ["ABC", "XYZ"]}


@pytest.fixture
def kb_a(tmp_path):
    """KB path with state.yaml already written."""
    return setup_template_kb(tmp_path, "a")

@pytest.fixture
def kb_b(tmp_path):
    return setup_template_kb(tmp_path,"b")

@pytest.fixture
def kb_c(tmp_path):
    return setup_template_kb(tmp_path,"c")

@pytest.fixture
def kb_d(tmp_path):
    return setup_template_kb(tmp_path, "d")

@pytest.fixture
def kb_e(tmp_path):
    return setup_template_kb(tmp_path, "e")

import sqlite3
@pytest.fixture(scope="function")
def test_db(tmp_path):
    """
    Initialize the DB for the Knowledge Base with 4 tables:
    - items
    - item_ids
    - item_types
    - jobs
    """
    db_path = tmp_path / "kb.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()