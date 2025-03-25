Write-Host "🚀 Configuring DVC remotes..."

# Perform operations in the root directory using a subshell
& {
    # Navigate to the root of the project
    $rootDir = git rev-parse --show-toplevel
    if (-not $?) { exit }

    # Define the config file path relative to the root
    $configFilePath = Join-Path -Path $rootDir -ChildPath ".dvc/config.local"

    # Attempt to remove the config file
    if (Test-Path -Path $configFilePath) {
        Write-Host "🗑️  Removing config.local..."
        Remove-Item -Path $configFilePath
    } else {
        Write-Host "🏳️ config.local not found. Continuing..."
    }
}


# Path to the .env file
$envFile = ".env"

# Fetch the SAS token by calling the Python script as an executable (see fetch_sas_token.py for more information)
python ./scripts/fetch_sas_token.py

# Read through the .env file and export each variable
Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()

    # Ignore empty lines and comments
    if ($line -eq "" -or $line.StartsWith("#")) {
        return
    }

    # Split the line into key and value, only split on the first occurrence of '='
    $parts = $line -split '=', 2
    # Trim any surrounding whitespace (useful for some environments)
    $key = $parts[0].Trim()
    $value = $parts[1].Trim()

    # Remove surrounding quotes from the value (if present)
    if ($value.StartsWith('"') -and $value.EndsWith('"')) {
        $value = $value.Substring(1, $value.Length - 2)
    }

    # Export the variable to the current session
    [System.Environment]::SetEnvironmentVariable($key, $value, [System.EnvironmentVariableTarget]::Process)
}

echo "✨ Environment variables set!"

# Define your remote names in an array
$remotes = @("vaccination_db", "get_instituitions_response")

foreach ($remote in $remotes) {
    Write-Host "⚙️  Configuring remote: $remote."

    # Add remote with base URL
    dvc remote add $remote "$env:AZURE_URL/$remote" --force

    # Add local configurations for credentials
    dvc remote modify --local $remote account_name $env:AZURE_STORAGE_ACCOUNT
    dvc remote modify --local $remote sas_token $env:AZURE_STORAGE_SAS_TOKEN
}

# Inform the user of completion
Write-Host "✅ All remotes configured successfully."
