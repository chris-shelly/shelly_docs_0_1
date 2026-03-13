# Shelly Docs, the TUI/CLI Knowledge Mgmt Application for Agents and Humans
Use Markdown documents to manage various types of documentation Items within a codebase and/or filesystem.

Users can specify type of documentation Item in markdown by using Item Tags in Headers.

## Concept
Humans will primarily interact with Shelly Docs via TUI (Terminal User Interface) built in Textual

Agents will primarily interact with Shelly Docs via CLI, retrieving structured data for use in gathering context for accomplishing tasks.

Goal is to provide a more effective way to manage project documentation and knowledge as a source for agentic coding workflows, spec-driven development, context engineering techniques.


## Directory Structure
- `/shelly_docs`
  - source code for the application
- `/mgmt_docs`
  - Knowledge Base of Documentation Items for this project
- `/experiment_code`
  - code snippets for small scale experiments
- `/tests`
  - pytest tests and config
