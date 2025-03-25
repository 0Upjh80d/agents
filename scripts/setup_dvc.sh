#!/usr/bin/env bash

echo "🚀 Configuring DVC remotes..."

# Perform operations in the root directory using a subshell
(
    # Navigate to the root of the project
    cd "$(git rev-parse --show-toplevel)" || exit

    # Define the config file path relative to the root
    CONFIG_FILE_PATH=".dvc/config.local"

    # Attempt to remove the config file
    if [ -f "$CONFIG_FILE_PATH" ]; then
        echo "🗑️  Removing config.local..."
        rm "$CONFIG_FILE_PATH"
    else
        echo "🏳️ config.local not found. Continuing..."
    fi
)

# Path to the .env file
ENV_FILE=".env"

# Fetch the SAS token by calling the Python script as an executable (see fetch_sas_token.py for more information)
./scripts/fetch_sas_token.py

# Read through the .env file and export each variable
while IFS='=' read -r key value; do
    # Ignore empty lines and comments
    if [[ -z "$key" || "$key" == \#* ]]; then
        continue
    fi

    # Trim any surrounding whitespace (useful for some environments)
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)

    # Remove surrounding quotes from the value (if present)
    if [[ "$value" =~ ^\".*\"$ ]]; then
        value="${value:1:-1}"
    fi

    # Export the variable
    export "$key"="$value"

done < "$ENV_FILE"

echo "✨ Environment variables set!"

# Define your remote names in an array
remotes=("vaccination_db" "get_instituitions_response")

# Loop through each remote and execute the DVC commands
for remote in "${remotes[@]}"; do
    echo "⚙️  Configuring for remote: $remote."
    # Add remote with base URL
    dvc remote add "$remote" "$AZURE_URL/$remote" --force

    # Add local configurations for credentials
    dvc remote modify --local "$remote" account_name "$AZURE_STORAGE_ACCOUNT"
    dvc remote modify --local "$remote" sas_token "$AZURE_STORAGE_SAS_TOKEN"

done

# Inform the user of completion
echo "✅ All remotes configured successfully."
