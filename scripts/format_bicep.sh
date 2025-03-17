#!/usr/bin/env bash

set -euo pipefail

echo "🧹 Formatting all Bicep files..."
# Use `find` to locate every *.bicep file recursively
find . -name '*.bicep' -print0 | while IFS= read -r -d '' file
do
  echo "Formatting $file"
  az bicep format -f "$file"
done

echo "✅ All Bicep files have been formatted!"
