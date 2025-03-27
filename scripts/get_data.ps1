Write-Host "🚀 Pulling data..."

# Define arrays for file paths and their corresponding remotes
$filePaths = @("data/vaccination_db.sqlite.dvc", "data/get_instituitions_response.json.dvc")
$remotes = @("vaccination_db", "get_instituitions_response")

# Loop through each file and remote using their indices
for ($i = 0; $i -lt $filePaths.Length; $i++) {
    $filePath = $filePaths[$i]
    $remote = $remotes[$i]
    Write-Host "Pulling $filePath from remote $remote..."
    & dvc pull $filePath --remote $remote
}

Write-Host "✅ All files pulled successfully."
