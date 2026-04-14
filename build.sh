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
find dist/ -name '*.html' -exec sed -i '' \
  -e 's/class="sourceCode/data-pagefind-ignore class="sourceCode/g' \
  -e 's/class="btn code-tools-button"/data-pagefind-ignore class="btn code-tools-button"/g' \
  {} +

# Build Pagefind search index
bun pagefind --site dist/
cp -r dist/pagefind public/pagefind
