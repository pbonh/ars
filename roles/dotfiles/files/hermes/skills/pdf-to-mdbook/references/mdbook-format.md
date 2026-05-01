# mdBook Format Reference

Quick reference for the files this skill produces.

## Anatomy of an mdBook

```
book-root/
├── book.toml          # Configuration
├── src/
│   ├── SUMMARY.md     # Table of contents (mandatory)
│   ├── README.md      # Intro / front matter (convention)
│   ├── chapter-1.md   # Content files
│   └── assets/
│       └── images/    # Static assets
└── book/              # Build output (created by mdbook build)
```

## `book.toml`

Minimal valid file:

```toml
[book]
title = "Book Title"
authors = ["Author Name"]
language = "en"
src = "src"

[build]
build-dir = "book"
```

Optional but recommended:

```toml
[preprocessor.index]
[preprocessor.links]
```

## `src/SUMMARY.md`

The summary **must** list every markdown file in `src/`. `mdbook` will create missing files if `create-missing = true` in `book.toml`. This skill sets `create-missing = false` to avoid accidental stubs.

### Syntax

```markdown
# Summary

[Introduction](README.md)

- [Chapter One](chapter-one.md)
- [Chapter Two](chapter-two.md)
    - [Subsection](chapter-two/section.md)

- [Appendix A](appendix-a.md)
```

### Rules for this skill

- Top-level items use `-` bullets.
- Nested items indent with 4 spaces.
- The link text becomes the chapter title in the rendered sidebar.
- Files not listed in `SUMMARY.md` are unreachable in the built book.
- Special sections:
  - `README.md` is conventionally the book's landing page.
  - `toc.md` can be listed if the original PDF had a printable table of contents.

### Naming conventions

- Chapter files: `NN-chapter-slug.md` (zero-padded two digits) or `chapter-slug.md`.
- Appendices: `appendix-a-slug.md`, `appendix-b-slug.md`, …
- Back matter: `bibliography.md`, `glossary.md`, `index.md`.
- Front matter: `preface.md`, `acknowledgments.md`, `toc.md`.

## Linking to assets

From any `src/*.md` file, reference images relatively:

```markdown
![Figure 1.1: Description](assets/images/chapter-01/fig-01.png)
```

The path is relative to the `src/` directory.

## Building and serving

```bash
mdbook build                    # Build to book/
mdbook serve --open             # Serve locally with auto-reload
mdbook test                     # Run doc-tests (Rust code blocks)
```
