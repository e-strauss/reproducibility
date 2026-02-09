#!/bin/bash

# Ensure uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create venv and install dependencies in one command
# uv handles venv creation automatically if it doesn't exist
uv venv

# Install dependencies from requirements.txt
# Use --locked if you have a uv.lock file for exact reproducibility
if [ -f "uv.lock" ]; then
    uv pip install --locked
else
    uv pip install -r requirements.txt
fi

# Activate venv for subsequent commands
source .venv/bin/activate