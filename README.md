# VS Code Workspaces Guide

This repository contains multiple independent experiments, each with their own Python virtual environment (`.venv`). To avoid Python interpreter conflicts in VS Code, each experiment has its own workspace file.

## Quick Start

Open workspace files directly:
- **Root workspace**: `reproducibility.code-workspace` - Shows all experiments in a multi-root workspace
- **Individual experiments**: `{experiment_folder}/{experiment_name}.code-workspace` - Dedicated workspace with correct Python interpreter (e.g., `stratum/scrabble_player_rating/scrabble_player_rating.code-workspace`)

## Workspace Files

### Individual Experiment Workspaces
Each experiment workspace:
- Sets the Python interpreter to the experiment's `.venv`
- Activates the virtual environment in the terminal
- Configures Python analysis paths correctly

**Location**: `{experiment_folder}/{experiment_name}.code-workspace`

### Root Workspace
The root workspace (`reproducibility.code-workspace`) is a **multi-root workspace** that serves several important purposes:

**Why it's needed:**
- **Unified view**: Provides a single workspace that shows all experiments as separate folders, making it easy to browse and navigate between different experiments
- **Repository overview**: When you need to see the big picture or work across multiple experiments, this workspace gives you access to everything at once
- **File organization**: VS Code's file explorer shows each experiment as a distinct root folder, making it clear which files belong to which experiment
- **Shared settings**: Applies repository-wide settings like excluding `.venv` folders and `__pycache__` directories from the file explorer and file watchers (improving performance)
- **Extension recommendations**: Ensures all team members get prompted to install the recommended Python extensions

**When to use it:**
- Browsing/searching across multiple experiments
- Comparing code between experiments
- Managing the repository structure
- Initial exploration of the codebase

**Note**: VS Code may prompt you to select a Python interpreter for each folder. For focused development work on a single experiment, use individual experiment workspaces instead.

## Adding a New Experiment Workspace

### Option 1: Use the setup script (Recommended)
```bash
# Set up a new experiment workspace
./setup_new_exp.sh stratum/uk-housing

# This will:
# - Create the folder if it doesn't exist (including parent folders)
# - Create the workspace file: stratum/uk-housing/uk-housing.code-workspace
# - Use the template from workspace-template.json (or default template)
# - Automatically update reproducibility.code-workspace to include the new experiment
```

Then:
1. Set up your experiment (usually via `./run.sh` in the experiment folder, which creates the `.venv` automatically)
2. Open the workspace: `code stratum/uk-housing/uk-housing.code-workspace`

### Option 2: Manual setup
1. Create your experiment folder and set up the environment (usually via `./run.sh`)
2. Create a workspace file: `{experiment_folder}/{experiment_name}.code-workspace`
3. Use the template from `workspace-template.json` or copy from an existing workspace
4. Manually add the experiment folder to `reproducibility.code-workspace` if you want it in the root workspace

## Tips

- **For focused work**: Use individual experiment workspaces
- **For browsing**: Use the root workspace
- VS Code will remember which workspace you last opened
- You can pin workspaces in VS Code's File menu for quick access
