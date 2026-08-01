import subprocess

import subprocess
import sys

filepath = "./code_to_run/hello_and_input.py"

try:
    subprocess.run([sys.executable, filepath, "DOC-123"], check=True)
except FileNotFoundError:
    print(f"File not found: {filepath}")
except subprocess.CalledProcessError as e:
    print(f"Script exited with error: {e}")
