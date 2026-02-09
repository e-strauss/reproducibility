#!/bin/bash
# Helper script to open VS Code workspaces for experiments

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$1" = "root" ] || [ -z "$1" ]; then
    echo "Opening root workspace..."
    code "$REPO_ROOT/reproducibility.code-workspace"
elif [ "$1" = "scrabble" ] || [ "$1" = "scrabble_player_rating" ]; then
    echo "Opening scrabble_player_rating workspace..."
    code "$REPO_ROOT/stratum/scrabble_player_rating/scrabble_player_rating.code-workspace"
else
    echo "Usage: $0 [root|scrabble]"
    echo ""
    echo "Available workspaces:"
    echo "  root     - Open root reproducibility workspace (default)"
    echo "  scrabble - Open scrabble_player_rating experiment workspace"
    echo ""
    echo "Or open workspace files directly:"
    find "$REPO_ROOT" -name "*.code-workspace" -type f | sed 's|^|  |'
fi
