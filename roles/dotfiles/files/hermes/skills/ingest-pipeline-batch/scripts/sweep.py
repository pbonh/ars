#!/usr/bin/env python3
"""
sweep.py — Deterministic library walk for ingest-pipeline-batch.

Walks the library root, identifies book directories, filters out books
that are already complete, and emits the working set as JSON. Owns
library.json bookkeeping (create/update/finalize). The orchestrator
LLM reads the working set and dispatches per-book ingest-pipeline
subagents.

Subcommands:
  scan <library_root> [--force] [--wiki-root <abs_wiki_root>]
      Walk the tree, refresh library.json, print the working set as JSON.
      With --wiki-root, a book counts as complete only if both
      pipeline.json and wiki.json report status:complete; books whose
      pipeline finished but whose wiki chain is incomplete are returned in
      the working set with `wiki_pending: true`.

  mark <library_root> --root <book_root_basename> --status <pending|in_progress|complete|failed> [--failed-phase X] [--error MSG]
      Update one book entry in library.json. Called by the orchestrator
      before/after each per-book subagent dispatch.

  finalize <library_root>
      Set last_swept_at, sort books by root name, print a summary.

Output of `scan` (stdout, JSON):
  {
    "library_root": "/abs",
    "total": 41,
    "complete": 3,
    "skipped_complete": 3,
    "working_set": [
      {"root": "calculus", "abs_path": "/abs/calculus", "prior_status": null},
      ...
    ]
  }

The script never invokes ingest-pipeline. Dispatch is the orchestrator's
job — it knows how to call delegate_task with the right parameters.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


LIBRARY_FILENAME = "library.json"
PIPELINE_FILENAME = "pipeline.json"
WIKI_FILENAME = "wiki.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def fatal(msg: str, code: int = 2) -> "NoReturn":
    print(f"sweep: {msg}", file=sys.stderr)
    sys.exit(code)


def library_path(root: Path) -> Path:
    return root / LIBRARY_FILENAME


def load_library(root: Path) -> dict:
    p = library_path(root)
    if not p.exists():
        return {
            "schema_version": 1,
            "library_root": str(root),
            "last_swept_at": None,
            "books": [],
        }
    with p.open() as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            fatal(f"{p} is not valid JSON: {e}")


def write_library(root: Path, lib: dict) -> None:
    p = library_path(root)
    tmp = p.with_suffix(".json.tmp")
    with tmp.open("w") as f:
        json.dump(lib, f, indent=2)
        f.write("\n")
    os.replace(tmp, p)


def is_book_root(d: Path) -> bool:
    """Per ingest-pipeline-batch SKILL.md Step 2."""
    if not d.is_dir():
        return False
    if (d / PIPELINE_FILENAME).exists():
        return True
    if (d / "book.toml").exists() and (d / "src" / "SUMMARY.md").exists():
        return True
    pdfs = list(d.glob("*.pdf"))
    if len(pdfs) == 1:
        return True
    return False


def read_pipeline_status(book_dir: Path) -> tuple[str | None, str | None, str | None]:
    """Return (status, failed_phase, error_message) from pipeline.json, or all None."""
    p = book_dir / PIPELINE_FILENAME
    if not p.exists():
        return None, None, None
    try:
        with p.open() as f:
            m = json.load(f)
    except json.JSONDecodeError:
        return None, None, "pipeline.json is malformed"
    return m.get("status"), m.get("failed_phase"), m.get("error_message")


def read_wiki_status(book_dir: Path) -> tuple[str | None, str | None, str | None]:
    """Return (status, failed_phase, error_message) from wiki.json, or all None."""
    p = book_dir / WIKI_FILENAME
    if not p.exists():
        return None, None, None
    try:
        with p.open() as f:
            m = json.load(f)
    except json.JSONDecodeError:
        return None, None, "wiki.json is malformed"
    return m.get("status"), m.get("failed_phase"), m.get("error_message")


def find_book_entry(lib: dict, root_name: str) -> dict | None:
    for b in lib["books"]:
        if b["root"] == root_name:
            return b
    return None


def upsert_book_entry(lib: dict, entry: dict) -> None:
    existing = find_book_entry(lib, entry["root"])
    if existing is None:
        lib["books"].append(entry)
        return
    existing.update(entry)


# ---------- Subcommands ----------

def cmd_scan(args: argparse.Namespace) -> None:
    root = Path(args.library_root).resolve()
    if not root.is_dir():
        fatal(f"{root} is not a directory.")

    lib = load_library(root)

    candidates = sorted([d for d in root.iterdir() if is_book_root(d)], key=lambda d: d.name)

    working_set: list[dict] = []
    complete = 0
    failed = 0
    skipped_complete = 0

    seen_roots: set[str] = set()
    for d in candidates:
        seen_roots.add(d.name)
        status, failed_phase, error_message = read_pipeline_status(d)
        entry = {
            "root": d.name,
            "pipeline_json": f"{d.name}/{PIPELINE_FILENAME}",
        }
        if status == "complete" and not args.force:
            wiki_status = None
            if args.wiki_root is not None:
                wiki_status, _, _ = read_wiki_status(d)
            if args.wiki_root is None or wiki_status == "complete":
                entry["status"] = "complete"
                upsert_book_entry(lib, entry)
                complete += 1
                skipped_complete += 1
                continue
            # Pipeline done, wiki chain still pending → re-dispatch.
            entry["status"] = "in_progress"
            entry["pipeline_complete"] = True
            upsert_book_entry(lib, entry)
            working_set.append({
                "root": d.name,
                "abs_path": str(d),
                "prior_status": status,
                "prior_failed_phase": None,
                "wiki_pending": True,
            })
            continue

        if status == "failed":
            failed += 1
            entry.update({"status": "failed", "failed_phase": failed_phase, "error_message": error_message})
        elif status in ("in_progress", "pending"):
            entry["status"] = "in_progress"
        elif args.force and status == "complete":
            entry["status"] = "in_progress"
        else:
            entry["status"] = "pending"

        upsert_book_entry(lib, entry)
        working_set.append({
            "root": d.name,
            "abs_path": str(d),
            "prior_status": status,
            "prior_failed_phase": failed_phase,
        })

    # Drop entries for directories that no longer exist.
    lib["books"] = [b for b in lib["books"] if b["root"] in seen_roots]
    lib["books"].sort(key=lambda b: b["root"])
    write_library(root, lib)

    json.dump({
        "library_root": str(root),
        "total": len(candidates),
        "complete": complete,
        "skipped_complete": skipped_complete,
        "failed_prior": failed,
        "pending": len(working_set),
        "working_set": working_set,
    }, sys.stdout, indent=2)
    sys.stdout.write("\n")


def cmd_mark(args: argparse.Namespace) -> None:
    root = Path(args.library_root).resolve()
    lib = load_library(root)
    entry = find_book_entry(lib, args.root)
    if entry is None:
        # Create a minimal entry; this happens if `mark` is called before `scan`.
        entry = {"root": args.root, "pipeline_json": f"{args.root}/{PIPELINE_FILENAME}"}
        lib["books"].append(entry)
    entry["status"] = args.status
    if args.failed_phase is not None:
        entry["failed_phase"] = args.failed_phase
    if args.error is not None:
        entry["error_message"] = args.error
    if args.status == "complete":
        # Drop transient fields.
        entry.pop("failed_phase", None)
        entry.pop("error_message", None)
    write_library(root, lib)
    json.dump({"action": "marked", "root": args.root, "status": args.status}, sys.stdout, indent=2)
    sys.stdout.write("\n")


def cmd_finalize(args: argparse.Namespace) -> None:
    root = Path(args.library_root).resolve()
    lib = load_library(root)
    lib["last_swept_at"] = now_iso()
    lib["books"].sort(key=lambda b: b["root"])
    write_library(root, lib)

    by_status: dict[str, int] = {}
    failed_books: list[dict] = []
    for b in lib["books"]:
        s = b.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1
        if s == "failed":
            failed_books.append(b)

    json.dump({
        "action": "finalized",
        "library_root": str(root),
        "total": len(lib["books"]),
        "by_status": by_status,
        "failed": failed_books,
    }, sys.stdout, indent=2)
    sys.stdout.write("\n")


# ---------- argparse ----------

def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministic library walk for ingest-pipeline-batch.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    scan_p = sub.add_parser("scan", help="Walk the library, refresh library.json, print the working set.")
    scan_p.add_argument("library_root")
    scan_p.add_argument("--force", action="store_true", help="Include books with status:complete in the working set.")
    scan_p.add_argument("--wiki-root", default=None, help="Wiki root (parent of raw/ and wiki/). When set, a book is only complete if both pipeline.json and wiki.json report complete.")

    mark_p = sub.add_parser("mark", help="Update one book entry in library.json.")
    mark_p.add_argument("library_root")
    mark_p.add_argument("--root", required=True, help="Book root basename.")
    mark_p.add_argument("--status", required=True, choices=["pending", "in_progress", "complete", "failed"])
    mark_p.add_argument("--failed-phase", default=None)
    mark_p.add_argument("--error", default=None)

    fin_p = sub.add_parser("finalize", help="Set last_swept_at, sort, print summary.")
    fin_p.add_argument("library_root")

    args = parser.parse_args()
    {"scan": cmd_scan, "mark": cmd_mark, "finalize": cmd_finalize}[args.cmd](args)


if __name__ == "__main__":
    main()
