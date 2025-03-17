#!/usr/bin/env bash

echo "🚀 Pulling data..."

# Define parallel arrays for paths and their corresponding remotes
file_paths=("data/vaccination_db.sqlite.dvc")
remotes=("vaccination_db")

# Loop through each file and remote using indexed arrays
for i in "${!file_paths[@]}"; do
    file_path="${file_paths[$i]}"
    remote="${remotes[$i]}"
    echo "💪 Pulling $file_path from remote $remote..."
    dvc pull "$file_path" --remote "$remote"
done

echo "✅ All files pulled successfully."
