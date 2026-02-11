#!/bin/bash
# Script to set up a new experiment workspace

set -e  # Exit on error

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if folder path is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <folder_path>"
    echo "Example: $0 stratum/uk-housing"
    exit 1
fi

FOLDER_PATH="$1"
FULL_PATH="$REPO_ROOT/$FOLDER_PATH"

# Extract experiment name (last part of the path)
EXPERIMENT_NAME=$(basename "$FOLDER_PATH")

# Create folder if it doesn't exist (including parent folders)
if [ ! -d "$FULL_PATH" ]; then
    echo "Creating folder: $FULL_PATH"
    mkdir -p "$FULL_PATH"
else
    echo "Folder already exists: $FULL_PATH"
fi

# Path to workspace file
WORKSPACE_FILE="$FULL_PATH/${EXPERIMENT_NAME}.code-workspace"

# Check if workspace file already exists
if [ -f "$WORKSPACE_FILE" ]; then
    echo "Warning: Workspace file already exists: $WORKSPACE_FILE"
    read -p "Overwrite? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# Create workspace file using template
echo "Creating workspace file: $WORKSPACE_FILE"

# Use template from root if it exists, otherwise use inline template
TEMPLATE_FILE="$REPO_ROOT/workspace-template.json"
if [ -f "$TEMPLATE_FILE" ]; then
    # Use template file
    cp "$TEMPLATE_FILE" "$WORKSPACE_FILE"
    echo "✓ Created workspace file from template"
else
    # Use inline template
    cat > "$WORKSPACE_FILE" << 'EOF'
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
EOF
    echo "✓ Created workspace file with default template"
fi

# Update reproducibility.code-workspace to include the new experiment
ROOT_WORKSPACE="$REPO_ROOT/reproducibility.code-workspace"
if [ -f "$ROOT_WORKSPACE" ]; then
    echo "Updating root workspace: $ROOT_WORKSPACE"
    
    # Use Python to update the JSON file
    python3 << EOF
import json
import sys

workspace_file = "$ROOT_WORKSPACE"
folder_path = "$FOLDER_PATH"
experiment_name = "$EXPERIMENT_NAME"

try:
    with open(workspace_file, 'r') as f:
        workspace = json.load(f)
    
    # Check if folder already exists
    folder_exists = False
    for folder in workspace.get('folders', []):
        if folder.get('path') == f"./{folder_path}":
            folder_exists = True
            break
    
    if not folder_exists:
        # Add new folder entry
        new_folder = {
            "name": f"🎯 {experiment_name.replace('_', ' ').title()}",
            "path": f"./{folder_path}"
        }
        workspace.setdefault('folders', []).append(new_folder)
        
        # Write back to file
        with open(workspace_file, 'w') as f:
            json.dump(workspace, f, indent='\t')
        
        print(f"✓ Added {folder_path} to root workspace")
    else:
        print(f"✓ Folder {folder_path} already exists in root workspace")
        
except Exception as e:
    print(f"Warning: Could not update root workspace: {e}", file=sys.stderr)
    sys.exit(0)  # Don't fail the script if this fails
EOF
else
    echo "Warning: Root workspace file not found: $ROOT_WORKSPACE"
fi

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Set up your experiment (usually via ./run.sh in the experiment folder)"
echo "  2. Open the workspace: code $WORKSPACE_FILE"
