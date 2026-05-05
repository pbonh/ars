#!/usr/bin/env python3
"""
run_pipeline.py — Deterministic state machine for ingest-pipeline.

Owns every step that does not require LLM judgment: path resolution, state
classification (per references/state-detection.md), pipeline.json
read/write with the filesystem-truth rule, S3 inline scaffold, S4 mdbook
build with one auto-fix round, S5 finalize. For S1 it does NOT invoke
pdf-to-mdbook itself — it emits a JSON action signal asking the calling
LLM agent to dispatch the subagent. For S4 build failures the auto-fix
cannot repair, it emits a judgment signal with the captured stderr.

The script is invoked once per turn by the LLM agent. It performs at most
one state transition per invocation and exits with one of:

  exit 0 + stdout JSON {"action": "done"}                         — S5 reached
  exit 0 + stdout JSON {"action": "delegate_pdf_to_mdbook", ...}  — S1, agent must dispatch subagent
  exit 0 + stdout JSON {"action": "need_judgment_build_fix", ...} — S4 build failed after auto-fix
  exit 0 + stdout JSON {"action": "advanced", ...}                — phase advanced, agent should re-run
  exit 2 + stderr message                                         — fatal (S0, missing tools, bad input)

Usage:
    python run_pipeline.py <book_root_or_pdf> [--force] [--vision auto|never|always]
    python run_pipeline.py --record-phase <book_root> --phase <name> --status <complete|failed> [--manifest <rel>] [--invocation-id <id>] [--error <msg>] [--working-dir <path>]

The second form is how the LLM agent reports back the result of a subagent
dispatch (S1's pdf-to-mdbook). It updates pipeline.json atomically so the
next state-machine invocation classifies cleanly.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path


# ---------- IO helpers ----------

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def emit(payload: dict) -> None:
    """Print a JSON action signal to stdout (the only thing the LLM reads)."""
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")


def fatal(msg: str, code: int = 2) -> "NoReturn":
    print(f"run_pipeline: {msg}", file=sys.stderr)
    sys.exit(code)


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


# ---------- Manifest ----------

PIPELINE_FILENAME = "pipeline.json"


def manifest_path(book_root: Path) -> Path:
    return book_root / PIPELINE_FILENAME


def load_manifest(book_root: Path) -> dict | None:
    p = manifest_path(book_root)
    if not p.exists():
        return None
    try:
        with p.open() as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        fatal(f"{p} is not valid JSON: {e}")


def write_manifest(book_root: Path, m: dict) -> None:
    m["updated_at"] = now_iso()
    p = manifest_path(book_root)
    tmp = p.with_suffix(".json.tmp")
    with tmp.open("w") as f:
        json.dump(m, f, indent=2)
        f.write("\n")
    os.replace(tmp, p)


def new_manifest(book_root: Path, input_target: Path, working_dir: Path, initial_state: str) -> dict:
    return {
        "schema_version": 1,
        "skill": "ingest-pipeline",
        "book_root": str(book_root),
        "input_target": str(input_target),
        "working_dir": str(working_dir),
        "initial_state": initial_state,
        "current_state": initial_state,
        "status": "pending",
        "started_at": now_iso(),
        "updated_at": now_iso(),
        "phases": [],
        "failed_phase": None,
        "error_message": None,
        "notes": [],
    }


def append_note(m: dict, note: str) -> None:
    m.setdefault("notes", []).append(f"{now_iso()} {note}")


def append_phase(m: dict, name: str, skill: str | None) -> dict:
    phase = {
        "name": name,
        "skill": skill,
        "status": "pending",
        "started_at": now_iso(),
    }
    m["phases"].append(phase)
    return phase


def mark_phase(phase: dict, status: str, **extra) -> None:
    phase["status"] = status
    if status in ("complete", "failed"):
        phase["completed_at"] = now_iso()
    for k, v in extra.items():
        if v is not None:
            phase[k] = v


# ---------- State classification ----------

def classify(book_root: Path, working_dir: Path, manifest: dict | None, force: bool) -> str:
    """Return one of S0/S1/S3/S4/S5 per references/state-detection.md."""
    # Step 3 of the algorithm — manifest-driven S5.
    if manifest and manifest.get("status") == "complete" and not force:
        # Filesystem-truth check: confirm output dir still exists.
        wd = Path(manifest.get("working_dir", str(working_dir)))
        if (wd / "book.toml").exists() and (wd / "src" / "SUMMARY.md").exists():
            return "S5"
        # Filesystem disagrees — fall through to fresh classification.
        append_note(manifest, "filesystem reclassification: status:complete but working_dir missing book.toml/SUMMARY.md")
        manifest["status"] = "in_progress"

    # Step 4 — partial mdBook.
    if (working_dir / "book.toml").exists() and (working_dir / "src" / "SUMMARY.md").exists():
        return "S4"

    # Step 5 — count files at top level of working_dir.
    pdfs = list(working_dir.glob("*.pdf"))
    mds = list(working_dir.glob("*.md"))

    if len(mds) >= 2 and len(pdfs) == 0:
        return "S3"
    if len(pdfs) == 1:
        return "S1"

    return "S0"


# ---------- Phase actions ----------

def title_case_slug(slug: str) -> str:
    parts = slug.replace("_", "-").split("-")
    # Strip leading numeric prefix on filenames like "01-intro".
    if parts and parts[0].isdigit():
        parts = parts[1:] or [slug]
    return " ".join(p.capitalize() for p in parts if p)


def do_s3_scaffold(book_root: Path, force: bool) -> tuple[Path, list[str]]:
    """S3 inline scaffold. Returns (mdbook_root, file_list)."""
    stem = book_root.name
    out = book_root / f"{stem}-mdbook"
    if out.exists() and not force:
        raise RuntimeError(f"output dir exists: {out} (pass --force to overwrite)")
    if out.exists():
        shutil.rmtree(out)
    src = out / "src" / "assets" / "images"
    src.mkdir(parents=True, exist_ok=True)

    title = title_case_slug(stem)
    book_toml = textwrap.dedent(f"""\
        [book]
        title = "{title}"
        authors = ["Unknown"]
        language = "en"
        src = "src"

        [build]
        build-dir = "book"
        create-missing = false
        """)
    (out / "book.toml").write_text(book_toml)

    md_files = sorted(p.name for p in book_root.glob("*.md"))
    if not md_files:
        raise RuntimeError("S3 scaffold: no .md files at book root")

    summary_lines = ["# Summary", "", "[Introduction](README.md)", ""]
    for fn in md_files:
        stem_part = Path(fn).stem
        summary_lines.append(f"- [{title_case_slug(stem_part)}]({fn})")
    summary_lines.append("")
    (out / "src" / "SUMMARY.md").write_text("\n".join(summary_lines))

    if not (out / "src" / "README.md").exists():
        (out / "src" / "README.md").write_text(f"# {title}\n\nGenerated from pre-split markdown by ingest-pipeline.\n")

    for fn in md_files:
        shutil.copy2(book_root / fn, out / "src" / fn)

    return out, md_files


SUMMARY_LINK_RE = None  # compiled lazily


def diagnose_and_stub_missing(working_dir: Path) -> list[str]:
    """Read src/SUMMARY.md, create stubs for any referenced .md files that don't exist."""
    import re
    summary = working_dir / "src" / "SUMMARY.md"
    if not summary.exists():
        return []
    text = summary.read_text()
    pattern = re.compile(r"\[([^\]]+)\]\(([^)]+\.md)\)")
    created: list[str] = []
    for title, ref in pattern.findall(text):
        target = working_dir / "src" / ref
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"# {title}\n\n<!-- TODO: content -->\n")
        created.append(ref)
    return created


