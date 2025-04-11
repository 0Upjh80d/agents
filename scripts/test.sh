#!/usr/bin/env bash

# Exits immediately if any command returns a non-zero exit status
set -e

echo "🚀 Running infrastructure integration tests..."

uv sync --group test --no-dev

DIR="$( cd "$( dirname "$0" )/../tests" && pwd )"

python -m pytest -v "${DIR}"

echo "✅ Infrastructure integration tests passed!"
