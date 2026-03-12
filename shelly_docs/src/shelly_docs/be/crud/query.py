"""
Query engine for filtering Shelly Docs Items by their `data` field.
Supports MongoDB-like query operators.
"""
from typing import Union

def query_pipeline(items: dict, query_pipeline: list[Union[dict, str]]) -> list[dict]:
  """
  Run a list of queries on the items
  """
  pipeline_results = items
  for query in query_pipeline:
    pipeline_results = query_items(pipeline_results, query)
  return pipeline_results

def query_items(items: dict, query: Union[dict,str]) -> list[dict]:
  """Filter state items by matching their `data` field against a query.
  Args:
    items: dict of item_key -> item_dict (from state['items'])
    query: MongoDB-like query dict (e.g. {"status": "done"} or {"priority": {"$gt": 3}})
  Returns:
    list of matching item dicts
  """
  results = []
  if isinstance(items, dict):
    for item_key, item in items.items():
      data = item.get("data")
      if data is None:
        continue
      if match_item(data, query):
        results.append(item)
  elif isinstance(items, list):
    # if items are a list, we can then consider aggregations ($sum, $count)
    # check if query is an agggregation

    if isinstance(query, str): # ex. "$count"
      return aggregate_items(items, query)
    elif isinstance(query, dict) and (any(val in query.keys() for val in ("$sum","$concat"))): # ex. "$sum: field"
      return aggregate_items(items, query)
    else:
      for item in items:
        data = item.get("data")
        if data is None:
          continue
        if match_item(data, query):
          results.append(item)
  return results


def match_item(data: dict, query: dict) -> bool:
  """Test if a single item's data satisfies the query."""
  for key, condition in query.items():
    if key == "$or":
      if not any(match_item(data, sub_query) for sub_query in condition):
        return False
    elif key == "$and":
      if not all(match_item(data, sub_query) for sub_query in condition):
        return False
    else:
      field_value = data.get(key)
      if not _evaluate_condition(field_value, condition, key in data):
        return False
  return True

def aggregate_items(items: list, query: Union[str, dict]):
  if isinstance(query, str):
    if query == "$count":
      return len(items)
  elif isinstance(query, dict):
    # only take the first item
    query_key, query_field = list(query.items())[0]
    if query_key == "$sum":
      result = 0
      for item in items:
        item_data = item.get("data",{}).get(query_field)
        if (item_data is not None) and (isinstance(item_data,(int, float))):
          result += item_data
    
    elif query_key == "$concat":
      result = ""
      for item in items:
        item_data = item.get("data",{}).get(query_field)
        if (item_data is not None) and (isinstance(item_data,str)):
          result += item_data
    return result


def _evaluate_condition(field_value, condition, field_exists: bool) -> bool:
  """Equality check (scalar) or operator evaluation (dict with $gt, etc.)."""
  if isinstance(condition, dict):
    for operator, operand in condition.items():
      if not _apply_operator(field_value, operator, operand, field_exists):
        return False
    return True
  else:
    # Simple equality
    if not field_exists:
      return False
    return field_value == condition


def _apply_operator(field_value, operator: str, operand, field_exists: bool) -> bool:
  """Apply a single comparison operator."""
  if operator == "$ne":
    if not field_exists:
      return True
    return field_value != operand
  if not field_exists:
    return False
  if operator == "$gt":
    try:
      return field_value > operand
    except TypeError:
      return False
  elif operator == "$gte":
    try:
      return field_value >= operand
    except TypeError:
      return False
  elif operator == "$lt":
    try:
      return field_value < operand
    except TypeError:
      return False
  elif operator == "$lte":
    try:
      return field_value <= operand
    except TypeError:
      return False
  elif operator == "$in":
    return field_value in operand
  else:
    raise ValueError(f"Unknown operator: {operator}")
