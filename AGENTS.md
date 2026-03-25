# Repository Guidelines

## Project Structure

```
src/
├── pages/           # Route definitions (.astro and .md files)
├── components/      # Reusable UI components
├── layouts/         # Layout wrappers
├── assets/          # Images and icons
└── styles/          # Shared CSS

public/              # Static files served at build time
public/pagefind/     # Generated search indexes (gitignored)
```

## Build Commands

```bash
bun install          # Install dependencies
bun dev              # Start dev server with hot reload
bun run build        # Production build + pagefind indexing
bun preview          # Preview production build locally
```

## Pagefind Search

This project uses [pagefind](https://pagefind.app/) for full-text search on the built site.

**How it works:**
- The build command (`bun run build`) runs `astro build`, then `bun pagefind --site dist/` to index the built HTML files, and copies the results to `public/pagefind/`.
- The `SearchBar.astro` component loads pagefind's CSS and JS from `/pagefind/` and initializes the search UI.

**Important notes:**
- Search is only available in production builds (`bun run build`) or preview mode (`bun preview`), not in dev mode.
- The `public/pagefind/` directory is gitignored but included in deployments via GitHub Actions.
- If search breaks after adding new pages, run `bun run build` to regenerate the indexes.

## Coding Style

- **Language**: TypeScript with ES modules (`"type": "module"`)
- **Indentation**: 2 spaces
- **Files**: PascalCase for components (`LeftSide.astro`), lowercase for pages
- **Styles**: CSS with oklch colors; no Tailwind
- **Components**: `.astro` files in `src/components/`; receive props via `Astro.props`

## Styles

### Color System

Colors are defined in `src/styles/typography.css` using CSS custom properties and oklch color space:

```css
:root {
  /* Backgrounds */
  --color-bg: oklch(97% 0.01 260);           /* Light background */
  --color-bg-dark: oklch(25% 0.035 265);     /* Dark sidebar/headers */
  
  /* Cards */
  --color-card: oklch(92% 0.025 255);        /* Card backgrounds */
  --color-card-border: oklch(85% 0.03 255);  /* Card borders */
  
  /* Text */
  --color-text: oklch(25% 0.03 260);         /* Primary text */
  --color-text-muted: oklch(50% 0.04 260);   /* Secondary text */
  --color-text-light: oklch(95% 0.01 260);   /* Text on dark backgrounds */
  
  /* Links */
  --color-link: oklch(50% 0.15 250);         /* Link color */
  --color-link-hover: oklch(40% 0.18 250);    /* Link hover */
}
```

### Typography

- **Font stack**: System fonts (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto`)
- **Monospace**: `var(--font-mono)` for code blocks
- **Headings**: 600 weight with slight negative letter-spacing

## Frontmatter Format

All markdown pages require:

```yaml
---
title: Page Title
description: Description
date: 'YYYY-MM-DD'
published: true
layout: ../layouts/Layout.astro
---
```

## Testing

No automated tests configured. Manual verification:

1. Run `bun dev` for development
2. Run `bun preview` after `bun run build` to verify output

## Git Conventions

**Commits**: Use conventional prefixes:
- `feat:` — New features or content
- `fix:` — Bug fixes
- `chore:` — Maintenance (deps, config)
- `docs:` — Documentation

**Pull requests**:
- Link related issues
- Include screenshots for visual changes
- Test locally before merging
- Ensure CI passes

## Deployment

Pushes to `main` trigger GitHub Actions (`withastro/action@v3`) to build and deploy to GitHub Pages at `https://mohdibntarek.github.io/`.
