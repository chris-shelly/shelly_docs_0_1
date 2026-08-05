# Shelly Docs, the TUI/CLI Knowledge Mgmt Application for Agents and Humans
Use Markdown documents to manage various types of documentation Items within a codebase and/or filesystem.

Users can specify type of documentation Item in markdown by using Item Tags in Headers.

## Concept
Agents will primarily interact with Shelly Docs via CLI, retrieving structured data for use in gathering context for accomplishing tasks.

Goal is to provide a more effective way to hold semi-structured data source for:
- notetaking
- productivity
- document analysis
- system documentation (requirements, designs, tests, etc.)

## Getting Started
- Clone the repo
- Install
  - per [PROCESS-2](./mgmt_docs/dev_processes/local_env_install_and_testing.md#process-2-installing-to-rest-of-system), install via `uv`
``` bash
# build a python wheel
uv build

# install on system (or exclude `--system` flag if you want to install to a specific envt)
uv pip install $WHEEL_FILEPATH --system
```
- Make your first Knowledge Base
  - make/choose a folder
  - change to that directory
  - make a `shellydocs.yaml`
```yaml
item_tags: # tags to recognize as items
  - DOC
jobs:
```
  - Create an Item in a markdown file
`````md
# DOC-1 Hello 'shelly_docs' world
```yaml (data)
foo: bar
```
Hi, this is my first Item
# DOC-2 Hi again
Hello, this is my second Item
`````
  - Set a Knowledge Base path (`shelly-docs kb set --path "."`)
  - Run `shelly-docs kb update`
  - Verify that a `state.yaml` file was generated


You can update Items and the Knowledge base programmatically by:
- manual file edits and `shelly-docs kb update`
- `shelly-docs CLI`
- `shelly_docs` python library

We also have the basics covered in a skill. You can use `shelly-docs skill load` to load the skill to a directory.

## Directory Structure
- `/shelly_docs`
  - code for the application
- `/mgmt_docs`
  - Knowledge Base of Items for this project
- `/experiment_code`
  - code snippets for small scale experiments

