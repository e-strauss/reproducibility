#!/bin/bash

# Ensure uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create venv w/ python 3.12 and install dependencies in one command
# uv handles venv creation automatically if it doesn't exist
uv venv --python 3.12

# Install dependencies from requirements.txt
# Use uv.lock if available for exact reproducibility (created from current .venv)
if [ -f "uv.lock" ]; then
    uv pip install -r uv.lock
else
    uv pip install -r requirements.txt
fi

# Activate venv for subsequent commands
source .venv/bin/activate

# make data folder if it doesn't exist
mkdir -p data

# if the data folder is empty, download the data
if [ -z "$(ls -A data)" ]; then
    # Check if Kaggle credentials are present
    if [ ! -f "$HOME/.kaggle/kaggle.json" ]; then
        echo "Error: Kaggle credentials not found at ~/.kaggle/kaggle.json"
        echo "Please configure Kaggle CLI:"
        echo "1. Get your API credentials from https://www.kaggle.com/settings"
        echo "2. Create ~/.kaggle/kaggle.json with format: {\"username\":\"your_username\",\"key\":\"your_key\"}"
        echo "3. Set permissions: chmod 600 ~/.kaggle/kaggle.json"
        exit 1
    fi
    
    # Check if kaggle command is available
    if ! command -v kaggle &> /dev/null; then
        echo "Error: Kaggle CLI not found. Install it with: pip install kaggle"
        exit 1
    fi
    
    kaggle competitions download -c scrabble-player-rating
    unzip scrabble-player-rating.zip -d data/
    rm scrabble-player-rating.zip
else
    echo "Scrabble player data is already there"
fi

echo "Running sempipes optimization"
python optimize2.py