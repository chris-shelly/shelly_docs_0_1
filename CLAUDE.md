# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Shelly Docs is a TUI/CLI Knowledge Management application. It parses Markdown documents to extract structured documentation "Items" identified by configurable tags (e.g., USECASE-1, DESIGN-2, ACTOR-1) in headings. Humans use the TUI (Textual); AI agents use the CLI for structured data retrieval.

## Running the Application

```bash
# Run the TUI app
python src/main.py

# Run CRUD module directly (for testing backend)
python src/be/crud.py

# Run markdown parsing experiments
python experiment_code/md_parsing/md_parsing.py
```

## Testing
Use `pytest` for Unit tests of functions. In progress with bulding the tests.
- `test_crud.py` for 

## Architecture

```
shelly_docs/src/shelly_docs/tui/tui.py          → TUI frontend (Textual app, screens, widgets)
shelly_docs/src/shelly_docs/tui/styles.tcss          → Textual CSS for the TUI in General
shelly_docs/src/shelly_docs/tui/knowledge_base_widget.tcss          → Textual CSS for the TUI Knowledge Base Widgets
shelly_docs/src/shelly_docs/be/shelly_docs/config.py     → Reads shellydocs.yaml config from a Knowledge Base directory
shelly_docs/src/shelly_docs/be/crud/crud.py       → Creating and Reading Shelly Doc Items
shelly_docs/src/shelly_docs/be/crud/query.py       → Querying
shelly_docs/src/shelly_docs/be/crud/shelly_doc_processing.py       → Markdown parsing (mistletoe) and item extraction
shelly_docs/src/shelly_docs/main.py      → Typer CLI
```

### Functionality/
- User provides Knowledge Base path
- `config.get_config()` reads `shellydocs.yaml` for item_tags, which determines the valid types of Shelly Doc Items to look for in the Knowledge Base
- `crud.get_items()` recursively finds `.md` files, and processes items parses each to an AST via mistletoe, and traverses headings matching tag patterns (regex `^(TAG-\d+.*)`) 
- data can be accessed and updated via TUI or returned as structured data via CLI.

**Key backend functions in `crud.py`:**
- `get_items(path, config)` — entry point: finds docs and extracts all items
- `parse_md_doc(path)` — converts markdown file to JSON AST
- `traverse_for_items(doc, pattern, items)` — recursive AST traversal matching item headings
- `get_text_from_children(node)` — extracts text from AST child nodes

**TUI structure in `main.py`:** `ShellyDocs` (App) → `Home` (path input widget) → `KnowledgeBaseScreen` (displays config + items). Components communicate via Textual messages (e.g., `PathProvided`).

## Key Dependencies

- **textual** — TUI framework
- **typer** - CLI Framework
- **mistletoe** — Markdown-to-AST parser
- **ruamel.yaml** — YAML config parsing
- **pytest** - Testing

## Knowledge Base Format
A Knowledge Base (KB) directory contains:
- `shellydocs.yaml` config file defining `item_tags` 
- `.md` files with Items declared via headings (e.g., `## USECASE-1 Title`). Files can be nested within directories. 
- The `mgmt_docs/` directory is the KB for this project itself.

After processing Items, a `state.yaml` file is created/updated to reflect the current set of Items in the Knowledge Base.

## Item Format
An Item is a section of a Markdown document, declared with a Markdown heading and Item tag.

Items can have a 'data' field, which is declared as a codefenced `yaml (data)` block.