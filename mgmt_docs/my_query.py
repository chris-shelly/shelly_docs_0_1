from rich import print
from shelly_docs.kb import KnowledgeBase

kb = KnowledgeBase(".")

print(kb.sql_query("SELECT key, type FROM items WHERE type = 'PROMPT'"))