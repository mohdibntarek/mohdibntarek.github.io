#!/bin/bash
set -e

# Find all *.before.toml files and copy them to *.toml files
# Only copy if the target .toml file doesn't already exist
find . -name "*.before.toml" -type f | while read -r before_file; do
    # Get the target filename by removing .before before .toml
    target_file="${before_file%.before.toml}.toml"
    
    if [ ! -f "$target_file" ]; then
        echo "Copying $before_file -> $target_file"
        cp "$before_file" "$target_file"
    else
        echo "Skipping $target_file (already exists)"
    fi
done

# Render Quarto blog
quarto render quarto_blog/

# Copy Quarto output to public directory
rm -rf public/quarto_blog
cp -r quarto_blog/_site public/quarto_blog

# Build Astro site
astro build

# Add data-pagefind-ignore to code blocks and code-tools button
# Copy data-anchor-id to id on Quarto headings for Pagefind section indexing
find dist/ -name '*.html' -exec sed -i.bak \
  -e 's/class="sourceCode/data-pagefind-ignore class="sourceCode/g' \
  -e 's/class="btn code-tools-button"/data-pagefind-ignore class="btn code-tools-button"/g' \
  -e 's/class="anchored" data-anchor-id="\([^"]*\)"/class="anchored" data-anchor-id="\1" id="\1"/g' \
  {} +
find dist/ -name '*.bak' -delete

# Build Pagefind search index
bun pagefind --site dist/

rm -rf public/pagefind
cp -r dist/pagefind public/pagefind
