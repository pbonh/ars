# mdBook layout, config, and build

`init_mdbook.py` writes a working `book.toml` and `src/` tree with
sensible defaults. This file documents what it produces, how to adjust
it, and how to fix the build errors you'll most often hit.

## Directory layout

```
book-output/
├── book.toml         ← config
├── src/
│   ├── SUMMARY.md    ← table of contents (mdBook reads this first)
│   ├── chapter-1.md
│   ├── chapter-2.md
│   ├── nested/
│   │   ├── README.md
│   │   └── sub.md
│   └── figures/      ← images
└── book/             ← built HTML output (after `mdbook build`)
```

`mdbook build` runs in the `book-output/` directory (where `book.toml`
lives), reads from `src/`, writes HTML to `book/`.

## SUMMARY.md format (strict)

mdBook's parser is finicky. The format is:

```markdown
# Summary

[Foreword](foreword.md)

# Part I — Foundations

- [Chapter 1: Beginnings](chapter-1.md)
  - [The Before](chapter-1/before.md)
  - [The After](chapter-1/after.md)
- [Chapter 2: Patterns](chapter-2.md)

# Part II — Practice

- [Chapter 3: Examples](chapter-3.md)

---

[Glossary](glossary.md)
[Index](index.md)
```

Rules that trip up generators:

- **Prefix chapters** (front-matter, no number) — link with no list
  marker, before any `# Part` heading or numbered list.
- **Numbered chapters** — list items with `-` or `*` (don't mix in one
  document). Nesting is two-space indentation per level.
- **Part titles** — `# Heading` (level-1 ATX). Optional but useful for
  multi-section books. Once you start numbered chapters, you can't go
  back to prefix chapters in the same book.
- **Suffix chapters** — link with no list marker, after all numbered
  chapters and any `---` separator.
- **Draft chapters** — `[Title]()` with empty link target. Useful
  placeholders.

`assemble_chapters.py` produces a SUMMARY.md that follows these rules
exactly. If you edit by hand and the build complains, check
indentation (two-space, not four, not tab) and that you didn't mix
list markers.

## book.toml essentials

What `init_mdbook.py` writes by default:

```toml
[book]
title = "Book Title"
authors = ["Author Name"]
language = "en"
src = "src"

[build]
build-dir = "book"
create-missing = false

[output.html]
default-theme = "light"
preferred-dark-theme = "navy"
git-repository-url = ""
edit-url-template = ""
copy-fonts = true
mathjax-support = true
no-section-label = false
additional-css = []
additional-js = []

[output.html.search]
enable = true
limit-results = 30
use-boolean-and = true
boost-title = 2
boost-hierarchy = 1
boost-paragraph = 1
expand = true
heading-split-level = 3

[output.html.fold]
enable = true
level = 1

[output.html.print]
enable = true
```

**Common edits after init:**

- Change `language = "en"` for non-English books — affects search
  stemming and sidebar locale strings.
- Set `git-repository-url` if the book is in a repo — adds a "GitHub"
  link to the header.
- Set `edit-url-template` to enable per-page "Edit this page" links.
- Set `mathjax-support = false` if there's no math (slightly faster
  load).
- Add a custom theme by uncommenting `additional-css` and pointing it
  at a file in `theme/`.

## Building

```bash
cd book-output
mdbook build
```

Output appears under `book/`. Open `book/index.html` to view.

For interactive editing:

```bash
mdbook serve --open
```

This builds, opens the result in a browser, and rebuilds-and-reloads
on file changes. Best for the cleanup loop.

## Build errors and fixes

**`Error: Summary parsing failed`**: SUMMARY.md has a syntax error.
Most common: mixed `-` and `*` list markers, wrong indentation, or a
`# Part` heading after numbered chapters started without proper
suffix-chapter format. Re-run `init_mdbook.py` from a clean draft
SUMMARY.md if it gets too tangled.

**`Error: Couldn't find file "src/foo.md"`**: SUMMARY.md links to a
chapter file that wasn't written. Either the slug in your outline
doesn't match the filename produced by `assemble_chapters.py`, or you
edited SUMMARY.md by hand and made a typo. List the src directory and
compare:

```bash
ls book-output/src/*.md
grep -E '\.md\)' book-output/src/SUMMARY.md
```

**`Error: chapter "X" has invalid heading`**: A chapter file starts
with something mdBook can't parse as a heading. Make sure each
chapter starts with `# Title` on the first non-blank line.

**Build succeeds but search doesn't find anything**: Check that
`heading-split-level` is at least 2 — it controls how aggressively the
search index splits chapters. Higher number = more granular search
results.

**Math doesn't render**: Confirm `mathjax-support = true` is set under
`[output.html]`, then hard-refresh the browser (MathJax loads via
JavaScript and gets cached aggressively).

## Hosting the built book

The `book/` directory is plain static HTML. To publish:

- **GitHub Pages**: push to a `gh-pages` branch, or use the
  `peaceiris/actions-gh-pages` action with `book/` as the publish
  directory.
- **Netlify, Vercel, Cloudflare Pages**: set the build command to
  `mdbook build` and the publish directory to `book`.
- **Any web server**: copy `book/` to your webroot.

The HTML has no server-side dependencies — it's all static plus a
small client-side search index.

## Custom theming

mdBook supports custom themes by placing files under `theme/` next to
`book.toml`:

```
book-output/
├── book.toml
├── theme/
│   ├── index.hbs       ← layout template (Handlebars)
│   ├── highlight.css   ← syntax highlighting overrides
│   └── custom.css      ← referenced by additional-css in book.toml
└── src/
    └── ...
```

Run `mdbook init --theme` in an empty directory to get the default
theme as a starting point — copy whatever you want to override into
`theme/` and delete the rest. The full theming reference is at
<https://rust-lang.github.io/mdBook/format/theme/index.html>.

This skill doesn't bundle theme assets — that's a separate design
problem and a different skill's job.
