#!/usr/bin/env python3
"""
Custom cache system for Quarto blog posts.

This module provides functionality to:
1. Compute content hashes for each blog post folder
2. Detect changes in blog posts (including TOML files)
3. Clean up freeze folders for changed posts
4. Cache results that can be stored by GitHub Actions but gitignored

The cache file stores a mapping of post folder names to their content hashes.
If any file in a post folder changes, the hash changes and the freeze folder
should be deleted to force re-rendering.
"""

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


# Default paths
QUARTO_BLOG_DIR = Path("quarto_blog")
POSTS_DIR = QUARTO_BLOG_DIR / "posts"
FREEZE_DIR = QUARTO_BLOG_DIR / "_freeze"
CACHE_FILE = QUARTO_BLOG_DIR / ".post_cache.json"


def compute_file_hash(filepath: Path) -> str:
    """
    Compute MD5 hash of a file's contents.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Hexadecimal hash string
    """
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    except (IOError, OSError) as e:
        print(f"Warning: Could not read file {filepath}: {e}", file=sys.stderr)
        return ""
    return hash_md5.hexdigest()


def compute_post_hash(post_dir: Path) -> str:
    """
    Compute a combined hash of all files in a post directory.
    
    Files are sorted to ensure consistent hashing regardless of filesystem order.
    The hash includes both file paths and contents to detect:
    - File content changes
    - File additions/removals
    - File renames
    
    Excludes files in `.cache` and `.CondaPkg` directories as these are
    auto-generated folders that should not affect the cache key.
    
    Args:
        post_dir: Path to the post directory
        
    Returns:
        Hexadecimal hash string representing the entire post folder state
    """
    if not post_dir.exists():
        return ""
    
    # Directories to exclude from the hash
    excluded_dirs = {'.cache', '.CondaPkg'}
    
    # Collect all files recursively, excluding certain directories
    files: List[Path] = []
    for item in post_dir.rglob("*"):
        if item.is_file():
            # Get relative path parts to check for excluded directories
            rel_path = item.relative_to(post_dir)
            path_parts = rel_path.parts
            
            # Skip files in excluded directories
            if any(part in excluded_dirs for part in path_parts):
                continue
            
            # Store relative path from post_dir for consistency
            files.append(item)
    
    # Sort for consistent ordering
    files.sort()
    
    # Compute combined hash
    hasher = hashlib.md5()
    for file_path in files:
        # Include relative path in hash (to detect renames)
        rel_path = file_path.relative_to(post_dir).as_posix()
        hasher.update(rel_path.encode('utf-8'))
        
        # Include file content hash
        file_hash = compute_file_hash(file_path)
        hasher.update(file_hash.encode('utf-8'))
    
    return hasher.hexdigest()


def load_cache(cache_path: Path = CACHE_FILE) -> Dict[str, str]:
    """
    Load the post cache from disk.
    
    Args:
        cache_path: Path to the cache file
        
    Returns:
        Dictionary mapping post folder names to their hashes
    """
    if not cache_path.exists():
        return {}
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not load cache from {cache_path}: {e}", file=sys.stderr)
        return {}


def save_cache(cache: Dict[str, str], cache_path: Path = CACHE_FILE) -> None:
    """
    Save the post cache to disk.
    
    Args:
        cache: Dictionary mapping post folder names to their hashes
        cache_path: Path to the cache file
    """
    # Ensure parent directory exists
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, sort_keys=True)
    except IOError as e:
        print(f"Error: Could not save cache to {cache_path}: {e}", file=sys.stderr)
        raise


def get_all_posts(posts_dir: Path = POSTS_DIR) -> List[Path]:
    """
    Get all post directories.
    
    Args:
        posts_dir: Path to the posts directory
        
    Returns:
        List of paths to post directories
    """
    if not posts_dir.exists():
        return []
    
    posts = []
    for item in posts_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            posts.append(item)
    
    return sorted(posts)


