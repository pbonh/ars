# PDF Textbook Split Workflow

**Date:** 2026-04-29
**Scope:** `roles/node/defaults/main/claude.yml`, `roles/dotfiles/tasks/configure_claude_code.yml`, `roles/dotfiles/templates/claude/`, `roles/dotfiles/files/claude/`, package install lists (Brewfile, `dev_packages`)
**Branch:** `main` (no PR, no branch)

## Goal

Add a Claude-driven workflow that preprocesses a directory of PDF textbooks. Each book is split into per-section PDF slices (lossless) plus extracted markdown sidecars (searchable). Scanned PDFs are OCR'd via a sidecar `*.ocr.pdf` so the original is never modified. Everything is delivered as managed Claude assets via the existing `roles/node` deployment pattern.

The workflow is two slash commands plus one skill:

- `/split-textbooks <directory> [--force]` — batch entry, iterates over PDFs in a directory.
- `/split-textbook <path-to-pdf>` — single-book retry; implies `--force` and overwrites prior output without prompting.
- `split-textbooks` skill — the per-book recipe Claude follows for one PDF.

Claude drives every step itself via `Bash`. There are no bundled helper scripts; the recipe is composed of standard CLI tools (`pdfinfo`, `pdftotext`, `pdffonts`, `qpdf`, `ocrmypdf`).

## Non-goals

- Building an mdbook, search index, or any downstream consumer of the split output.
- Editing/cleaning the extracted markdown beyond minimal whitespace normalization (no heading inference, no table reconstruction, no figure captioning).
- Cross-book operations (no merging multi-volume sets, no global glossary).
- Watching the directory for new PDFs (one-shot batch; re-run to pick up new files).
- Automated unit tests of the recipe text. Recipe verification is fixture-based and manual.
- Updates to the `nonroot` role for tool installation.

## Design

### Output layout per book

Given input `<dir>/calculus.pdf`:

```
<dir>/
├── calculus.pdf                      (untouched original)
├── calculus.ocr.pdf                  (sidecar OCR, only if scanned)
└── calculus/                         (output subfolder, named to match)
    ├── manifest.json                 (detected sections + page ranges)
    ├── toc.pdf  +  toc.md
    ├── 00-preface.pdf  +  00-preface.md
    ├── 01-chapter-01-limits.pdf  +  01-chapter-01-limits.md
    ├── 02-chapter-02-derivatives.pdf + ...
    ├── 99-appendix-a.pdf + 99-appendix-a.md
    ├── glossary.pdf + glossary.md
    └── sources.pdf + sources.md
```

- Output subfolder lives in the same parent dir as the source PDF.
- Chapters/appendices/front-matter sections use a numeric prefix (`NN-<slug>`) for ordering.
- Special files (`toc`, `glossary`, `sources`) are unprefixed at the same level as chapters.

### Components

#### Slash command: `/split-textbooks` (batch)

**File on disk:** `~/.claude/commands/split-textbooks.md`
**Repo source:** `roles/dotfiles/files/claude/commands/split-textbooks.md`
**Argument hint:** `<directory> [--force]`
**Model:** `opus`
**Allowed tools:** `Bash,Read,Write,Glob`

Resolves the directory, enumerates `*.pdf` (excluding `*.ocr.pdf`), and for each invokes the skill recipe. Skip-if-done check happens here: read existing `<book>/manifest.json`; if `status: "complete"` and `--force` is absent, skip. Failures in one book do not abort the batch; the next book is attempted.

#### Slash command: `/split-textbook` (single-book retry)

**File on disk:** `~/.claude/commands/split-textbook.md`
**Repo source:** `roles/dotfiles/files/claude/commands/split-textbook.md`
**Argument hint:** `<path-to-pdf>`
**Model:** `opus`
**Allowed tools:** `Bash,Read,Write,Glob`

Wipes any prior `<book>/` output dir and `*.ocr.pdf` sidecar without prompting (user opted in by invoking the retry), then runs the skill recipe on the single PDF. Used when the batch produced bad output for one book.

