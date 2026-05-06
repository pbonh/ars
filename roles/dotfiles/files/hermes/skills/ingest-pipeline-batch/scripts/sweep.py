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

  dispatch <library_root> --root <book_root_basename> [--wiki-root <abs>] [--vision <mode>] [--force]
      Emit the literal `delegate_task` kwargs (JSON) for one book. The
      orchestrator forwards the parsed JSON verbatim to delegate_task —
      no template transcription, no parameter omission. Picks Step 3a
      vs Step 3b automatically from the presence of --wiki-root, and
      reads `wiki_pending` from library.json (persisted by `scan`).

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


# ---------- delegate_task templates (single source of truth) ----------
#
# These constants own the per-book delegate_task kwargs. SKILL.md no
# longer carries inline templates — it instructs the orchestrator to
# call `dispatch` and forward the JSON verbatim. If you change a goal
# string, context body, iteration cap, or skills preload, do it here.

STEP_3A_GOAL = "Drive {root} to a complete mdBook using the ingest-pipeline skill."

STEP_3A_CONTEXT = """\
Book directory (absolute): {abs_path}
Force flag: {force_flag}           # forward as --force if true
Vision mode: {vision_mode}   # forward as --vision <mode>

Run the ingest-pipeline skill against this directory. Follow the
skill's Step 0 / Step 1 loop exactly: invoke run_pipeline.py,
read the JSON action signal, dispatch pdf-to-mdbook on S1,
record-phase on return, repair build errors when surfaced.
Stop on `done` or any `failed` record-phase.
"""

STEP_3A_FIXED = {
    "toolsets": ["terminal", "file", "vision"],
    "skills": ["ingest-pipeline", "pdf-to-mdbook"],
    "max_iterations": 80,
    "max_spawn_depth": 2,
}

STEP_3B_GOAL = "Drive {root} through ingest-pipeline → wiki-ingest → wiki-lint."

STEP_3B_CONTEXT = """\
Book directory (absolute): {abs_path}
Wiki root (absolute):      {abs_wiki_root}
Force flag:                {force_flag}           # forward as --force if true
Vision mode:               {vision_mode}    # forward as --vision <mode>
Wiki-pending only:         {wiki_pending}           # from working_set entry

Run the chain in order:

1. ingest-pipeline against the book directory.
   - Skip if `Wiki-pending only` is true (pipeline.json already
     reports complete). Otherwise follow ingest-pipeline's Step 0
     / Step 1 loop exactly: invoke run_pipeline.py, read the JSON
     action signal, dispatch pdf-to-mdbook on S1, record-phase
     on return, repair build errors when surfaced. Stop on `done`
     or any `failed` record-phase.
   - On `failed`: write <book_dir>/wiki.json with
     {{"status": "failed", "failed_phase": "ingest-pipeline",
      "error_message": "<message>"}} and return — do NOT proceed.

2. wiki-ingest against {abs_wiki_root}.
   - Run the skill's Step 0 triage. wiki-ingest naturally skips
     sources whose wiki/summaries/<slug>.md already exists, so
     only the freshly-completed source (or any unprocessed
     siblings sharing this wiki root) will be ingested. Process
     to completion.
   - On any failure: write <book_dir>/wiki.json with
     {{"status": "failed", "failed_phase": "wiki-ingest",
      "error_message": "<message>"}} and return.

3. wiki-lint against {abs_wiki_root}.
   - Run the full lint workflow (read pages → run checks →
     auto-fix → update statistics → update dashboard/analytics
     → append to log → report).
   - On any failure: write <book_dir>/wiki.json with
     {{"status": "failed", "failed_phase": "wiki-lint",
      "error_message": "<message>"}} and return.

4. On success of all three, write <book_dir>/wiki.json with
   {{"status": "complete",
    "summary_path": "{abs_wiki_root}/wiki/summaries/<slug>.md",
    "linted_at": "<iso8601 utc>"}}.

Return a one-line summary of which phase finished last.
"""

STEP_3B_FIXED = {
    "toolsets": ["terminal", "file", "vision"],
    "skills": ["ingest-pipeline", "pdf-to-mdbook", "wiki-ingest", "wiki-lint"],
    "max_iterations": 150,
    "max_spawn_depth": 2,
}


def render_dispatch(
    *,
    book_root: str,
    abs_path: str,
    abs_wiki_root: str | None,
    vision_mode: str,
    force_flag: bool,
    wiki_pending: bool,
) -> dict:
    if abs_wiki_root is None:
        return {
            "goal": STEP_3A_GOAL.format(root=book_root),
            "context": STEP_3A_CONTEXT.format(
                abs_path=abs_path,
                force_flag="true" if force_flag else "false",
                vision_mode=vision_mode,
            ),
            **STEP_3A_FIXED,
        }
    return {
        "goal": STEP_3B_GOAL.format(root=book_root),
        "context": STEP_3B_CONTEXT.format(
            abs_path=abs_path,
            abs_wiki_root=abs_wiki_root,
            force_flag="true" if force_flag else "false",
            vision_mode=vision_mode,
            wiki_pending="true" if wiki_pending else "false",
        ),
        **STEP_3B_FIXED,
    }


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
            "wiki_pending": False,
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
            entry["wiki_pending"] = True
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


def cmd_dispatch(args: argparse.Namespace) -> None:
    library_root = Path(args.library_root).resolve()
    if not library_root.is_dir():
        fatal(f"{library_root} is not a directory.")

    book_dir = library_root / args.root
    if not is_book_root(book_dir):
        fatal(f"{book_dir} is not a recognized book root under {library_root}.")

    abs_wiki_root: str | None = None
    if args.wiki_root is not None:
        if not args.wiki_root.startswith("/"):
            fatal(f"--wiki-root must be an absolute path; got {args.wiki_root!r}.")
        wiki_root_path = Path(args.wiki_root)
        if not wiki_root_path.is_dir():
            fatal(f"--wiki-root {args.wiki_root} is not a directory.")
        abs_wiki_root = str(wiki_root_path.resolve())

    lib = load_library(library_root)
    entry = find_book_entry(lib, args.root)
    wiki_pending = bool(entry and entry.get("wiki_pending"))

    payload = render_dispatch(
        book_root=args.root,
        abs_path=str(book_dir.resolve()),
        abs_wiki_root=abs_wiki_root,
        vision_mode=args.vision,
        force_flag=args.force,
        wiki_pending=wiki_pending,
    )
    json.dump(payload, sys.stdout, indent=2)
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

    disp_p = sub.add_parser("dispatch", help="Emit the literal delegate_task kwargs (JSON) for one book.")
    disp_p.add_argument("library_root")
    disp_p.add_argument("--root", required=True, help="Book root basename.")
    disp_p.add_argument("--wiki-root", default=None, help="Wiki root (parent of raw/ and wiki/). Switches to Step 3b chain template.")
    disp_p.add_argument("--vision", default="auto", choices=["auto", "never", "always"])
    disp_p.add_argument("--force", action="store_true")

    fin_p = sub.add_parser("finalize", help="Set last_swept_at, sort, print summary.")
    fin_p.add_argument("library_root")

    args = parser.parse_args()
    {"scan": cmd_scan, "mark": cmd_mark, "dispatch": cmd_dispatch, "finalize": cmd_finalize}[args.cmd](args)


if __name__ == "__main__":
    main()
