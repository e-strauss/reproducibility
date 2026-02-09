# VS Code Workspaces Guide

This repository contains multiple independent experiments, each with their own Python virtual environment (`.venv`). To avoid Python interpreter conflicts in VS Code, each experiment has its own workspace file.

## Quick Start

### Option 1: Use the helper script
```bash
# Open root workspace (shows all experiments)
./open-workspace.sh root

# Open specific experiment workspace
./open-workspace.sh scrabble
```

### Option 2: Open workspace files directly
- **Root workspace**: `reproducibility.code-workspace` - Shows all experiments in a multi-root workspace
- **Scrabble Player Rating**: `stratum/scrabble_player_rating/scrabble_player_rating.code-workspace` - Dedicated workspace with correct Python interpreter

## Workspace Files

### Individual Experiment Workspaces
Each experiment workspace:
- Sets the Python interpreter to the experiment's `.venv`
- Activates the virtual environment in the terminal
- Configures Python analysis paths correctly

**Location**: `{experiment_folder}/{experiment_name}.code-workspace`

### Root Workspace
The root workspace (`reproducibility.code-workspace`):
- Shows all experiments as folders
- Useful for browsing the entire repository
- **Note**: VS Code may prompt you to select a Python interpreter for each folder. For best results, use individual experiment workspaces.

## Adding a New Experiment Workspace

1. Create a `.venv` in your experiment folder
2. Create a workspace file: `{experiment_folder}/{experiment_name}.code-workspace`
3. Use this template:

```json
{
	"folders": [
		{
			"path": "."
		}
	],
	"settings": {
		"python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
		"python.terminal.activateEnvironment": true,
		"python.analysis.extraPaths": [
			"${workspaceFolder}"
		]
	},
	"extensions": {
		"recommendations": [
			"ms-python.python",
			"ms-python.vscode-pylance"
		]
	}
}
```

4. Update `open-workspace.sh` to include your new experiment

## Tips

- **For focused work**: Use individual experiment workspaces
- **For browsing**: Use the root workspace
- VS Code will remember which workspace you last opened
- You can pin workspaces in VS Code's File menu for quick access
