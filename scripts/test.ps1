# Exit immediately if any command fails
$ErrorActionPreference = "Stop"

Write-Host "🚀 Running infrastructure integration tests..."

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$testDir = Resolve-Path "$scriptDir/../tests"

python -m pytest --rootdir="$testDir" -v

Write-Host "✅ Infrastructure integration tests passed!"
