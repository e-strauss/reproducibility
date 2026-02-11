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
    kaggle competitions download -c scrabble-player-rating
    unzip scrabble-player-rating.zip -d data/
    rm scrabble-player-rating.zip
else
    echo "Scrabble player data is already there"
fi