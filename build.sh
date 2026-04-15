#!/bin/bash
set -e

# Install Julia dependencies
julia --project=quarto_blog -e 'using Pkg; Pkg.instantiate()'

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
