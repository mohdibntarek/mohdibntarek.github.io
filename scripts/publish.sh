#!/bin/bash
set -e

# Script to prepare quarto_blog for publishing
# Sets freeze: true in .qmd files
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
echo "Setting freeze: true in post files..."

# Process .qmd files only (skip pre-rendered .ipynb files)
find "$POST_DIR" -maxdepth 1 -type f -name "*.qmd" | while read -r qmd_file; do
    echo "Processing $qmd_file"
    
    # First remove any existing freeze: false
    sed -i '/^[[:space:]]*freeze: false/d' "$qmd_file"
    
    if grep -q "^execute:" "$qmd_file"; then
        # Add freeze: true under existing execute: section
        # Check if freeze: true already exists
        if ! grep -q "^execute:" "$qmd_file" | grep -q "freeze: true"; then
            # Check if freeze: true is already under execute:
            if ! sed -n '/^execute:/,/^\(---\|$\)/p' "$qmd_file" | grep -q "freeze: true"; then
                sed -i '/^execute:/a\  freeze: true' "$qmd_file"
                echo "  Added freeze: true to existing execute: section"
            else
                echo "  freeze: true already exists"
            fi
        fi
    else
        # Add execute: section with freeze: true after the YAML frontmatter
        # Find the end of the first YAML block (---) and insert execute: section after it
        awk '
        BEGIN { in_yaml = 0; yaml_started = 0; lines[0] = ""; count = 0 }
        /^---$/ {
            if (!yaml_started) {
                yaml_started = 1
                in_yaml = 1
                print "---"
            } else if (in_yaml) {
                in_yaml = 0
                # Print accumulated lines
                for (i = 0; i < count; i++) print lines[i]
                # Insert execute: section
                print "execute:"
                print "  freeze: true"
                # Print closing ---
                print "---"
                count = 0
            }
            next
        }
        { 
            if (yaml_started && in_yaml) {
                lines[count++] = $0
            } else {
                print
            }
        }
        END {
            if (count > 0) {
                for (i = 0; i < count; i++) print lines[i]
            }
        }
        ' "$qmd_file" > "$qmd_file.tmp" && mv "$qmd_file.tmp" "$qmd_file"
        echo "  Created execute: section with freeze: true"
    fi
done

echo ""
echo "Publish preparation complete!"