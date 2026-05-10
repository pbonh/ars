#!/usr/bin/env python3
"""
archive_fragments.py — Move consumed fragments from wiki/.fragments/<kind>/...
to wiki/.fragments/.merged/<kind>/... after a successful merge step.

Idempotent: if the destination already exists, the source is unlinked
(the destination is from a prior merge of the same fragment after a
re-ingest; we keep the older archive copy by default — pass --overwrite
to replace it).

Usage:
    python archive_fragments.py <wiki_root> --paths PATH [PATH ...]
    python archive_fragments.py <wiki_root> --stdin   # newline-separated paths on stdin
    python archive_fragments.py <wiki_root> --paths PATH ... --overwrite

Paths must be wiki-root-relative (matching what triage_fragments.py emits)
and must live under wiki/.fragments/. Anything else is rejected.

Exit codes:
    0  success (all paths archived or already archived)
    1  partial failure (some moves failed — details on stderr)
    2  invalid arguments
"""

import argparse
import os
import sys
from pathlib import Path

FRAGMENTS_PREFIX = "wiki/.fragments/"
ARCHIVE_PREFIX = "wiki/.fragments/.merged/"


def fatal(msg: str, code: int = 2):
    print(f"archive_fragments: {msg}", file=sys.stderr)
    sys.exit(code)


def warn(msg: str) -> None:
    print(f"archive_fragments: {msg}", file=sys.stderr)


def archive_one(wiki_root: Path, rel_path: str, overwrite: bool) -> bool:
    """Returns True on success, False on failure."""
    if not rel_path.startswith(FRAGMENTS_PREFIX):
        warn(f"reject (not under {FRAGMENTS_PREFIX}): {rel_path}")
        return False
    if rel_path.startswith(ARCHIVE_PREFIX):
        warn(f"already archived: {rel_path}")
        return True
    src = wiki_root / rel_path
    if not src.is_file():
        # If a prior partial run already moved it, that's success-equivalent.
        relative_inside = rel_path[len(FRAGMENTS_PREFIX) :]
        already_dest = wiki_root / ARCHIVE_PREFIX / relative_inside
        if already_dest.is_file():
            return True
        warn(f"missing source (skipping): {rel_path}")
        return False
    relative_inside = rel_path[len(FRAGMENTS_PREFIX) :]
    dst = wiki_root / ARCHIVE_PREFIX / relative_inside
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not overwrite:
        # Keep the older archive; just remove the source.
        try:
            src.unlink()
            return True
        except OSError as e:
            warn(f"failed to remove source after seeing existing archive: {rel_path}: {e}")
            return False
    try:
        os.replace(src, dst)  # atomic within same filesystem
        return True
    except OSError as e:
        warn(f"move failed: {rel_path} → {dst}: {e}")
        return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Archive consumed fragments after merge")
    ap.add_argument("wiki_root")
    ap.add_argument("--paths", nargs="*", default=[])
    ap.add_argument("--stdin", action="store_true", help="read newline-separated paths from stdin")
    ap.add_argument("--overwrite", action="store_true", help="replace existing archive entries")
    args = ap.parse_args(argv)

    wiki_root = Path(args.wiki_root).resolve()
    if not wiki_root.is_dir():
        fatal(f"wiki_root not a directory: {wiki_root}")

    paths: list[str] = list(args.paths)
    if args.stdin:
        for line in sys.stdin:
            line = line.strip()
            if line:
                paths.append(line)
    if not paths:
        warn("no paths given; nothing to do")
        return 0

    failures = 0
    for p in paths:
        if not archive_one(wiki_root, p, args.overwrite):
            failures += 1

    if failures:
        warn(f"{failures} of {len(paths)} path(s) failed")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
