import os
from pathlib import Path

import shelly_docs.main
from shelly_docs.kb import KnowledgeBase, Item


class TestLoadSkill:
  def test_load_skill(self, kb_a):
    """Test the loading of a skill to a directory"""
    print("\n---test_load_skill---")
    kb = KnowledgeBase(kb_a)
    print("running shelly-docs skill load")
    shelly_docs.main.skill_load(Path(kb_a) / ".claude/skills/")

    print("ls kb_a",os.listdir(Path(kb_a)))
    print("ls kb_a/.claude/skills/", os.listdir(Path(kb_a) / ".claude/skills/"))
    print("ls kb_a/.claude/skills/shelly-docs", os.listdir(Path(kb_a) / ".claude/skills/shelly-docs"))