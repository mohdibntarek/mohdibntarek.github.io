#!/bin/bash
set -e

# Script to prepare quarto_blog for publishing
# 1. Copies any .toml files (except before.toml) to their corresponding before.toml files
# 2. Removes freeze: false from .qmd files
#
# Usage: ./scripts/publish.sh <post-name>
# Example: ./scripts/publish.sh 6-my-new-post

POST_NAME=$1

# Require post name argument
if [ -z "$POST_NAME" ]; then
    echo "Error: Post name is required"
    echo "Usage: ./scripts/publish.sh <post-name>"
    echo "Example: ./scripts/publish.sh 6-my-new-post"
    exit 1
fi

# Find the post directory in quarto_blog/posts/
POST_DIR="quarto_blog/posts/${POST_NAME}"

if [ ! -d "$POST_DIR" ]; then
    echo "Error: Post '$POST_NAME' not found in quarto_blog/posts/"
    echo "Looking for: $POST_DIR"
    exit 1
fi

echo "Preparing quarto_blog for publishing..."
echo "Publishing post: $POST_NAME"

echo ""
echo "Processing .toml files..."

# Find all .toml files in the post directory (excluding before.toml files)
find "$POST_DIR" -maxdepth 1 -type f -name "*.toml" ! -name "*.before.toml" | while read -r toml_file; do
    # Get the directory containing the toml file
    dir=$(dirname "$toml_file")
    # Get the filename without extension
    filename=$(basename "$toml_file" .toml)
    # Construct the before.toml path
    before_file="${dir}/${filename}.before.toml"
    
    echo "Copying $toml_file -> $before_file"
    cp "$toml_file" "$before_file"
done

echo ""
echo "Removing freeze: false from post files..."

# Process .qmd files only (skip pre-rendered .ipynb files)
find "$POST_DIR" -maxdepth 1 -type f -name "*.qmd" | while read -r qmd_file; do
    if grep -qE "^[[:space:]]+freeze: false" "$qmd_file"; then
        echo "Processing $qmd_file"
        # Remove the freeze: false line (with indentation)
        sed -i '/^[[:space:]]*freeze: false/d' "$qmd_file"
    fi
done

echo ""
echo "Publish preparation complete!"