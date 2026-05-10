#!/usr/bin/env python3
"""
triage_fragments.py — Plan a wiki-merge run.

Walks <wiki_root>/wiki/.fragments/ and emits one JSON record per merge unit
to stdout as JSONL. The wiki-merge skill consumes this and acts on each
record in order.

Record shapes (one per stdout line):

  Concept merge:
    {"kind": "concept",
     "slug": "two-graph-method",
     "fragment_paths": ["wiki/.fragments/concepts/two-graph-method/<file>.md", ...],
     "canonical_path": "wiki/concepts/two-graph-method.md",
     "canonical_exists": true|false,
     "fragment_count": N}

  Entity merge:
    {"kind": "entity", ... same fields, with "canonical_path": "wiki/entities/<slug>.md"}

  Log batch:
    {"kind": "log",
     "fragment_paths": [...sorted by filename = chronological order],
     "fragment_count": N}

  Index deltas:
    {"kind": "index",
     "delta_paths": [...sorted by filename],
     "delta_count": N}

Output ordering:
  All concept records first (sorted by slug), then all entity records
  (sorted by slug), then exactly one log record (omitted if no log
  fragments), then exactly one index record (omitted if no deltas).

Errors and progress notes go to stderr. Stdout is parser-clean JSONL.

Usage:
    python triage_fragments.py <wiki_root>             # plan
    python triage_fragments.py <wiki_root> --summary   # print counts to stderr too
    python triage_fragments.py <wiki_root> --kind concept  # only one kind

Exit codes:
    0  success (even if no fragments — empty stdout is valid)
    2  invalid arguments / wiki layout missing
"""

import argparse
import json
import os
import sys
from pathlib import Path

FRAGMENTS_SUBDIR = "wiki/.fragments"
CANONICAL_CONCEPTS = "wiki/concepts"
CANONICAL_ENTITIES = "wiki/entities"


def fatal(msg: str, code: int = 2):
    print(f"triage_fragments: {msg}", file=sys.stderr)
    sys.exit(code)


def warn(msg: str) -> None:
    print(f"triage_fragments: {msg}", file=sys.stderr)


def emit(rec: dict) -> None:
    sys.stdout.write(json.dumps(rec, sort_keys=True) + "\n")


def list_slug_dirs(parent: Path) -> list[Path]:
    """Subdirectories of parent that aren't dotfiles, sorted by name."""
    if not parent.is_dir():
        return []
    out = []
    for child in parent.iterdir():
        if child.name.startswith("."):
            continue
        if child.is_dir():
            out.append(child)
    return sorted(out, key=lambda p: p.name)


def list_fragment_files(slug_dir: Path) -> list[Path]:
    """Markdown fragment files inside one slug dir, sorted by filename."""
    out = []
    for child in slug_dir.iterdir():
        if child.is_file() and child.suffix == ".md" and not child.name.startswith("."):
            out.append(child)
    return sorted(out, key=lambda p: p.name)


def rel(p: Path, wiki_root: Path) -> str:
    return os.path.relpath(p, wiki_root)


def plan_concepts_or_entities(
    wiki_root: Path, kind: str, fragments_dir: Path, canonical_dir: Path
) -> int:
    """Returns count of merge records emitted for this kind."""
    n = 0
    for slug_dir in list_slug_dirs(fragments_dir):
        slug = slug_dir.name
        files = list_fragment_files(slug_dir)
        if not files:
            continue
        canonical = canonical_dir / f"{slug}.md"
        emit(
            {
                "kind": kind,
                "slug": slug,
                "fragment_paths": [rel(f, wiki_root) for f in files],
                "canonical_path": rel(canonical, wiki_root),
                "canonical_exists": canonical.is_file(),
                "fragment_count": len(files),
            }
        )
        n += 1
    return n


def plan_log(wiki_root: Path, log_dir: Path) -> int:
    if not log_dir.is_dir():
        return 0
    files = []
    for child in log_dir.iterdir():
        if child.is_file() and child.suffix == ".md" and not child.name.startswith("."):
            files.append(child)
    if not files:
        return 0
    files.sort(key=lambda p: p.name)
    emit(
        {
            "kind": "log",
            "fragment_paths": [rel(f, wiki_root) for f in files],
            "fragment_count": len(files),
        }
    )
    return 1


def plan_index(wiki_root: Path, index_dir: Path) -> int:
    if not index_dir.is_dir():
        return 0
    files = []
    for child in index_dir.iterdir():
        if child.is_file() and child.suffix == ".json" and not child.name.startswith("."):
            files.append(child)
    if not files:
        return 0
    files.sort(key=lambda p: p.name)
    emit(
        {
            "kind": "index",
            "delta_paths": [rel(f, wiki_root) for f in files],
            "delta_count": len(files),
        }
    )
    return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Plan a wiki-merge run")
    ap.add_argument("wiki_root", help="absolute path to the wiki root (parent of wiki/)")
    ap.add_argument(
        "--kind",
        choices=["concept", "entity", "log", "index", "all"],
        default="all",
        help="restrict planning to one kind (default: all)",
    )
    ap.add_argument(
        "--summary",
        action="store_true",
        help="also print aggregate counts to stderr",
    )
    args = ap.parse_args(argv)

    wiki_root = Path(args.wiki_root).resolve()
    if not wiki_root.is_dir():
        fatal(f"wiki_root not a directory: {wiki_root}")

    fragments_root = wiki_root / FRAGMENTS_SUBDIR
    if not fragments_root.is_dir():
        # Empty plan is valid output. Bootstrap may not have created it yet.
        if args.summary:
            warn(f"no {FRAGMENTS_SUBDIR}/ — emitting empty plan")
        return 0

    n_concepts = n_entities = n_log = n_index = 0

    if args.kind in ("concept", "all"):
        n_concepts = plan_concepts_or_entities(
            wiki_root,
            "concept",
            fragments_root / "concepts",
            wiki_root / CANONICAL_CONCEPTS,
        )
    if args.kind in ("entity", "all"):
        n_entities = plan_concepts_or_entities(
            wiki_root,
            "entity",
            fragments_root / "entities",
            wiki_root / CANONICAL_ENTITIES,
        )
    if args.kind in ("log", "all"):
        n_log = plan_log(wiki_root, fragments_root / "log")
    if args.kind in ("index", "all"):
        n_index = plan_index(wiki_root, fragments_root / "index")

    if args.summary:
        warn(
            f"plan: {n_concepts} concept(s), {n_entities} entity(s), "
            f"{n_log} log batch, {n_index} index batch"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
