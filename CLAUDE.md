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

No test framework, linter, or build system is configured yet.

## Architecture

```
src/main.py          → TUI frontend (Textual app, screens, widgets)
src/be/config.py     → Reads shellydocs.yaml config from a Knowledge Base directory
src/be/crud.py       → Markdown parsing (mistletoe) and item extraction
src/styles.tcss      → Textual CSS for the TUI
```

**Data flow:** User provides KB path → `config.get_config()` reads `shellydocs.yaml` for item_tags → `crud.get_items()` recursively finds `.md` files, parses each to an AST via mistletoe, and traverses headings matching tag patterns (regex `^(TAG-\d+.*)`) → results displayed in TUI or returned as structured data.

**Key backend functions in `crud.py`:**
- `get_items(path, config)` — entry point: finds docs and extracts all items
- `parse_md_doc(path)` — converts markdown file to JSON AST
- `traverse_for_items(doc, pattern, items)` — recursive AST traversal matching item headings
- `get_text_from_children(node)` — extracts text from AST child nodes

**TUI structure in `main.py`:** `ShellyDocs` (App) → `Home` (path input widget) → `KnowledgeBaseScreen` (displays config + items). Components communicate via Textual messages (e.g., `PathProvided`).

## Key Dependencies

- **textual** — TUI framework
- **mistletoe** — Markdown-to-AST parser
- **ruamel.yaml** — YAML config parsing

## Knowledge Base Format

A Knowledge Base directory contains a `shellydocs.yaml` config file defining `item_tags` and `.md` files with items as headings (e.g., `## USECASE-1 Title`). The `mgmt_docs/` directory is the KB for this project itself.

## Development Notes

- `experiment_code/` contains prototyping/research code, separate from the main app
- Item content extraction (`get_item()` for full item content) is actively being developed
- No `requirements.txt` or `pyproject.toml` exists yet — dependencies must be installed manually
