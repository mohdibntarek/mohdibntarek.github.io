#!/bin/bash
set -e

# Script to reset cache for blog posts
# Usage: bun run reset-cache [post-name] [--delete-local-folders]

# Parse arguments
POST_NAME=""
DELETE_LOCAL_FOLDERS=""

for arg in "$@"; do
  case "$arg" in
    --delete-local-folders)
      DELETE_LOCAL_FOLDERS="--delete-local-folders"
      ;;
    *)
      if [ -z "$POST_NAME" ]; then
        POST_NAME="$arg"
      fi
      ;;
  esac
done

# Build the command
CMD="python3 scripts/quarto_post_cache.py --reset"

# Add post name if provided, otherwise empty (resets all)
if [ -n "$POST_NAME" ]; then
  CMD="$CMD \"$POST_NAME\""
else
  CMD="$CMD \"\""
fi

# Add delete-local-folders flag if requested
if [ -n "$DELETE_LOCAL_FOLDERS" ]; then
  CMD="$CMD --delete-local-folders"
fi

# Execute
eval $CMD