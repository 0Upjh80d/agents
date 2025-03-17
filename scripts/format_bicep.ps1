Set-StrictMode -Version Latest

Write-Host "🧹 Formatting all Bicep files..."

Get-ChildItem -Path . -Recurse -Filter *.bicep | ForEach-Object {
    Write-Host "Formatting $($_.FullName)"
    az bicep format -f "$($_.FullName)"
}

Write-Host "✅ All Bicep files have been formatted!"
