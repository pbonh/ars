#!/usr/bin/env python3
"""
triage_source.py — Classify every source in a wiki's `raw/` directory.

For each entry, decide whether to ingest from a structured mdBook (output of
`ingest-pipeline` / `pdf-to-mdbook`) or fall back to the raw source. Emits a
single JSON manifest describing what the wiki-ingest skill should read for
each source. The LLM never has to do filesystem probes inside its iteration
budget.

mdBook detection (in priority order, per source):
  1. Sibling directory: <source_dir>/<stem>-mdbook/ contains book.toml +
     src/SUMMARY.md. (Matches pdf-to-mdbook's default output naming.)
  2. Sibling pipeline.json: <source_dir>/pipeline.json with status:complete
     and a working_dir that contains a valid mdbook layout.
  3. (For directory entries in raw/) the entry itself contains book.toml +
     src/SUMMARY.md, OR contains a pipeline.json pointing to one.

Source kinds in the output:
  - "mdbook"   — prefer; ingest from chapter .md files + book.toml metadata
  - "markdown" — native markdown source, read directly
  - "text"     — plain text, read directly
  - "pdf"      — no mdBook found, fall back to progressive PDF read
  - "other"    — unknown extension; skip with a warning

Usage:
    python triage_source.py <wiki_root>           # triage everything in raw/
    python triage_source.py <wiki_root> --json    # same, force JSON to stdout (default)
    python triage_source.py <wiki_root> --source <path>   # triage one entry only

Output: JSON to stdout. Errors and warnings go to stderr.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


SCHEMA_VERSION = 1
RAW_SUBDIR = "raw"
# Summaries live under <wiki_root>/wiki/summaries/<slug>.md per the
# wiki-bootstrap layout. Don't confuse this with `<wiki_root>/summaries/`.
SUMMARIES_SUBDIR = "wiki/summaries"


# ---------- helpers ----------

def fatal(msg: str, code: int = 2) -> "NoReturn":
    print(f"triage_source: {msg}", file=sys.stderr)
    sys.exit(code)


def warn(msg: str) -> None:
    print(f"triage_source: warning: {msg}", file=sys.stderr)


def read_book_toml(book_toml: Path) -> dict:
    """Minimal [book] section parser. Returns {title, authors, language}."""
    out: dict = {}
    if not book_toml.is_file():
        return out
    in_book = False
    try:
        text = book_toml.read_text()
    except OSError:
        return out
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("[") and s.endswith("]"):
            in_book = (s == "[book]")
            continue
        if not in_book:
            continue
        m = re.match(r"([a-z_-]+)\s*=\s*(.+)", s)
        if not m:
            continue
        key, raw = m.group(1), m.group(2).strip()
        if key == "title":
            out["title"] = _strip_toml_string(raw)
        elif key == "authors":
            out["authors"] = _parse_toml_list(raw)
        elif key == "language":
            out["language"] = _strip_toml_string(raw)
    return out


def _strip_toml_string(raw: str) -> str:
    raw = raw.strip()
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]
    return raw


def _parse_toml_list(raw: str) -> list[str]:
    raw = raw.strip()
    if not (raw.startswith("[") and raw.endswith("]")):
        return [_strip_toml_string(raw)]
    inner = raw[1:-1]
    parts = [p.strip() for p in inner.split(",") if p.strip()]
    return [_strip_toml_string(p) for p in parts]


SUMMARY_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+\.md)\)")


def parse_summary(summary_md: Path, src_root: Path) -> list[dict]:
    """Parse src/SUMMARY.md → list of {title, path (abs), missing} chapter entries."""
    chapters: list[dict] = []
    if not summary_md.is_file():
        return chapters
    text = summary_md.read_text()
    for title, ref in SUMMARY_LINK_RE.findall(text):
        target = (src_root / ref).resolve()
        chapters.append({
            "title": title,
            "path": str(target),
            "rel_path": ref,
            "exists": target.is_file(),
        })
    return chapters


def load_pipeline_json(p: Path) -> dict | None:
    if not p.is_file():
        return None
    try:
        with p.open() as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def is_mdbook_layout(d: Path) -> bool:
    return (d / "book.toml").is_file() and (d / "src" / "SUMMARY.md").is_file()


def find_mdbook_for_pdf(pdf: Path) -> tuple[Path | None, str]:
    """Return (mdbook_root, detection_method) or (None, '')."""
    parent = pdf.parent
    stem = pdf.stem

    candidate = parent / f"{stem}-mdbook"
    if is_mdbook_layout(candidate):
        return candidate, "sibling-naming-convention"

    pipeline = load_pipeline_json(parent / "pipeline.json")
    if pipeline and pipeline.get("status") == "complete":
        wd = pipeline.get("working_dir")
        if wd:
            wd_path = Path(wd)
            if is_mdbook_layout(wd_path):
                return wd_path, "sibling-pipeline.json"

    return None, ""


def find_mdbook_for_dir(d: Path) -> tuple[Path | None, str, Path | None]:
    """For a directory entry in raw/, see if it is itself or contains a book.
    Returns (mdbook_root, detection_method, pdf_inside) where pdf_inside is the
    PDF inside the directory (if any) used as the fallback source.
    """
    if is_mdbook_layout(d):
        return d, "self-is-mdbook", None

    pipeline = load_pipeline_json(d / "pipeline.json")
    if pipeline and pipeline.get("status") == "complete":
        wd = pipeline.get("working_dir")
        if wd and is_mdbook_layout(Path(wd)):
            return Path(wd), "self-pipeline.json", None

    pdfs = sorted(d.glob("*.pdf"))
    if len(pdfs) == 1:
        pdf = pdfs[0]
        candidate = d / f"{pdf.stem}-mdbook"
        if is_mdbook_layout(candidate):
            return candidate, "single-pdf-sibling-mdbook", pdf
        # Also check pipeline.json was already handled above.
        return None, "", pdf

    return None, "", None


# ---------- per-entry triage ----------

def triage_file(raw_path: Path, summaries_dir: Path) -> dict:
    stem = raw_path.stem
    record: dict = {
        "raw_path": str(raw_path),
        "stem": stem,
        "slug": _slug(stem),
        "processed": (summaries_dir / f"{_slug(stem)}.md").is_file(),
        "kind": None,
        "fallback_reason": None,
    }
    suffix = raw_path.suffix.lower()
    if suffix == ".pdf":
        mdbook_root, method = find_mdbook_for_pdf(raw_path)
        if mdbook_root is not None:
            record["kind"] = "mdbook"
            record["mdbook_root"] = str(mdbook_root)
            record["detection"] = method
            record.update(_mdbook_metadata(mdbook_root))
        else:
            record["kind"] = "pdf"
            record["fallback_reason"] = "no sibling -mdbook directory; no pipeline.json with status:complete"
    elif suffix in (".md", ".markdown"):
        record["kind"] = "markdown"
        record["fallback_reason"] = "native markdown — no mdBook stage applies"
    elif suffix == ".txt":
        record["kind"] = "text"
        record["fallback_reason"] = "plain text — no mdBook stage applies"
    else:
        record["kind"] = "other"
        record["fallback_reason"] = f"unknown extension '{suffix}' — wiki-ingest will skip with a warning"
    return record


def triage_dir(raw_path: Path, summaries_dir: Path) -> dict:
    stem = raw_path.name
    record: dict = {
        "raw_path": str(raw_path),
        "stem": stem,
        "slug": _slug(stem),
        "processed": (summaries_dir / f"{_slug(stem)}.md").is_file(),
        "kind": None,
        "fallback_reason": None,
    }
    mdbook_root, method, pdf_inside = find_mdbook_for_dir(raw_path)
    if mdbook_root is not None:
        record["kind"] = "mdbook"
        record["mdbook_root"] = str(mdbook_root)
        record["detection"] = method
        record.update(_mdbook_metadata(mdbook_root))
    elif pdf_inside is not None:
        record["kind"] = "pdf"
        record["pdf_path"] = str(pdf_inside)
        record["fallback_reason"] = "directory contains a PDF but no mdBook output yet"
    else:
        record["kind"] = "other"
        record["fallback_reason"] = "directory contains neither an mdBook layout nor a single PDF"
    return record


def _mdbook_metadata(mdbook_root: Path) -> dict:
    meta = read_book_toml(mdbook_root / "book.toml")
    chapters = parse_summary(mdbook_root / "src" / "SUMMARY.md", mdbook_root / "src")
    out = {
        "title": meta.get("title"),
        "authors": meta.get("authors", []),
        "language": meta.get("language", "en"),
        "chapter_count": len(chapters),
        "chapters": chapters,
    }
    missing = [c for c in chapters if not c["exists"]]
    if missing:
        out["missing_chapters"] = [c["rel_path"] for c in missing]
    return out


def _slug(stem: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", stem.lower()).strip("-")
    return s or "source"


# ---------- main ----------

def triage_one(raw_entry: Path, summaries_dir: Path) -> dict:
    if raw_entry.is_file():
        return triage_file(raw_entry, summaries_dir)
    if raw_entry.is_dir():
        return triage_dir(raw_entry, summaries_dir)
    return {
        "raw_path": str(raw_entry),
        "stem": raw_entry.name,
        "slug": _slug(raw_entry.name),
        "kind": "other",
        "processed": False,
        "fallback_reason": "not a regular file or directory",
    }


def _dedupe_mdbook_outputs(sources: list[dict]) -> list[dict]:
    """Mark directory entries that ARE another entry's resolved mdbook_root.

    Example: raw/ contains both `calculus.pdf` (kind=mdbook, mdbook_root pointing
    at raw/calculus-mdbook/) and `calculus-mdbook/` (kind=mdbook, self-detection).
    The second entry is the *output* of the first — ingesting both would double-
    count chapters. Mark the directory entry kind="mdbook-output" so the wiki-
    ingest skill skips it.
    """
    referenced: set[str] = set()
    for s in sources:
        root = s.get("mdbook_root")
        if not root:
            continue
        # Only PDF→mdbook resolutions count as "this entry references that dir".
        # Self-detection (a directory that IS the mdbook) doesn't claim anything
        # other than itself.
        if s.get("detection") in ("self-is-mdbook", "self-pipeline.json"):
            continue
        referenced.add(str(Path(root).resolve()))

    for s in sources:
        if s["kind"] != "mdbook":
            continue
        if Path(s["raw_path"]).resolve().is_dir() and str(Path(s["raw_path"]).resolve()) in referenced:
            s["kind"] = "mdbook-output"
            s["fallback_reason"] = "this directory is the mdBook output of a sibling source — skip"
    return sources


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("wiki_root", help="Path to the wiki root directory (the one containing raw/).")
    p.add_argument("--source", default=None, help="Triage only this single entry under raw/ (path).")
    args = p.parse_args()

    wiki_root = Path(args.wiki_root).resolve()
    if not wiki_root.is_dir():
        fatal(f"{wiki_root} is not a directory.")

    raw_dir = wiki_root / RAW_SUBDIR
    if not raw_dir.is_dir():
        fatal(f"{raw_dir} does not exist or is not a directory.")

    summaries_dir = wiki_root / SUMMARIES_SUBDIR

    if args.source:
        entry = Path(args.source).resolve()
        try:
            entry.relative_to(raw_dir)
        except ValueError:
            fatal(f"--source {entry} is not inside {raw_dir}")
        sources = [triage_one(entry, summaries_dir)]
    else:
        entries = sorted(p for p in raw_dir.iterdir() if not p.name.startswith("."))
        sources = [triage_one(e, summaries_dir) for e in entries]
        sources = _dedupe_mdbook_outputs(sources)

    by_kind: dict[str, int] = {}
    for s in sources:
        by_kind[s["kind"]] = by_kind.get(s["kind"], 0) + 1

    out = {
        "schema_version": SCHEMA_VERSION,
        "wiki_root": str(wiki_root),
        "raw_dir": str(raw_dir),
        "total": len(sources),
        "by_kind": by_kind,
        "unprocessed": sum(1 for s in sources if not s["processed"]),
        "sources": sources,
    }
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
