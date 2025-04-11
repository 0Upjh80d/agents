# Exit immediately if any command fails
$ErrorActionPreference = "Stop"

Write-Host "🚀 Running infrastructure integration tests..."

uv sync --group test --no-dev

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$testDir = Resolve-Path "$scriptDir/../tests"

python -m pytest -v "${DIR}"

Write-Host "✅ Infrastructure integration tests passed!"
