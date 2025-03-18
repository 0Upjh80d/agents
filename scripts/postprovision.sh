#!/usr/bin/env bash

# Exits immediately if any command returns a non-zero exit status
set -e

echo "🚀 Running postprovision.sh..."

./scripts/test.sh

./scripts/rolesgroup.sh
