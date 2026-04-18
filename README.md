# Personal Website

A personal website built with Astro and Quarto for the blog.

## Prerequisites

- [Bun](https://bun.sh/) - JavaScript runtime and package manager
- [Quarto](https://quarto.org/) - For rendering blog content
- [Julia](https://julialang.org/) - For the Julia Quarto extension and running Julia code in blog posts
- [Python](https://python.org/) - For some build scripts and running Python code in blog posts (via CondaPkg)
- [R](https://www.r-project.org/) (optional) - For running R code in blog posts

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
- An empty `Project.toml` for Julia dependencies (delete if not using Julia)
- Template content to get started

**Note:** The `Project.toml` is created by default. If your post is text-only (no Julia code), delete the `Project.toml`. If using Python code with CondaPkg, you may need to create a `CondaPkg.toml` file.

---

### 2. Set Up Your Environment (for Julia/Python posts)

#### Julia Posts
If your post uses Julia packages, create both `Project.toml` and `Manifest.toml` files in your post directory. You can add dependencies as needed either external to the document or within the document while writing it.

Include a (hidden) cell in your post that calls `Pkg.instantiate()`:

```julia
using Pkg
Pkg.instantiate()
```

This will run when the document is built on CI and when others run your document. Link to the TOML files at the end of your post so others can reproduce your environment.

#### Python Posts
If your post uses Python packages via [CondaPkg](https://github.com/JuliaPy/CondaPkg.jl), create a `CondaPkg.toml` file in your post directory to specify Python dependencies.

#### Always Commit TOML Files
Once done writing, always commit your TOML files to git. They are used during rendering to ensure reproducible builds.

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
| `bun run astro` | Run Astro CLI commands |
| `bun run new-post <name> [format]` | Create a new blog post |
| `bun run publish-post <name>` | Publish a post (freeze outputs) |
| `bun run reset-cache [name]` | Clear cache for all posts or a specific post |

### Cache Management

The build system caches rendered post outputs to avoid unnecessary re-execution. To force re-rendering:

```bash
# Reset cache for all posts
bun run reset-cache

# Reset cache for a specific post
bun run reset-cache <post-name>

# Also delete local environment folders (.cache/, .CondaPkg/)
bun run reset-cache --delete-local-folders
bun run reset-cache <post-name> --delete-local-folders
```

By default, `reset-cache` only removes the `_freeze/` folder, which triggers re-execution on the next build. The `--delete-local-folders` option additionally removes the `.cache/` and `.CondaPkg/` folders that contain local development environments.

This is useful when:
- You want to force re-execution of a post on the next build
- The cache appears to be out of sync
- You want to completely reset a post's environment (with `--delete-local-folders`)

---

## Project Structure

```
├── src/                    # Astro source files
│   ├── components/         # Reusable Astro components
│   ├── layouts/            # Page layout templates
│   ├── pages/              # Website pages (.astro, .md)
│   ├── data/               # JSON data files (publications, teaching)
│   ├── styles/             # Custom CSS stylesheets
│   └── assets/             # Images and other assets
├── quarto_blog/            # Quarto blog content
│   ├── posts/              # Blog posts
│   ├── _quarto.yml         # Quarto configuration
│   ├── styles/             # Custom CSS
│   └── partials/           # HTML partial templates
├── public/                 # Static assets (PDFs, favicon, etc.)
│   └── pdfs/               # PDF publications
├── scripts/                # Helper scripts for building and publishing
├── .github/workflows/      # CI/CD workflows
└── package.json            # Bun dependencies
```

## Search

This website uses [Pagefind](https://pagefind.app/) for client-side search. The search index is automatically built during `bun run build`.