def try_mdbook_auto_fix(working_dir: Path, stderr: str) -> bool:
    """Attempt one heuristic fix based on mdbook stderr. Returns True if a fix was applied."""
    fixed = False

    # Missing README.md — write one-line stub.
    readme = working_dir / "src" / "README.md"
    if "README.md" in stderr and not readme.exists():
        readme.write_text(f"# {working_dir.name}\n\nIntroduction.\n")
        fixed = True

    # Broken table syntax — wrap suspected file in a fenced code block. We can
    # only act on this if mdbook named a file. Best-effort: scan stderr for
    # "src/<file>.md" patterns mentioned alongside "table".
    import re
    if "table" in stderr.lower():
        for match in re.findall(r"(src/[^\s:]+\.md)", stderr):
            f = working_dir / match
            if not f.exists():
                continue
            content = f.read_text()
            if "```" not in content and "|" in content:
                f.write_text(f"```\n{content}\n```\n")
                fixed = True

    return fixed


def run_mdbook_build(working_dir: Path) -> tuple[int, str]:
    res = subprocess.run(
        ["mdbook", "build"],
        cwd=working_dir,
        capture_output=True,
        text=True,
    )
    return res.returncode, (res.stderr or "") + (res.stdout or "")


# ---------- Environment ----------

def env_check() -> None:
    missing = [c for c in ("pdfinfo", "pdftotext", "mdbook", "jq") if not have(c)]
    if missing:
        fatal(
            "missing required tools: " + ", ".join(missing) + "\n"
            "Install hints:\n"
            "  macOS: brew install poppler mdbook jq\n"
            "  Linux/devbox: devbox add poppler mdbook jq"
        )


