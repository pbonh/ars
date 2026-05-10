#!/usr/bin/env python3
"""
rebuild_index.py — Regenerate the Statistics + Concepts/Entities/Summaries
tables in <wiki_root>/wiki/index.md from a filesystem scan of
wiki/concepts/, wiki/entities/, wiki/summaries/, and the YAML frontmatter
of those pages.

Idempotent. Atomic write via tmp + os.replace. Other sections of
index.md (front matter, headings, hand-written prose) are preserved.

Behavior:
  - The Concepts table is replaced between its `## Concepts` header and the
    next `## ` heading. Same for Entities and Summaries.
  - The Statistics section is replaced between its `## Statistics` header
    and the next `## ` heading (or EOF).
  - If index.md doesn't exist, a minimal one is created.
  - Pages are sorted alphabetically by filename slug.
  - Pages with malformed/missing frontmatter still get listed; missing
    fields render as empty cells.

Usage:
    python rebuild_index.py <wiki_root>            # rewrite wiki/index.md
    python rebuild_index.py <wiki_root> --dry-run  # print to stdout instead

Exit codes:
    0 success
    2 invalid arguments / wiki layout missing
"""

import argparse
import os
import re
import sys
from pathlib import Path

WIKI_SUBDIR = "wiki"
INDEX_REL = "wiki/index.md"
DIRS = {
    "concept": "wiki/concepts",
    "entity": "wiki/entities",
    "summary": "wiki/summaries",
}

