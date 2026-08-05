# `shellydocs.yaml`
A Shelly Docs Knowledge Base is a file folder that has:
- **`{kb_path}/shellydocs.yaml`**
  - acts as the root of the knowledge base folder
  - specifies the item types (`item_tags`) and jobs (`jobs`) available in that knowledge base
- `{kb_path}/state.yaml`

```yaml
item_tags:
- WEEK # a calendar week, has days and goals, used for goals and productivity reporting
- DAY # a calendar day
- TASK # a discrete task to be completed
- THING # non-work activity
- GOAL # goal/theme for a given week
- DOC # a document, used for notetaking and reference to pieces of information
- EVENT # an activity that does not yield direct productivity output
jobs:
- name: set_dates_on_workouts
  job_type: item
  script: set_date_on_workout.py
  active: false
  item_types:
  - TASK
```