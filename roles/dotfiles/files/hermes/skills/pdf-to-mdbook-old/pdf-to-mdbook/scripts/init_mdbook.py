#!/usr/bin/env python3
"""
init_mdbook.py — Initialize an mdBook from assembled chapters.

Writes book.toml with sensible defaults, copies chapter Markdown files
into src/, places SUMMARY.md correctly. After running, the directory
is ready for `mdbook build`.

Usage:
    python init_mdbook.py \\
        --title "Book Title" \\
        --author "Author Name" \\
        --chapters work/chapters \\
        --summary work/chapters/SUMMARY.md \\
        --out ./book-output
"""

import argparse
import shutil
import sys
import textwrap
from pathlib import Path


BOOK_TOML_TEMPLATE = """\
[book]
title = "{title}"
authors = [{authors}]
language = "{language}"
src = "src"

[build]
build-dir = "book"
create-missing = false

[output.html]
default-theme = "light"
preferred-dark-theme = "navy"
copy-fonts = true
mathjax-support = true
no-section-label = false

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
"""


def quote_authors(authors: list[str]) -> str:
    return ", ".join(f'"{a}"' for a in authors)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--title", required=True, help="Book title")
    ap.add_argument("--author", action="append", default=[],
                    help="Author name; pass multiple times for co-authors")
    ap.add_argument("--language", default="en",
                    help="Language code (default: en)")
    ap.add_argument("--chapters", required=True,
                    help="Directory of chapter Markdown files")
    ap.add_argument("--summary", required=True, help="Path to SUMMARY.md draft")
    ap.add_argument("--out", required=True, help="Output mdBook directory")
    ap.add_argument("--mathjax", action="store_true", default=True,
                    help="Enable MathJax (default: on)")
    ap.add_argument("--no-mathjax", dest="mathjax", action="store_false",
                    help="Disable MathJax")
    args = ap.parse_args()

    chapters_dir = Path(args.chapters)
    summary_path = Path(args.summary)
    out_dir = Path(args.out)

    if not chapters_dir.is_dir():
        print(f"ERROR: --chapters dir not found: {chapters_dir}", file=sys.stderr)
        sys.exit(1)
    if not summary_path.exists():
        print(f"ERROR: --summary not found: {summary_path}", file=sys.stderr)
        sys.exit(1)

    src_dir = out_dir / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    # Write book.toml
    authors = args.author or ["Unknown"]
    book_toml = BOOK_TOML_TEMPLATE.format(
        title=args.title.replace('"', '\\"'),
        authors=quote_authors(authors),
        language=args.language,
    )
    if not args.mathjax:
        book_toml = book_toml.replace("mathjax-support = true",
                                      "mathjax-support = false")
    (out_dir / "book.toml").write_text(book_toml)

    # Copy chapter files (everything except SUMMARY.md, which we'll place
    # explicitly)
    chapter_files = sorted(p for p in chapters_dir.glob("*.md")
                           if p.name != "SUMMARY.md")
    for f in chapter_files:
        shutil.copy(f, src_dir / f.name)

    # Copy any subdirectories of chapters/ (for nested structures or figures)
    for sub in chapters_dir.iterdir():
        if sub.is_dir():
            shutil.copytree(sub, src_dir / sub.name, dirs_exist_ok=True)

    # Place SUMMARY.md
    shutil.copy(summary_path, src_dir / "SUMMARY.md")

    print(f"Initialized mdBook at {out_dir}")
    print(f"  book.toml          → {out_dir / 'book.toml'}")
    print(f"  src/SUMMARY.md     → {src_dir / 'SUMMARY.md'}")
    print(f"  copied {len(chapter_files)} chapter file(s) into src/")
    print()
    print(textwrap.dedent(f"""\
        Next steps:
            cd {out_dir}
            mdbook build           # produces book/
            mdbook serve --open    # interactive preview

        If `mdbook` is not installed:
            cargo install mdbook
        Or download a binary release from:
            https://github.com/rust-lang/mdBook/releases
    """))


if __name__ == "__main__":
    main()