# ---------- Main drive ----------

def cmd_run(target: Path, force: bool, vision: str) -> None:
    env_check()

    # Step 1 — resolve book_root and input_target.
    if target.is_file() and target.suffix.lower() == ".pdf":
        book_root = target.parent
        input_target = target
    elif target.is_dir():
        book_root = target
        input_target = target
    else:
        fatal(f"target does not exist or is not a .pdf/dir: {target}")

    # working_dir from prior manifest if present.
    manifest = load_manifest(book_root)
    working_dir = book_root
    if manifest and manifest.get("working_dir"):
        wd = Path(manifest["working_dir"])
        if wd.exists():
            working_dir = wd
        else:
            append_note(manifest, f"working_dir {wd} missing on disk; reverting to book_root")

    # Step 2 — classify.
    state = classify(book_root, working_dir, manifest, force)

    # Step 3 — open or create manifest.
    if manifest is None:
        if state == "S0":
            fatal(
                f"{book_root} contains no PDFs, no markdown, and no manifest. "
                "Nothing to ingest. (Add a PDF or markdown file and rerun.)"
            )
        manifest = new_manifest(book_root, input_target, working_dir, state)
    else:
        manifest["current_state"] = state
        if state != "S5":
            manifest.setdefault("status", "in_progress")
            if manifest["status"] == "complete":
                manifest["status"] = "in_progress"

    # Step 4 — dispatch by state.
    if state == "S0":
        # Already short-circuited above when manifest was None. Reaching here
        # means a manifest exists but the filesystem is now empty — record and stop.
        manifest["status"] = "failed"
        manifest["failed_phase"] = None
        manifest["error_message"] = "filesystem reclassified to S0; nothing to ingest"
        write_manifest(book_root, manifest)
        fatal(manifest["error_message"])

    if state == "S1":
        # Find the single PDF.
        pdf_path = input_target if input_target.is_file() else next(working_dir.glob("*.pdf"))
        # Mark a pending phase so a crash mid-subagent leaves a consistent record.
        phase = next((p for p in manifest["phases"] if p["name"] == "mdbook" and p["status"] in ("pending", "in_progress")), None)
        if phase is None:
            phase = append_phase(manifest, "mdbook", "pdf-to-mdbook")
        manifest["status"] = "in_progress"
        write_manifest(book_root, manifest)
        emit({
            "action": "delegate_pdf_to_mdbook",
            "pdf": str(pdf_path),
            "book_root": str(book_root),
            "force": force,
            "vision": vision,
            "phase_index": manifest["phases"].index(phase),
            "note": "Dispatch the pdf-to-mdbook subagent on this PDF, then call run_pipeline.py --record-phase to update state.",
        })
        return

    if state == "S3":
        phase = append_phase(manifest, "scaffold", None)
        manifest["status"] = "in_progress"
        write_manifest(book_root, manifest)
        try:
            mdbook_root, files = do_s3_scaffold(book_root, force)
        except Exception as e:
            mark_phase(phase, "failed", error=str(e))
            manifest["status"] = "failed"
            manifest["failed_phase"] = "scaffold"
            manifest["error_message"] = str(e)
            write_manifest(book_root, manifest)
            fatal(f"S3 scaffold failed: {e}")
        mark_phase(phase, "complete")
        manifest["working_dir"] = str(mdbook_root)
        write_manifest(book_root, manifest)
        emit({"action": "advanced", "from": "S3", "working_dir": str(mdbook_root), "scaffolded_files": files})
        return

    if state == "S4":
        wd = Path(manifest.get("working_dir") or working_dir)
        if not (wd / "book.toml").exists() or not (wd / "src" / "SUMMARY.md").exists():
            manifest["status"] = "failed"
            manifest["failed_phase"] = "build"
            manifest["error_message"] = f"S4 entered but {wd} does not contain a valid mdbook layout"
            write_manifest(book_root, manifest)
            fatal(manifest["error_message"])

        phase = append_phase(manifest, "build", None)
        manifest["status"] = "in_progress"
        write_manifest(book_root, manifest)

        stubbed = diagnose_and_stub_missing(wd)

        rc, output = run_mdbook_build(wd)
        if rc != 0:
            # One auto-fix round.
            if try_mdbook_auto_fix(wd, output):
                rc2, output2 = run_mdbook_build(wd)
                if rc2 == 0:
                    mark_phase(phase, "complete", auto_fix_applied=True, stubbed_files=stubbed or None)
                    manifest["status"] = "complete"
                    manifest["current_state"] = "S5"
                    write_manifest(book_root, manifest)
                    emit({"action": "advanced", "from": "S4", "to": "S5"})
                    return
                output = output2

            # Auto-fix did not repair — hand off to LLM judgment.
            mark_phase(phase, "in_progress", auto_fix_failed=True)
            write_manifest(book_root, manifest)
            emit({
                "action": "need_judgment_build_fix",
                "working_dir": str(wd),
                "stderr": output[-2000:],
                "phase_index": manifest["phases"].index(phase),
                "note": "mdbook build failed and the deterministic auto-fix did not repair it. Inspect stderr, edit files in working_dir, then re-run run_pipeline.py.",
            })
            return

        mark_phase(phase, "complete", stubbed_files=stubbed or None)
        manifest["status"] = "complete"
        manifest["current_state"] = "S5"
        write_manifest(book_root, manifest)
        emit({"action": "advanced", "from": "S4", "to": "S5"})
        return

    if state == "S5":
        # Idempotent finalize.
        manifest["status"] = "complete"
        manifest["current_state"] = "S5"
        write_manifest(book_root, manifest)
        wd = manifest.get("working_dir", str(working_dir))
        emit({
            "action": "done",
            "book_root": str(book_root),
            "working_dir": wd,
            "pipeline_json": str(manifest_path(book_root)),
            "message": f"ingest-pipeline: {book_root} is complete. Preview with: mdbook serve {wd}",
        })
        return

    fatal(f"unhandled state: {state}")


