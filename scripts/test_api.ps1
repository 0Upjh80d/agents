# Exit if any command fails
$ErrorActionPreference = "Stop"

Write-Host "🚀 Running backend API unit tests..."

uv sync --group test

Set-Location app/backend/app

pytest tests -W ignore::DeprecationWarning -v

Write-Host "✅ Backend API unit tests passed!"
