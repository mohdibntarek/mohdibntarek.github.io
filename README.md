# Personal Website

A personal website built with Astro and Quarto for the blog.

## Prerequisites

- [Bun](https://bun.sh/) - JavaScript runtime and package manager
- [Quarto](https://quarto.org/) - For rendering blog content
- [Julia](https://julialang.org/) (optional) - For running Julia code in blog posts

## Installation

```bash
bun install
```

---

## Writing and Publishing a Blog Post

### 1. Create a New Post

```bash
bun run new-post <post-name> [qmd|ipynb]
```

**Examples:**
```bash
# Create a .qmd post (default)
bun run new-post my-new-post

# Create a Jupyter notebook post
bun run new-post my-new-post ipynb
```

This creates a new post at `quarto_blog/posts/<post-name>/` with:
- `freeze: false` set in the qmd case for active development (so changes are picked up)
- An empty `Project.toml` for Julia dependencies
- Template content to get started

**Important:** `Project.toml` and `Manifest.toml` are gitignored by default (only `.before.toml` files are tracked). This is intentional - see the Publishing section below.

---

### 2. Set Up Your Environment (for Julia posts)

If your post uses Julia code, instantiate your environment before rendering:

```bash
cd quarto_blog/posts/<post-name>
julia --project=. -e 'using Pkg; Pkg.instantiate()'
```

Add dependencies as needed:
```bash
julia --project=. -e 'using Pkg; Pkg.add("Plots")'
```

---

### 3. Build Locally

```bash
# Build just the Quarto blog
bun run quarto

# Or build everything (includes search indexing)
bun run build
```

**Note:** Only the new post is unfrozen during development (`freeze: false`), so it'll re-render on each build.

---

### 4. Publish Your Post

When ready to publish, run:

```bash
bun run publish <post-name>
```

This prepares the post by:
1. Backing up your `.toml` files as `.before.toml` (these get committed)
2. Removing `freeze: false` so the document renders with frozen outputs

**Note on `.ipynb` files:** Jupyter notebooks are always frozen (Quarto never executes cells during rendering). Executing cells is the author's responsibility before publishing. For `.ipynb` posts, the TOML files are not used during site rendering, but they are still useful to keep around for:
- Future edits to your post
- Linking to for readers who want to reproduce your environment

**Why this workflow?** The `.before.toml` files are static and represent the state of the environment at the beginning of the post. The regular `.toml` files are dynamic and change as packages are added programmatically during the post—they are also gitignored. This allows the post to modify its environment without committing the full (potentially large) TOML files. When the site builds for deployment, the build script restores `.toml` files from these backups, allowing the CI to reproduce your initial environment and render the post.

**Important:** Before publishing, remove any packages that were added programmatically by your post (e.g., via `Pkg.add()` calls in the notebook). The publish script copies your current `.toml` files to `.before.toml`, so you want the initial state to be clean. The packages will be re-added when the post executes during the CI build. Keep only packages you manually added for development purposes that the post doesn't install itself.

After publishing, commit your changes:
```bash
git add quarto_blog/posts/<post-name>/
git commit -m "Publish post: my-new-post"
```

---

## Development Scripts

| Command | Description |
|---------|-------------|
| `bun run dev` | Start Astro development server |
| `bun run build` | Build the entire website (Quarto + Astro + search) |
| `bun run preview` | Preview the built website locally |
| `bun run quarto` | Render Quarto blog content only |

---

## Project Structure

```
├── src/                    # Astro source files
├── quarto_blog/            # Quarto blog content
│   ├── posts/              # Blog posts
│   ├── _quarto.yml         # Quarto configuration
│   └── styles/             # Custom CSS
├── public/                 # Static assets
├── scripts/                # Helper scripts
└── package.json            # Node dependencies
```

## Search

This website uses [Pagefind](https://pagefind.app/) for client-side search. The search index is automatically built during `bun run build`.