When invoked on a book whose prior `manifest.json` had `status: "failed"` and the user has manually edited `page_offset`, the recipe respects that override (skips redetection's offset step and uses the manifest value).

#### Skill: `split-textbooks`

**File on disk:** `~/.claude/skills/split-textbooks/SKILL.md`
**Repo source:** `roles/dotfiles/files/claude/skills/split-textbooks/SKILL.md`
**Allowed tools:** `Bash,Read,Write,Edit,Glob`

The recipe Claude follows for one book. Detailed in the next section.

#### Why one skill, not three

Splitting into "ocr-pdf" + "detect-sections" + "slice-pdf" adds interface surface (each step would need a contract for the canonical-PDF-path, the page offset, the manifest in progress) without reuse. The steps are tightly coupled around shared per-book state. One skill keeps the recipe linear and the failure handling local.

### The recipe (SKILL.md content)

#### Step 0 — Environment self-check

Run once per session, not per book.

```
command -v pdfinfo pdftotext pdffonts qpdf ocrmypdf
```

If any missing, print platform-specific install hints (Homebrew for macOS; nix/devbox for Linux) and abort. Belt-and-suspenders alongside the Ansible-time installs.

#### Step 1 — Resolve canonical PDF (detect scanned vs. text-layered)

Given input `<path>/book.pdf`:

1. `pdffonts <path>/book.pdf` outputs a 2-line header followed by one row per embedded font. If only the header is present (i.e., `tail -n +3` is empty) → no embedded fonts.
2. AND `pdftotext -l 5 <path>/book.pdf -` produces empty/whitespace output (first 5 pages have no extractable text).
3. → It's a scanned PDF. Run `ocrmypdf --skip-text --output-type pdf <path>/book.pdf <path>/book.ocr.pdf`. Canonical PDF for downstream steps becomes `<path>/book.ocr.pdf`.
4. Otherwise canonical = original.

`--skip-text` makes `ocrmypdf` idempotent and safe on mixed-content PDFs.

#### Step 2 — Detect sections (cascade)

Each path produces the same output: an ordered list of `{title, start_page, kind}` entries. End pages are computed as `next.start_page - 1`; the final section ends at `pdfinfo`'s reported page count.

**2a — Bookmarks (preferred):**
- `pdfinfo -outline <canonical>` — outline tree.
- If top-level outline has ≥3 entries that look like sections (matching keywords: preface, intro, chapter, appendix, glossary, sources, bibliography, index), accept and build manifest from outline entries.

**2b — TOC text parsing (fallback):**
- Scan `pdftotext -layout -l 30 <canonical> -` for the first page containing "Contents" or "Table of Contents" as a heading.
- Continue capturing pages until the dotted-leader pattern stops.
- Parse entries with regex: `^(.+?)\s*\.{2,}\s*(\d+|[ivxlcdm]+)$`.
- Resolve **page-number offset**: locate the first chapter title in the body, compute delta between printed page number and PDF page index, apply globally.

**2c — LLM fallback (last resort):**
- Extract first 30 pages: `pdftotext -l 30 <canonical> -`.
- Claude reads the front matter and emits the section list as JSON.
- Same offset resolution as 2b.

**Section-kind classification** (heuristic on title, applied in all three paths):

| Pattern (case-insensitive) | `kind` |
|---|---|
| `^(preface\|foreword\|introduction\|prologue\|acknowledgments\|table of contents\|contents)` | `front_matter` |
| `^(chapter\b\|^\d+\b\|^part\b\|^lesson\b\|^unit\b)` | `chapter` |
| `^(appendix\b\|appendix [a-z\d]+)` | `appendix` |
| `^(glossary\|bibliography\|references\|sources\|index\|about the author\|colophon)` | `back_matter` |
| (no match) | `chapter` (default) |

#### Step 3 — Slice

For each section:

```
qpdf --empty --pages <canonical> <start>-<end> -- <out>/<filename>.pdf
```

Filename rules:
- Chapters / appendices / front-matter sections (other than `toc`): `NN-<slug>.pdf` (numeric prefix preserves order; slug is lowercased title with non-alphanumeric runs collapsed to `-`).
- Special files: `toc.pdf`, `glossary.pdf`, `sources.pdf`, `index.pdf`, `bibliography.pdf` — unprefixed.
- `toc` slice uses the page range detected in step 2b (or the outline's "Contents" entry range in 2a).

#### Step 4 — Extract markdown

For each sliced PDF:

```
pdftotext -layout <slice>.pdf - | <minimal cleanup> > <slice>.md
```

Minimal cleanup: collapse 3+ blank lines to 2, strip form-feed (`\f`) characters. Nothing more. Raw extracted text is the contract — for OCR'd books, quality is whatever Tesseract produced.

#### Step 5 — Write manifest, mark complete

Write `<book>/manifest.json` (schema below) with `status: "complete"`. This is the marker `--force`-less reruns check.

#### Failure handling

Any step failure → write `manifest.json` with `status: "failed"`, populate `failed_step` and `error_message`. The batch command continues to the next book. The user retries one book at a time via `/split-textbook`.

### Manifest schema

`<book>/manifest.json` — single source of truth per book. Inline-documented in SKILL.md; not a separate JSON Schema file.

```json
{
  "schema_version": 1,
  "source_pdf": "calculus.pdf",
  "canonical_pdf": "calculus.ocr.pdf",
  "is_scanned": true,
  "page_count": 612,
  "page_offset": 12,
  "detection_method": "bookmarks",
  "status": "complete",
  "generated_at": "2026-04-29T14:33:00Z",
  "tool_versions": {
    "ocrmypdf": "16.10.4",
    "qpdf": "11.9.0",
    "pdftotext": "24.08.0"
  },
  "sections": [
    {
      "index": 0,
      "kind": "front_matter",
      "title": "Table of Contents",
      "slug": "toc",
      "filename": "toc",
      "start_page": 5,
      "end_page": 11
    },
    {
      "index": 1,
      "kind": "chapter",
      "title": "Chapter 1: Limits",
      "slug": "chapter-01-limits",
      "filename": "01-chapter-01-limits",
      "start_page": 19,
      "end_page": 56
    }
  ],
  "failed_step": null,
  "error_message": null
}
```

**Field notes:**

- `canonical_pdf` — file actually used for slicing (`*.ocr.pdf` if scanned, else same as `source_pdf`). Lets the user trace which file produced the slices.
- `page_offset` — printed-page minus PDF-page index, from step 2b/2c. `0` when outline-based detection didn't need it. Manual override path: edit the manifest, set `status: "failed"`, run `/split-textbook` — the recipe respects the edited offset.
- `kind` enum: `front_matter` | `chapter` | `appendix` | `back_matter`.
- `slug` vs `filename`: `slug` is the title-derived identifier (`chapter-01-limits`); `filename` is what's on disk (`01-chapter-01-limits` with prefix, or unprefixed for special files).
- `tool_versions` — captured at run time. Useful for diagnosing reproducibility issues.
- `detection_method` — one of `bookmarks` | `toc_parse` | `llm`.
- `failed_step` enum (only when `status: "failed"`): `detect_outline` | `detect_llm` | `ocr` | `slice` | `extract`.

### Ansible plumbing

#### Schema extension: `content_file` for skills, agents, commands

The PDF skill body is too large to inline in YAML. Extend all three templates to accept either `content` (inline string) or `content_file` (path under `roles/dotfiles/files/`, mutually exclusive). Use `lookup('file', role_path ~ '/files/' ~ entry.content_file)` in the template.

Affected templates:

- `roles/dotfiles/templates/claude/SKILL.md.j2` — add `content_file` support.
- `roles/dotfiles/templates/claude/agent.md.j2` — add `content_file` support (for symmetry; not used by this workflow).
- `roles/dotfiles/templates/claude/command.md.j2` — **new**, supports `content` and `content_file` from the start.

#### New template: `command.md.j2`

```jinja
---
{% if command.description is defined %}
description: {{ command.description }}
{% endif %}
{% if command.allowed_tools is defined %}
allowed-tools: {{ command.allowed_tools }}
{% endif %}
{% if command.argument_hint is defined %}
argument-hint: {{ command.argument_hint }}
{% endif %}
{% if command.model is defined %}
model: {{ command.model }}
{% endif %}
---
{{ command.content if command.content is defined else lookup('file', role_path ~ '/files/' ~ command.content_file) }}
```

#### New tasks in `configure_claude_code.yml`

Append after the existing skills/agents block, mirroring the same pattern:

```yaml
- name: Claude | Ensure commands directory exists
  ansible.builtin.file:
    path: "{{ claude_commands_dir }}"
    state: directory
    mode: "0755"
  when: claude_commands | length > 0

- name: Claude | Template command files
  ansible.builtin.template:
    src: "claude/command.md.j2"
    dest: "{{ claude_commands_dir }}/{{ command.name }}.md"
    mode: "0644"
  loop: "{{ claude_commands }}"
  loop_control:
    loop_var: command
```

#### Defaults additions

`roles/node/defaults/main/claude.yml`:

```yaml
claude_commands_dir: "{{ claude_config_dir }}/commands"

# claude_commands:
#   - name: "review"
#     description: "Review the working tree"
#     allowed_tools: "Bash,Read,Grep"
#     argument_hint: "[--scope=staged]"
#     model: "opus"
#     content_file: "claude/commands/review.md"
claude_commands: []
```

Concrete entries for this workflow (added to the same file):

```yaml
claude_skills:
  - name: "split-textbooks"
    description: "Split a PDF textbook into per-section PDF slices and extracted markdown."
    allowed_tools: "Bash,Read,Write,Edit,Glob"
    content_file: "claude/skills/split-textbooks/SKILL.md"

claude_commands:
  - name: "split-textbooks"
    description: "Batch-process a directory of PDF textbooks"
    allowed_tools: "Bash,Read,Write,Glob"
    argument_hint: "<directory> [--force]"
    model: "opus"
    content_file: "claude/commands/split-textbooks.md"
  - name: "split-textbook"
    description: "Reprocess a single PDF textbook (overwrites prior output)"
    allowed_tools: "Bash,Read,Write,Glob"
    argument_hint: "<path-to-pdf>"
    model: "opus"
    content_file: "claude/commands/split-textbook.md"
```

#### Repo file layout

```
roles/dotfiles/
├── templates/claude/
│   ├── SKILL.md.j2                       (modified: content_file support)
│   ├── agent.md.j2                       (modified: content_file support)
│   └── command.md.j2                     (new)
├── tasks/configure_claude_code.yml       (modified: append commands block)
└── files/claude/
    ├── skills/split-textbooks/
    │   ├── SKILL.md                      (the recipe from "The recipe" section)
    │   └── fixtures/
    │       ├── README.md
    │       ├── outline-text.pdf          (small text PDF with embedded outline)
    │       ├── toc-text.pdf              (small text PDF, no outline)
    │       └── scanned.pdf               (small scanned PDF)
    └── commands/
        ├── split-textbooks.md            (short batch entry, dispatches to skill)
        └── split-textbook.md             (short retry entry, dispatches to skill)
```

#### Package install changes

Tools needed: `poppler-utils` (provides `pdfinfo`, `pdftotext`, `pdffonts`), `qpdf`, `ocrmypdf` (pulls `tesseract` and `ghostscript` as transitive deps).

- **Homebrew:** add `poppler`, `qpdf`, `ocrmypdf` to the Brewfile (location to be confirmed during implementation — likely `roles/homebrew/templates/Brewfile.j2` or `files/Brewfile`).
- **`dev_packages`** in `group_vars/all.yml`: add `poppler`, `qpdf`, `ocrmypdf` (exact nix attribute names confirmed during implementation).
- **`nonroot`:** no change (per scope).

The runtime self-check in step 0 covers cases where the role has not been re-run after the package additions.

### Failure modes

| Failure | Detected at | Behavior |
|---|---|---|
| Required tool missing | Step 0 self-check | Print install instructions for the OS, abort the run. No partial work. |
| Source PDF corrupt / not a PDF | `pdfinfo` non-zero | Skip book; manifest with `failed_step: "detect_outline"`; continue batch. |
| OCR pass fails | `ocrmypdf` non-zero | `failed_step: "ocr"`. Sanity-check `*.ocr.pdf` size > 0; if zero/missing, delete it. |
| All three detection methods fail | After 2c | `failed_step: "detect_llm"`. Manifest has `sections: []`; `error_message` includes the front-matter text dump for diagnosis. |
| Page-offset wrong → slices misaligned | User notices on review | Manifest reports `status: "complete"` (recipe can't catch this). User edits `manifest.json` (`page_offset`, `status: "failed"`) and runs `/split-textbook <pdf>`. |
| `qpdf` slice fails for one section | During slicing loop | `failed_step: "slice"`; offending section index in `error_message`; partial slices removed. |
| Disk full mid-extraction | `pdftotext` non-zero | `failed_step: "extract"`. Slices retained; markdown sidecars partial. Manifest reflects partial state. |

**Guiding principle:** every failure is recorded in `manifest.json`; the batch never aborts; the user has one command (`/split-textbook`) to retry one book at a time.

### Testing

#### Ansible role tests

Extend tests under `roles/dotfiles/tests/` (or add minimal `ansible-playbook --check` if Molecule isn't wired up here). Coverage:

- `claude_commands` end-to-end with both `content` (inline) and `content_file` paths.
- The same dual-path support applied to `claude_skills` and `claude_agents` (regression coverage for the template extensions).
- Verify rendered files land at `~/.claude/{commands,skills,agents}/...` with correct frontmatter.

#### Recipe smoke fixtures

Three small PDFs committed to `roles/dotfiles/files/claude/skills/split-textbooks/fixtures/`:

- `outline-text.pdf` — ~20 pages, embedded outline → exercises path 2a.
- `toc-text.pdf` — ~20 pages, TOC but no outline → exercises 2b.
- `scanned.pdf` — a few image pages, no text layer → exercises OCR + 2b/2c.

Documented in `fixtures/README.md` with expected manifest contents per fixture. Not run by CI; used for manual verification when the recipe changes.

#### End-to-end manual test (documented in spec)

1. Provision a fresh box via the `node` + `dotfiles` roles.
2. Copy fixtures to a scratch directory.
3. Run `/split-textbooks <scratch>` from Claude Code.
4. Verify each fixture produces the expected `manifest.json` and slice count.
5. Run `/split-textbook` on a deliberately-broken fixture (truncated PDF) → verify failure path writes `status: "failed"` with a populated `failed_step`.

Automated unit tests of the recipe text are explicitly out of scope — the recipe is a Markdown document, not code. The plumbing tests cover repeatable bugs; the fixtures cover PDF-specific quirks where bugs are not anticipatable in advance.

## Implementation order (non-binding hint)

A reasonable sequence (the implementation plan will refine this):

1. Extend `SKILL.md.j2` and `agent.md.j2` to support `content_file`. Add a regression test covering both forms.
2. Add `command.md.j2` template, `claude_commands` defaults entry, `claude_commands_dir` var, and command-templating tasks in `configure_claude_code.yml`. Test with an inline-content stub.
3. Write the SKILL.md recipe body to `roles/dotfiles/files/claude/skills/split-textbooks/SKILL.md`.
4. Write the two short slash-command bodies to `roles/dotfiles/files/claude/commands/`.
5. Wire the three concrete entries into `roles/node/defaults/main/claude.yml`.
6. Add packages to Brewfile and `dev_packages`.
7. Add fixtures + `fixtures/README.md`.
8. Manual end-to-end run on the fixtures; iterate on the recipe until the three paths produce expected output.
