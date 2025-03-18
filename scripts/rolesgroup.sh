#!/usr/bin/env bash

echo "🚀 Assigning roles to security group..."

output=$(azd env get-values)

while IFS= read -r line; do
  name=$(echo "$line" | cut -d '=' -f 1)
  value=$(echo "$line" | cut -d '=' -f 2 | sed 's/^\"//;s/\"$//')
  export "$name"="$value"
done <<< "$output"

echo "✅ Environment variables set!"

roles=(
    "ba92f5b4-2d11-453d-a403-e96b0029c9fe" # Storage Blob Data Contributor
    "5e0bd9bd-7b93-4f28-af87-19fc36ad61bd" # Cognitive Services OpenAI User
    "a001fd3d-188f-4b5d-821b-7da978bf7442" # Cognitive Services OpenAI Contributor
)

if [ -z "$AZURE_RESOURCE_GROUP" ]; then
    export AZURE_RESOURCE_GROUP="rg-$AZURE_ENV_NAME"
    azd env set AZURE_RESOURCE_GROUP "$AZURE_RESOURCE_GROUP"
fi

for role in "${roles[@]}"; do
    az role assignment create \
        --role "$role" \
        --assignee-object-id "$AZURE_GROUP_PRINCIPAL_ID" \
        --scope /subscriptions/"$AZURE_SUBSCRIPTION_ID"/resourceGroups/"$AZURE_RESOURCE_GROUP" \
        --assignee-principal-type Group
done

echo "✅ Roles assigned successfully!"
