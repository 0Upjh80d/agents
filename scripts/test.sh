#!/usr/bin/env bash

# Exits immediately if any command returns a non-zero exit status
set -e

echo "🚀 Running infrastructure integration tests..."

DIR="$( cd "$( dirname "$0" )/../tests" && pwd )"

python -m pytest --rootdir="${DIR}" -v

echo "✅ Infrastructure integration tests passed!"
