from shelly_docs.kb import KnowledgeBase, Item
import os
from pathlib import Path
from rich import print

class TestRunJobsItem:
  def test_job_invocation(self, kb_c):
    """
    Invoke a job on 'ABC' Items that writes data to a summary file based on the 'field1' values.
    """
    print("")
    kb = KnowledgeBase(kb_c)
    kb.run_jobs()
    print(f"test_job_invocation()::contents of {kb_c}", os.listdir(kb_c))

    # check for the 'add_ABC_field1s' job output
      # ABC-1.txt
      # ABC-2.txt
      # ABC-2-1.txt
      # ABC-3.txt
    files = [
      "ABC-1.txt",
      "ABC-2.txt",
      "ABC-2-1.txt",
      "ABC-3.txt",
    ]
    for file in files:
      output_path = Path(kb_c) / file
      print(f"test_job_invocation()::{file}")
      target_item_key = file.split(".")[0]
      print(f"test_job_invocation()::target item key", target_item_key)
      item = kb.get_item(target_item_key)
      if item.data is not None:
        field1 = item.data.get("field1")
        assert str(field1) == (output_path.read_text())
      else:
        assert "None" == (output_path.read_text())

class TestRunJobsQuery:
  def test_job_invocation(self, kb_c):
    """
    Invoke a job on the knowledgebase that runs a query and sums up 'field1.
    """
    print("")
    kb = KnowledgeBase(kb_c)
    kb.run_jobs()
    print(f"test_job_invocation()::contents of {kb_c}", os.listdir(kb_c))
    output_path = Path(kb_c) / "sum.txt"
    assert str('13') == output_path.read_text()