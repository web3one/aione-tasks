# Flyte Tasks Scripts

This directory contains scripts for working with Flyte tasks.

## Installation

Before running any scripts, make sure you have the required dependencies installed:

```bash
# On Linux/Mac
./install.sh

# On Windows
pip install flytekit
pip install flytekitplugins-flyteinteractive
```

## Scripts

### run_ide.py

This script executes the `ide.py` task and captures the VSCode access URL.

#### Usage

```bash
# On Linux/Mac
python3 run_ide.py

# On Windows
python run_ide.py
```

#### What it does

1. Executes the `ide.py` script in the `tasks` directory
2. Captures the output from the execution
3. Extracts the VSCode access URL from the output
4. Displays the URL to the user

If the script cannot find a VSCode URL in the output, it will display an error message and show the full output for debugging.

#### Example output

```
Executing /path/to/flyte-tasks/tasks/ide.py...

Output from ide.py:
forward
backward
... (other output) ...
VSCode instance is available at: https://example.com/vscode/12345

==================================================
VSCode access URL: https://example.com/vscode/12345
==================================================
```

## Troubleshooting

If you encounter any issues:

1. Make sure you have installed all required dependencies
2. Check the full output displayed by the script for any error messages
3. Verify that `ide.py` is executing correctly on its own
4. If the URL is not being detected, check the format of the URL in the output and update the regex patterns in `run_ide.py` if necessary