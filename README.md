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

If your post uses Julia code, instantiate your environment before rendering:

```bash
cd quarto_blog/posts/<post-name>
julia --project=. -e 'using Pkg; Pkg.instantiate()'
```

Add dependencies as needed:
```bash
julia --project=. -e 'using Pkg; Pkg.add("Plots")'
```

**Note on TOML files:** Commit your TOML files (`Project.toml`, `CondaPkg.toml`, etc.) directly to git. They are used during rendering to ensure reproducible builds.

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
- When ready to publish, use `bun run publish` to freeze outputs

> **Note on CI Caching:** The `_freeze/` folder is not committed to git (it's in `.gitignore`), but it is cached on CI. This means once a post is frozen, it will only be executed once on CI. Subsequent builds will use the cached frozen outputs unless the source files change. To re-execute a frozen post on CI, you'll need to make a change to the post's source files.

---

### 4. Publish Your Post

When ready to publish, run:

```bash
bun run publish <post-name>
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