def cmd_record_phase(args: argparse.Namespace) -> None:
    book_root = Path(args.book_root).resolve()
    manifest = load_manifest(book_root)
    if manifest is None:
        fatal(f"no pipeline.json at {book_root}")

    # Locate the matching pending/in_progress phase to update.
    phase = None
    if args.phase_index is not None:
        if 0 <= args.phase_index < len(manifest["phases"]):
            phase = manifest["phases"][args.phase_index]
    if phase is None:
        phase = next(
            (p for p in reversed(manifest["phases"])
             if p["name"] == args.phase and p["status"] in ("pending", "in_progress")),
            None,
        )
    if phase is None:
        fatal(f"no pending/in_progress phase named {args.phase} to update")

    extras: dict = {}
    if args.manifest:
        extras["manifest"] = args.manifest
    if args.invocation_id:
        extras["subagent_invocation_id"] = args.invocation_id

    if args.status == "complete":
        mark_phase(phase, "complete", **extras)
        if args.working_dir:
            manifest["working_dir"] = args.working_dir
        # Do NOT mark top-level complete here — the next run_pipeline pass
        # reclassifies and decides whether we've reached S5.
        manifest["status"] = "in_progress"
    elif args.status == "failed":
        mark_phase(phase, "failed", error=args.error or "unknown")
        manifest["status"] = "failed"
        manifest["failed_phase"] = phase["name"]
        manifest["error_message"] = args.error or "unknown"
    else:
        fatal(f"--status must be 'complete' or 'failed', got {args.status}")

    write_manifest(book_root, manifest)
    emit({"action": "phase_recorded", "phase": phase["name"], "status": args.status})


# ---------- argparse ----------

def main() -> None:
    # If the first arg is not a known subcommand, default to `run`.
    argv = sys.argv[1:]
    if argv and argv[0] not in ("run", "record-phase", "-h", "--help"):
        argv = ["run", *argv]

    parser = argparse.ArgumentParser(description="Deterministic state machine for ingest-pipeline.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="Drive the pipeline forward by one transition (default).")
    run_p.add_argument("target", help="Path to a .pdf file or a book directory.")
    run_p.add_argument("--force", action="store_true")
    run_p.add_argument("--vision", choices=["auto", "never", "always"], default="auto")

    rec_p = sub.add_parser("record-phase", help="Update pipeline.json after the LLM has dispatched a subagent.")
    rec_p.add_argument("book_root")
    rec_p.add_argument("--phase", required=True, choices=["mdbook", "scaffold", "build"])
    rec_p.add_argument("--phase-index", type=int, default=None)
    rec_p.add_argument("--status", required=True, choices=["complete", "failed"])
    rec_p.add_argument("--manifest", default=None, help="Relative path to sub-skill manifest.json.")
    rec_p.add_argument("--invocation-id", default=None)
    rec_p.add_argument("--error", default=None)
    rec_p.add_argument("--working-dir", default=None, help="Update top-level working_dir (e.g., after pdf-to-mdbook).")

    args = parser.parse_args(argv)
    if args.cmd == "run":
        cmd_run(Path(args.target).resolve(), args.force, args.vision)
    elif args.cmd == "record-phase":
        cmd_record_phase(args)


if __name__ == "__main__":
    main()
