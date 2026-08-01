# PROCESS-1 Running the `env` version of `shelly-docs`
## PROCESS-1-1 Activate Venv
First, make sure you have the venv activated
```bash
source .venv/Scripts/activate
```
## PROCESS-1-2 Update version in pyproject
Then, update the version in the pyproject.toml

## PROCESS-1-3 Sync to the `uv` project
Run `uv sync` with the venv activated, so that we now are running with the current version

# PROCESS-2 Installing to Rest of System
Build the wheel
```bash
uv build
```

Install system-wide
```bash
uv pip install $WHEEL_FILEPATH --system
```