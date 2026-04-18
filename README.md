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
- An empty `Project.toml` for Julia dependencies
- Template content to get started

---

### 2. Set Up Your Environment (for Julia posts)

If your post is using Julia or Python packages, it should have either both `Project.toml` and `Manifest.toml` files in the case of Julia, or `CondaPkg.toml` file in the case of Python.

You can add dependencies as needed to these environments either external to the document or within the document while writing it.

Once done writing, always commit your TOML files to git. They are used during rendering to ensure reproducible builds.

If your post uses Julia code with a `Project.toml` file, you should include a (hidden) cell in your post that calls `Pkg.instantiate()`:

```julia
using Pkg
Pkg.instantiate()
```

This will run when the document is built on CI and when others are running your document. But for someone else to run your document, they need to have the TOML files on their end so it is a good idea to link to them at the end of your post.

---

### 3. Build Locally

```bash
# Build just the Quarto blog
bun run quarto

# Or build everything (includes search indexing)
bun run build
```

**Freeze Configuration:**
- The project default is `freeze: false` (set in `quarto_blog/_quarto.yml`)
- This means posts re-execute on each build during development
- When ready to publish, use `bun run publish-post` to freeze outputs

> **Note on CI Caching:** The `_freeze/` folder is not committed to git (it's in `.gitignore`), but it is cached on CI. This means once a post is frozen, it will only be executed once on CI. Subsequent builds will use the cached frozen outputs unless the source files change. To re-execute a frozen post on CI, you'll need to make a change to the post's source files.

---

### 4. Publish Your Post

When ready to publish, run:

```bash
bun run publish-post <post-name>
```

This prepares the post by setting `freeze: true` in the post, so the outputs are frozen and won't re-execute on CI builds.

**Note on `.ipynb` files:** Jupyter notebooks are always frozen (Quarto never executes cells during rendering). Executing cells is the author's responsibility before publishing. For `.ipynb` posts, the TOML files are not used during site rendering, but they are still useful to keep around for:
- Future edits to your post
- Linking to for readers who want to reproduce your environment

**After publishing, commit your changes:**
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
| `bun run reset-cache` | Clear cache for all posts (or specific post) |

### Cache Management

The build system caches rendered post outputs to avoid unnecessary re-execution. To force re-rendering:

```bash
# Reset cache for all posts
bun run reset-cache

# Reset cache for a specific post
bun run reset-cache <post-name>
```

This is useful when:
- You want to force re-execution of a post on the next build
- The cache appears to be out of sync

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