#!/bin/bash
set -e

# Run cache detection to clean up freeze folders for changed posts
python3 scripts/quarto_post_cache.py

# Render Quarto blog
quarto render quarto_blog/

# Copy Quarto output to public directory
rm -rf public/quarto_blog
cp -r quarto_blog/_site public/quarto_blog
