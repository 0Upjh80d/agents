#!/usr/bin/env bash

# Exits immediately if any command returns a non-zero exit status
set -e

echo "🚀 Running backend API unit tests..."

uv sync --group test --no-dev

cd app/backend/app

pytest tests -W ignore::DeprecationWarning -v

echo "✅ Backend API unit tests passed!"
