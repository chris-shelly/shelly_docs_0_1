from src.shelly_docs.be.crud.query import match_item
class TestMatchItem:
  def test_positive(self):
    
    positive_item_data = {"status": "done"}
    assert match_item(positive_item_data,{"status":"done"}) == True
  def test_negative(self):
    negative_item_data = {"status": "drafting"}
    assert match_item(negative_item_data, {"status": "done"}) == False

from src.shelly_docs.be.crud.query import query_items
class TestQueryItems:
  def test_one_value_condition(self):
    items = {
      "ABC-1": {"title": "ABC-1 Alpha", "data": {"status": "done"}},
      "ABC-2": {"title": "ABC-2 Beta","data": {"status": "drafting"}}
    }
    query = {"status": "done"}
    actual_results = query_items(items, query)
    assert actual_results == [{"title": "ABC-1 Alpha","data": {"status": "done"}}] # should only return the item with 'status: done'
    pass
  def test_multiple_value_conditions(self):
    items = {
      "ABC-1": {"title": "ABC-1 Alpha", "data": {"status": "done", "related_to": "DESIGN-2-2"}},
      "ABC-2": {"title": "ABC-2 Beta","data": {"status": "drafting"}}
    }
    query = {"status": "done", "related_to": "DESIGN-2-2"}
    actual_results = query_items(items, query)
    assert actual_results == [{"title": "ABC-1 Alpha","data": {"status": "done", "related_to": "DESIGN-2-2"}}]
  
from src.shelly_docs.be.crud.query import query_pipeline
class TestQueryPipeline:
  def test_dict(self):
    items = {
      "ABC-1": {"title": "ABC-1 Alpha", "data": {"status": "done", "related_to": "DESIGN-2-2"}},
      "ABC-2": {"title": "ABC-2 Beta","data": {"status": "drafting"}}
    }
    query = [{"status": "done"}, {"related_to": "DESIGN-2-2"}]
    actual_results = query_pipeline(items, query)
    print(actual_results)
    assert actual_results == [{"title": "ABC-1 Alpha","data": {"status": "done", "related_to": "DESIGN-2-2"}}] # should only return the item with 'status: done'
    pass
  def test_count(self):
    """
    `$count` is used to get the count of a list of items
    for now, can only be called via pipeline from a list of items
    """
    items = {
      "ABC-1": {"title": "ABC-1 Alpha", "data": {"status": "done", "related_to": "DESIGN-2-2"}},
      "ABC-2": {"title": "ABC-2 Beta","data": {"status": "drafting"}},
      "ABC-3": {"title": "ABC-3 Charlie","data": {"status": "done"}}
    }
    query = [{"status": "done"}, "$count"]
    actual_results = query_pipeline(items, query)
    assert actual_results == 2
  def test_sum(self):
    """
    `$sum` is used to get the sum of a field of a list of items
    `"$sum: field"`
    for now, can only be called via pipeline from a list of items
    """
    items = {
      "ABC-1": {"title": "ABC-1 Alpha", "data": {"status": "done", "related_to": "DESIGN-2-2", "story_points": 5}},
      "ABC-2": {"title": "ABC-2 Beta","data": {"status": "drafting", "story_points": 8}},
      "ABC-3": {"title": "ABC-3 Charlie","data": {"status": "done", "story_points": 3}}
    }
    query = [{"status": "done"}, {"$sum":"story_points"}]
    actual_results = query_pipeline(items, query)
    assert actual_results == 8
  def test_concat(self):
    """
    `$concat` is used to concatenate a string from a field of a list of items
    `"$concat: field"`
    for now, can only be called via pipeline from a list of items
    """
    items = {
      "ABC-1": {"title": "ABC-1 Alpha", "data": {"status": "done", "related_to": "DESIGN-2-2", "story_points": 5, "trace": "hi"}},
      "ABC-2": {"title": "ABC-2 Beta","data": {"status": "drafting", "story_points": 8}},
      "ABC-3": {"title": "ABC-3 Charlie","data": {"status": "done", "story_points": 3, "trace": "there"}}
    }
    query = [{"status": "done"}, {"$concat":"trace"}]
    actual_results = query_pipeline(items, query)
    assert actual_results == "hithere"