# ---------- frontmatter parser (no external deps) ----------

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    """Tiny YAML-ish frontmatter parser. Handles only what wiki pages use:
    scalars, simple inline lists [a, b, c], and basic quoted strings.
    """
    m = _FM_RE.match(text)
    if not m:
        return {}
    body = m.group(1)
    out: dict = {}
    for line in body.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        k = k.strip()
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1].strip()
            items = [item.strip().strip('"').strip("'") for item in inner.split(",") if item.strip()]
            out[k] = items
        elif (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            out[k] = v[1:-1]
        else:
            out[k] = v
    return out


def _scan(dir_path: Path) -> list[dict]:
    """Return list of {slug, title, tags, confidence, updated, sources} for each .md page."""
    if not dir_path.is_dir():
        return []
    out = []
    for child in sorted(dir_path.iterdir(), key=lambda p: p.name):
        if not child.is_file() or child.suffix != ".md" or child.name.startswith("."):
            continue
        slug = child.stem
        try:
            text = child.read_text()
        except OSError:
            text = ""
        fm = parse_frontmatter(text)
        out.append(
            {
                "slug": slug,
                "title": fm.get("title", slug),
                "tags": fm.get("tags", []) or [],
                "confidence": fm.get("confidence", ""),
                "updated": fm.get("updated", ""),
                "sources": fm.get("sources", []) or [],
            }
        )
    return out


def render_concepts_table(rows: list[dict]) -> str:
    out = ["## Concepts", "", "| Page | Tags | Confidence | Updated |", "|------|------|------------|---------|"]
    for r in rows:
        tags = ", ".join(r["tags"]) if isinstance(r["tags"], list) else str(r["tags"])
        out.append(f"| [[concepts/{r['slug']}]] | {tags} | {r['confidence']} | {r['updated']} |")
    if not rows:
        out.append("| <!-- no concept pages yet --> | | | |")
    return "\n".join(out) + "\n"


def render_entities_table(rows: list[dict]) -> str:
    out = ["## Entities", "", "| Page | Tags | Updated |", "|------|------|---------|"]
    for r in rows:
        tags = ", ".join(r["tags"]) if isinstance(r["tags"], list) else str(r["tags"])
        out.append(f"| [[entities/{r['slug']}]] | {tags} | {r['updated']} |")
    if not rows:
        out.append("| <!-- no entity pages yet --> | | |")
    return "\n".join(out) + "\n"


def render_summaries_table(rows: list[dict]) -> str:
    out = ["## Summaries", "", "| Page | Source | Created | Updated |", "|------|--------|---------|---------|"]
    for r in rows:
        sources = "; ".join(r["sources"]) if isinstance(r["sources"], list) else str(r["sources"])
        out.append(f"| [[summaries/{r['slug']}]] | {sources} | | {r['updated']} |")
    if not rows:
        out.append("| <!-- no summary pages yet --> | | | |")
    return "\n".join(out) + "\n"


def render_statistics(rows_by_kind: dict[str, list[dict]]) -> str:
    n_concepts = len(rows_by_kind["concept"])
    n_entities = len(rows_by_kind["entity"])
    n_summaries = len(rows_by_kind["summary"])
    n_total = n_concepts + n_entities + n_summaries
    conf = {"high": 0, "medium": 0, "low": 0}
    for kind in ("concept", "entity"):
        for r in rows_by_kind[kind]:
            c = (r.get("confidence") or "").lower()
            if c in conf:
                conf[c] += 1
    out = [
        "## Statistics",
        "",
        f"- **Total pages**: {n_total}",
        f"- **Concepts**: {n_concepts}",
        f"- **Entities**: {n_entities}",
        f"- **Summaries**: {n_summaries}",
        f"- **Sources ingested**: {n_summaries}",
        f"- **High confidence**: {conf['high']}",
        f"- **Medium confidence**: {conf['medium']}",
        f"- **Low confidence**: {conf['low']}",
    ]
    return "\n".join(out) + "\n"


_SECTION_RE_FMT = r"(^##\s+{name}\b[^\n]*\n)(.*?)(?=^##\s+|\Z)"


def replace_section(text: str, name: str, new_block: str) -> str:
    """Replace a `## name` section (header + body up to next ##/EOF) with new_block.
    new_block must include its own `## name` header line. If section absent, append.
    """
    pat = re.compile(_SECTION_RE_FMT.format(name=re.escape(name)), re.DOTALL | re.MULTILINE)
    if pat.search(text):
        return pat.sub(lambda m: new_block + ("\n" if not new_block.endswith("\n") else ""), text)
    sep = "\n" if text.endswith("\n") else "\n\n"
    return text + sep + new_block + ("\n" if not new_block.endswith("\n") else "")


MINIMAL_INDEX = """---
title: "Knowledge Base Index"
type: index
---

# Knowledge Base Index

Master catalog of all wiki pages. Maintained by `wiki-merge`.

## Concepts

## Entities

## Summaries

## Syntheses

| Page | Pages Compared | Created |
|------|----------------|---------|

## Statistics
"""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Rebuild wiki/index.md from filesystem")
    ap.add_argument("wiki_root")
    ap.add_argument("--dry-run", action="store_true", help="print to stdout instead of writing")
    args = ap.parse_args(argv)

    wiki_root = Path(args.wiki_root).resolve()
    if not (wiki_root / WIKI_SUBDIR).is_dir():
        print(f"rebuild_index: not a wiki root (no wiki/): {wiki_root}", file=sys.stderr)
        return 2

    rows_by_kind = {kind: _scan(wiki_root / sub) for kind, sub in DIRS.items()}

    index_path = wiki_root / INDEX_REL
    text = index_path.read_text() if index_path.is_file() else MINIMAL_INDEX

    text = replace_section(text, "Concepts", render_concepts_table(rows_by_kind["concept"]))
    text = replace_section(text, "Entities", render_entities_table(rows_by_kind["entity"]))
    text = replace_section(text, "Summaries", render_summaries_table(rows_by_kind["summary"]))
    text = replace_section(text, "Statistics", render_statistics(rows_by_kind))

    if args.dry_run:
        sys.stdout.write(text)
        return 0

    index_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = index_path.with_suffix(".md.tmp")
    with tmp.open("w") as f:
        f.write(text)
    os.replace(tmp, index_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
