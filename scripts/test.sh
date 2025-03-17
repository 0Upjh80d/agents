#!/usr/bin/env bash

# Exits immediately if any command returns a non-zero exit status
set -e

DIR="$( cd "$( dirname "$0" )/../tests" && pwd )"

echo "Running infrastructure integration tests..."
python -m pytest --rootdir="${DIR}" -v
