# Shelly Docs, the TUI/CLI Knowledge Mgmt Application for Agents and Humans
Use Markdown documents to manage various types of documentation Items within a codebase and/or filesystem.

Users can specify type of documentation Item in markdown by using Item Tags in Headers.

Users can specify schema/structure of Items (Item typeshierarchy/nesting behavior, metadata, expected sub-sections, etc.)

## Concept
Humans will primarily interact with Shelly Docs via TUI (Terminal User Interface) built in Textual

Agents will primarily interact with Shelly Docs via CLI, retrieving structured data for use in gathering context for accomplishing tasks.

Goal is to build upon spec-driven development and context engineering techniques like the Ralph Loob and GSD.


## Directory Structure
- `/src`
  - source code for the application
- `/mgmt_docs`
  - Knowledge Base of Documentation Items for this project
- `/experiment_code`
  - code snippets for small scale experiments