def compute_current_state(posts_dir: Path = POSTS_DIR) -> Dict[str, str]:
    """
    Compute current hash state for all posts.
    
    Args:
        posts_dir: Path to the posts directory
        
    Returns:
        Dictionary mapping post folder names to their current hashes
    """
    current_state = {}
    for post_dir in get_all_posts(posts_dir):
        post_name = post_dir.name
        post_hash = compute_post_hash(post_dir)
        current_state[post_name] = post_hash
    
    return current_state


def detect_changed_posts(
    current_state: Dict[str, str],
    cached_state: Dict[str, str]
) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    Detect which posts have changed by comparing current and cached state.
    
    Args:
        current_state: Current hash state
        cached_state: Cached hash state
        
    Returns:
        Tuple of (changed_posts, new_posts, deleted_posts)
        - changed_posts: Posts that exist in both but have different hashes
        - new_posts: Posts that exist in current but not in cache
        - deleted_posts: Posts that exist in cache but not in current
    """
    current_names = set(current_state.keys())
    cached_names = set(cached_state.keys())
    
    # New posts: in current but not in cache
    new_posts = current_names - cached_names
    
    # Deleted posts: in cache but not in current
    deleted_posts = cached_names - current_names
    
    # Changed posts: in both but hashes differ
    common_posts = current_names & cached_names
    changed_posts = {
        name for name in common_posts 
        if current_state[name] != cached_state[name]
    }
    
    return changed_posts, new_posts, deleted_posts


def get_freeze_folder(post_name: str, freeze_dir: Path = FREEZE_DIR) -> Path:
    """
    Get the path to the freeze folder for a post.
    
    Args:
        post_name: Name of the post folder
        freeze_dir: Path to the _freeze directory
        
    Returns:
        Path to the freeze folder for this post
    """
    # Freeze folders are typically named after the post folder
    # and stored in _freeze/site/... or directly in _freeze
    # The structure is: _freeze/site/posts/<post_name>/...
    
    # Check common locations
    possible_paths = [
        freeze_dir / "site" / "posts" / post_name,
        freeze_dir / post_name,
        freeze_dir / "posts" / post_name,
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    # Return the most likely path even if it doesn't exist
    return freeze_dir / "site" / "posts" / post_name


def delete_freeze_folder(post_name: str, freeze_dir: Path = FREEZE_DIR) -> bool:
    """
    Delete the freeze folder for a post.
    
    Args:
        post_name: Name of the post folder
        freeze_dir: Path to the _freeze directory
        
    Returns:
        True if a freeze folder was found and deleted, False otherwise
    """
    import shutil
    
    freeze_folder = get_freeze_folder(post_name, freeze_dir)
    
    if freeze_folder.exists():
        try:
            shutil.rmtree(freeze_folder)
            print(f"Deleted freeze folder: {freeze_folder}")
            return True
        except (IOError, OSError) as e:
            print(f"Error: Could not delete freeze folder {freeze_folder}: {e}", file=sys.stderr)
            return False
    
    return False


def get_changed_posts(
    posts_dir: Path = POSTS_DIR,
    cache_path: Path = CACHE_FILE,
    auto_cleanup: bool = True
) -> List[str]:
    """
    Get list of posts that have changed since last cache update.
    
    This is the main function to call. It:
    1. Loads the cached state
    2. Computes current state
    3. Detects changes
    4. Optionally cleans up freeze folders for changed posts
    5. Updates the cache with current state
    
    Args:
        posts_dir: Path to the posts directory
        cache_path: Path to the cache file
        auto_cleanup: If True, delete freeze folders for changed posts
        
    Returns:
        List of post names that have changed (including new posts)
    """
    # Load cached state
    cached_state = load_cache(cache_path)
    
    # Compute current state
    current_state = compute_current_state(posts_dir)
    
    # Detect changes
    changed, new, deleted = detect_changed_posts(current_state, cached_state)
    
    # Combine changed and new posts
    all_changed = sorted(changed | new)
    
    # Clean up freeze folders if requested
    if auto_cleanup:
        for post_name in all_changed:
            delete_freeze_folder(post_name)
    
    # Update cache with current state
    save_cache(current_state, cache_path)
    
    # Report deleted posts
    if deleted:
        print(f"Note: {len(deleted)} post(s) were deleted since last cache: {deleted}")
    
    return all_changed


def main():
    """Command-line interface for the cache system."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Custom cache system for Quarto blog posts"
    )
    parser.add_argument(
        "--cache-file",
        type=Path,
        default=CACHE_FILE,
        help=f"Path to cache file (default: {CACHE_FILE})"
    )
    parser.add_argument(
        "--posts-dir",
        type=Path,
        default=POSTS_DIR,
        help=f"Path to posts directory (default: {POSTS_DIR})"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Don't delete freeze folders for changed posts"
    )
    parser.add_argument(
        "--show-cache",
        action="store_true",
        help="Show current cache contents and exit"
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear the cache and exit"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output changed posts as JSON"
    )
    parser.add_argument(
        "--reset",
        metavar="POST_NAME",
        nargs="?",
        const="ALL",
        help="Reset cache for a specific post, or all posts if no name provided"
    )
    parser.add_argument(
        "--delete-local-folders",
        action="store_true",
        help="Also delete .cache and .CondaPkg folders (default: off)"
    )
    
    args = parser.parse_args()
    
    def delete_local_folders(post_path: Path) -> None:
        """Delete .cache and .CondaPkg folders from a post directory."""
        for folder_name in ('.cache', '.CondaPkg'):
            folder = post_path / folder_name
            if folder.exists():
                try:
                    shutil.rmtree(folder)
                    print(f"  Deleted: {folder}")
                except OSError as e:
                    print(f"  Warning: Could not delete {folder}: {e}")
    
    # Fix: Empty string from shell script should be treated as "ALL"
    if args.reset == "":
        args.reset = "ALL"
    
    # Handle special commands
    if args.show_cache:
        cache = load_cache(args.cache_file)
        print(json.dumps(cache, indent=2))
        return 0
    
    if args.clear_cache:
        if args.cache_file.exists():
            args.cache_file.unlink()
            print(f"Cleared cache: {args.cache_file}")
        else:
            print(f"No cache file to clear: {args.cache_file}")
        return 0
    
    # Handle reset command
    if args.reset:
        cache = load_cache(args.cache_file)
        
        if args.reset == "ALL":
            print("Resetting cache for all posts...")
            
            # Process ALL post directories, not just cached ones
            all_posts = get_all_posts(Path(args.posts_dir))
            for post_dir in all_posts:
                post_name = post_dir.name
                print(f"\n  Processing: {post_name}")
                delete_freeze_folder(post_name, FREEZE_DIR)
                if args.delete_local_folders:
                    delete_local_folders(post_dir)
            
            # Clear cache
            if args.cache_file.exists():
                args.cache_file.unlink()
                print(f"\nCleared cache: {args.cache_file}")
            print("Cache reset complete for all posts.")
        else:
            post_name = args.reset
            print(f"Resetting cache for post: {post_name}")
            
            # Remove from cache
            if post_name in cache:
                del cache[post_name]
                save_cache(cache, args.cache_file)
                print(f"  Removed from cache")
            else:
                print(f"  Note: not found in cache")
            
            # Delete freeze folder
            delete_freeze_folder(post_name, FREEZE_DIR)
            if args.delete_local_folders:
                delete_local_folders(Path(args.posts_dir) / post_name)
            
            print(f"Cache reset complete for '{post_name}'.")
        return 0
    
    # Get changed posts
    changed_posts = get_changed_posts(
        posts_dir=args.posts_dir,
        cache_path=args.cache_file,
        auto_cleanup=not args.no_cleanup
    )
    
    # Output results
    if args.json:
        print(json.dumps({
            "changed_posts": changed_posts,
            "count": len(changed_posts)
        }))
    else:
        if changed_posts:
            print(f"Changed posts ({len(changed_posts)}):")
            for post in changed_posts:
                print(f"  - {post}")
        else:
            print("No posts changed.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())