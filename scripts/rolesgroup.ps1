Write-Host "🚀 Assigning roles to security group..."

$output = azd env get-values

foreach ($line in $output) {
  $name, $value = $line.Split("=")
  $value = $value -replace '^\"|\"$'
  [Environment]::SetEnvironmentVariable($name, $value)
}

Write-Host "✅ Environment variables set!"

$roles = @(
    "ba92f5b4-2d11-453d-a403-e96b0029c9fe", # Storage Blob Data Contributor
    "5e0bd9bd-7b93-4f28-af87-19fc36ad61bd", # Cognitive Services OpenAI User
    "a001fd3d-188f-4b5d-821b-7da978bf7442" # Cognitive Services OpenAI Contributor
)

if ([string]::IsNullOrEmpty($env:AZURE_RESOURCE_GROUP)) {
    $env:AZURE_RESOURCE_GROUP = "rg-$env:AZURE_ENV_NAME"
    azd env set AZURE_RESOURCE_GROUP $env:AZURE_RESOURCE_GROUP
}

foreach ($role in $roles) {
    az role assignment create `
        --role $role `
        --assignee-object-id $env:AZURE_PRINCIPAL_ID `
        --scope /subscriptions/$env:AZURE_SUBSCRIPTION_ID/resourceGroups/$env:AZURE_RESOURCE_GROUP `
        --assignee-principal-type User
}

Write-Host "✅ Roles assigned successfully!"
