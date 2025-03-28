#!/usr/bin/env bash

if ! command -v uv >/dev/null 2>&1; then
    echo "uv not installed. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

echo "Creaing python virtual environment..."
uv venv
source .venv/bin/activate

echo "Syncing dependencies..."
uv sync --no-dev

cd app/backend/app
uvicorn main:app --reload
