# PDF Textbook Split Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Claude-driven workflow (two slash commands + one skill) that preprocesses a directory of PDF textbooks, splitting each book into per-section PDF slices and markdown sidecars, with sidecar OCR for scanned PDFs.

**Architecture:** The workflow ships as managed Claude assets via the existing `dotfiles` role deployment pattern. The recipe is one skill (`split-textbooks`) Claude executes via `Bash`, composing standard CLI tools (`pdfinfo`, `pdftotext`, `pdffonts`, `qpdf`, `ocrmypdf`). Two slash commands dispatch to it: `/split-textbooks` (batch) and `/split-textbook` (single-book retry). To keep the recipe out of YAML, the existing `SKILL.md.j2` and `agent.md.j2` templates are extended to accept either `content` (inline) or `content_file` (path under `roles/dotfiles/files/`); a new `command.md.j2` template adds the same dual-path support for slash commands.

**Tech Stack:** Ansible (`dotfiles` and `node` roles), Jinja2 templates, `lookup('file', ...)`, Markdown, Homebrew/devbox for tool installation.

**Reference spec:** `docs/superpowers/specs/2026-04-29-pdf-textbook-split-workflow-design.md`

---

## File Structure

**Modified files:**

- `roles/dotfiles/templates/claude/SKILL.md.j2` — switch body line to `content` / `content_file` lookup.
- `roles/dotfiles/templates/claude/agent.md.j2` — same dual-path body line (regression symmetry).
- `roles/dotfiles/tasks/configure_claude_code.yml` — append `claude_commands` directory + template loop after the existing skills/agents blocks.
- `roles/dotfiles/defaults/main/claude.yml` — add `claude_commands_dir` and empty `claude_commands: []` default.
- `roles/node/defaults/main/claude.yml` — add `claude_commands_dir`, empty default, and the concrete `claude_skills` + `claude_commands` entries for this workflow.
- `group_vars/all.yml` — add `poppler`, `qpdf`, `ocrmypdf` entries to `dev_packages`.

**New files:**

- `roles/dotfiles/templates/claude/command.md.j2` — template for slash commands, supports `content` / `content_file` from the start.
- `roles/dotfiles/files/claude/skills/split-textbooks/SKILL.md` — the recipe Claude follows for one book.
- `roles/dotfiles/files/claude/commands/split-textbooks.md` — batch entry, dispatches to skill.
- `roles/dotfiles/files/claude/commands/split-textbook.md` — single-book retry entry, dispatches to skill.
- `roles/dotfiles/files/claude/skills/split-textbooks/fixtures/README.md` — describes the three smoke fixtures.
- `roles/dotfiles/files/claude/skills/split-textbooks/fixtures/outline-text.pdf` — exercises detection path 2a.
- `roles/dotfiles/files/claude/skills/split-textbooks/fixtures/toc-text.pdf` — exercises detection path 2b.
- `roles/dotfiles/files/claude/skills/split-textbooks/fixtures/scanned.pdf` — exercises OCR + 2b/2c.

**Unchanged but referenced:**

- `roles/dotfiles/tests/test.yml` — repo's existing minimal test playbook; we will run it with `--check` mode and overridden vars to smoke-test rendering.
- `roles/homebrew/templates/Brewfile.j2` — reads `dev_packages.*.brew` automatically; no edit needed once `dev_packages` is updated.

---

## Notes on the codebase that the engineer will need

- Defaults for the same `claude_*` variables live in BOTH `roles/dotfiles/defaults/main/claude.yml` (the role's own fallback) AND `roles/node/defaults/main/claude.yml` (the node-role copy that ships the concrete workflow entries). The `dotfiles` role is what actually runs the templating tasks, so its defaults must define the variable as an empty list. The `node` role overrides the empty default with the real workflow entries.
- Ansible's `lookup('file', path)` reads files relative to the role calling it. Inside a Jinja2 template, `role_path` resolves to the role currently invoking the template — that's the `dotfiles` role here. So `lookup('file', role_path ~ '/files/' ~ entry.content_file)` reads from `roles/dotfiles/files/<content_file>`.
- The `Brewfile.j2` template auto-includes anything in `dev_packages.<name>.brew`, so adding entries to `dev_packages` in `group_vars/all.yml` is sufficient for Homebrew. `devbox` entries cover the Linux-via-nix path (the spec's "`dev_packages` in `group_vars/all.yml`").
- The repo's `tests/` folders are minimal (no Molecule); use `ansible-playbook --syntax-check` and `ansible-playbook --check` with extra-vars to smoke-test changes.
- Use Bash heredocs to write multi-line file content. Trying to author the SKILL.md inline in a YAML literal would defeat the purpose of `content_file`.

---

## Task 1: Extend SKILL.md.j2 to accept `content_file`

**Purpose:** Allow large skill bodies to live as a sibling Markdown file under `roles/dotfiles/files/claude/skills/...` instead of being inlined in YAML. The existing `content` form must keep working — every existing skill in the wild uses `content`.

**Files:**
- Modify: `roles/dotfiles/templates/claude/SKILL.md.j2` (replace the body line)

- [ ] **Step 1: Read the current template to confirm starting state**

Run: `cat roles/dotfiles/templates/claude/SKILL.md.j2`

Expected output (12 lines):

```jinja
---
{% if skill.description is defined %}
description: {{ skill.description }}
{% endif %}
{% if skill.allowed_tools is defined %}
allowed-tools: {{ skill.allowed_tools }}
{% endif %}
{% if skill.disable_model_invocation is defined %}
disable-model-invocation: {{ skill.disable_model_invocation | lower }}
{% endif %}
---
{{ skill.content }}
```

- [ ] **Step 2: Replace the body line with dual-path lookup**

Edit `roles/dotfiles/templates/claude/SKILL.md.j2` — change the final line from:

```jinja
{{ skill.content }}
```

to:

```jinja
{{ skill.content if skill.content is defined else lookup('file', role_path ~ '/files/' ~ skill.content_file) }}
```

After editing, the file should be:

```jinja
---
{% if skill.description is defined %}
description: {{ skill.description }}
{% endif %}
{% if skill.allowed_tools is defined %}
allowed-tools: {{ skill.allowed_tools }}
{% endif %}
{% if skill.disable_model_invocation is defined %}
disable-model-invocation: {{ skill.disable_model_invocation | lower }}
{% endif %}
---
{{ skill.content if skill.content is defined else lookup('file', role_path ~ '/files/' ~ skill.content_file) }}
```

- [ ] **Step 3: Syntax-check the dotfiles role**

Run:

```bash
ansible-playbook -i roles/dotfiles/tests/inventory roles/dotfiles/tests/test.yml --syntax-check
```

Expected: `playbook: roles/dotfiles/tests/test.yml` with no errors.

- [ ] **Step 4: Render-test with an inline-content skill (regression check)**

Create a temporary fixture file, then dry-render with `--check` mode and confirm the SKILL.md would be created.

Run:

```bash
mkdir -p /tmp/ars-test && cd /tmp/ars-test && cp -r /var/home/phillip/Boxes/Homes/DotDev/Code/github.com/pbonh/ars/roles . && cp /var/home/phillip/Boxes/Homes/DotDev/Code/github.com/pbonh/ars/roles/dotfiles/tests/test.yml ./test.yml
```

Then create `/tmp/ars-test/extra-vars.yml`:

```yaml
claude_skills:
  - name: "smoke-inline"
    description: "Inline-content smoke skill"
    allowed_tools: "Read"
    content: |
      This is an inline skill body for regression testing.
```

Run:

```bash
cd /tmp/ars-test && ansible-playbook -i roles/dotfiles/tests/inventory test.yml \
  --extra-vars "@extra-vars.yml" \
  --tags claude --check --diff 2>&1 | tail -40
```

Expected: `Template SKILL.md files` task shows a diff including `description: Inline-content smoke skill` and the body line. No errors.

- [ ] **Step 5: Render-test with a `content_file` skill (new path)**

Create a fixture file:

```bash
mkdir -p /tmp/ars-test/roles/dotfiles/files/claude/skills/smoke-file
cat > /tmp/ars-test/roles/dotfiles/files/claude/skills/smoke-file/SKILL.md <<'EOF'
This is a file-backed skill body for the new content_file path.
EOF
```

Replace `/tmp/ars-test/extra-vars.yml`:

```yaml
claude_skills:
  - name: "smoke-file"
    description: "File-backed smoke skill"
    allowed_tools: "Read"
    content_file: "claude/skills/smoke-file/SKILL.md"
```

Run:

```bash
cd /tmp/ars-test && ansible-playbook -i roles/dotfiles/tests/inventory test.yml \
  --extra-vars "@extra-vars.yml" \
  --tags claude --check --diff 2>&1 | tail -40
```

Expected: diff shows `description: File-backed smoke skill` and the body `This is a file-backed skill body for the new content_file path.`

- [ ] **Step 6: Clean up the scratch directory**

Run: `rm -rf /tmp/ars-test`

- [ ] **Step 7: Commit**

```bash
git add roles/dotfiles/templates/claude/SKILL.md.j2
git commit -m "[Claude] SKILL.md.j2: accept content_file alongside content"
```

---

## Task 2: Extend agent.md.j2 to accept `content_file`

**Purpose:** Symmetric extension for agents. Not used by this workflow, but keeping the templates aligned avoids surprise when someone later adds a large agent prompt.

**Files:**
- Modify: `roles/dotfiles/templates/claude/agent.md.j2` (replace the body line)

- [ ] **Step 1: Read the current template**

Run: `cat roles/dotfiles/templates/claude/agent.md.j2`

Expected: 31 lines, ending with `{{ agent.content }}`.

- [ ] **Step 2: Replace the body line**

Edit `roles/dotfiles/templates/claude/agent.md.j2` — change the final line from:

```jinja
{{ agent.content }}
```

to:

```jinja
{{ agent.content if agent.content is defined else lookup('file', role_path ~ '/files/' ~ agent.content_file) }}
```

- [ ] **Step 3: Syntax-check**

Run:

```bash
ansible-playbook -i roles/dotfiles/tests/inventory roles/dotfiles/tests/test.yml --syntax-check
```

Expected: no errors.

- [ ] **Step 4: Render-test with an inline-content agent (regression)**

Set up scratch and an agent fixture:

```bash
mkdir -p /tmp/ars-test && cd /tmp/ars-test && cp -r /var/home/phillip/Boxes/Homes/DotDev/Code/github.com/pbonh/ars/roles . && cp /var/home/phillip/Boxes/Homes/DotDev/Code/github.com/pbonh/ars/roles/dotfiles/tests/test.yml ./test.yml
```

Create `/tmp/ars-test/extra-vars.yml`:

```yaml
claude_agents:
  - name: "smoke-inline-agent"
    description: "Inline agent regression"
    tools: "Read"
    content: |
      Inline agent body.
```

Run:

```bash
cd /tmp/ars-test && ansible-playbook -i roles/dotfiles/tests/inventory test.yml \
  --extra-vars "@extra-vars.yml" \
  --tags claude --check --diff 2>&1 | tail -40
```

Expected: `Template agent files` task shows a diff including `Inline agent body.`

- [ ] **Step 5: Render-test with a `content_file` agent**

```bash
mkdir -p /tmp/ars-test/roles/dotfiles/files/claude/agents
cat > /tmp/ars-test/roles/dotfiles/files/claude/agents/smoke-file-agent.md <<'EOF'
File-backed agent body for content_file regression.
EOF
```

Replace `/tmp/ars-test/extra-vars.yml`:

```yaml
claude_agents:
  - name: "smoke-file-agent"
    description: "File-backed agent regression"
    tools: "Read"
    content_file: "claude/agents/smoke-file-agent.md"
```

Run:

```bash
cd /tmp/ars-test && ansible-playbook -i roles/dotfiles/tests/inventory test.yml \
  --extra-vars "@extra-vars.yml" \
  --tags claude --check --diff 2>&1 | tail -40
```

Expected: diff shows the file-backed agent body.

- [ ] **Step 6: Clean up**

Run: `rm -rf /tmp/ars-test`

- [ ] **Step 7: Commit**

```bash
git add roles/dotfiles/templates/claude/agent.md.j2
git commit -m "[Claude] agent.md.j2: accept content_file alongside content"
```

---

## Task 3: Add `command.md.j2` template + defaults

**Purpose:** Slash commands are not yet supported by this role. Add the new template and the `claude_commands_dir` / `claude_commands: []` defaults. The template supports `content` and `content_file` from the start.

**Files:**
- Create: `roles/dotfiles/templates/claude/command.md.j2`
- Modify: `roles/dotfiles/defaults/main/claude.yml`
- Modify: `roles/node/defaults/main/claude.yml`

- [ ] **Step 1: Create the template**

Write `roles/dotfiles/templates/claude/command.md.j2` with this content:

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

- [ ] **Step 2: Add `claude_commands_dir` + empty default to dotfiles role**

Edit `roles/dotfiles/defaults/main/claude.yml`. After line 7 (`claude_agents_dir: ...`), insert:

```yaml
claude_commands_dir: "{{ claude_config_dir }}/commands"
```

At the end of the file (after the `claude_voltagent_agents: []` line), append:

```yaml

# claude_commands:
#   - name: "review"
#     description: "Review the working tree"
#     allowed_tools: "Bash,Read,Grep"
#     argument_hint: "[--scope=staged]"
#     model: "opus"
#     content_file: "claude/commands/review.md"
claude_commands: []
```

- [ ] **Step 3: Add the same `claude_commands_dir` + empty default to node role**

Edit `roles/node/defaults/main/claude.yml`. After line 7 (`claude_agents_dir: ...`), insert:

```yaml
claude_commands_dir: "{{ claude_config_dir }}/commands"
```

At the end of the file (after `claude_voltagent_agents: []`), append:

```yaml

# claude_commands:
#   - name: "review"
#     description: "Review the working tree"
#     allowed_tools: "Bash,Read,Grep"
#     argument_hint: "[--scope=staged]"
#     model: "opus"
#     content_file: "claude/commands/review.md"
claude_commands: []
```

- [ ] **Step 4: Syntax-check**

Run:

```bash
ansible-playbook -i roles/dotfiles/tests/inventory roles/dotfiles/tests/test.yml --syntax-check
```

Expected: no errors.

- [ ] **Step 5: Commit**

```bash
git add roles/dotfiles/templates/claude/command.md.j2 \
        roles/dotfiles/defaults/main/claude.yml \
        roles/node/defaults/main/claude.yml
git commit -m "[Claude] Add command.md.j2 template and claude_commands defaults"
```

---

## Task 4: Add `claude_commands` tasks block

**Purpose:** Wire the new template into the role so `claude_commands` entries are deployed to `~/.claude/commands/`.

**Files:**
- Modify: `roles/dotfiles/tasks/configure_claude_code.yml` (append after the existing voltagent block)

- [ ] **Step 1: Read the end of the current tasks file**

Run: `tail -15 roles/dotfiles/tasks/configure_claude_code.yml`

Expected: file ends at the `claude_voltagent_agents` `get_url` block (line ~95).

- [ ] **Step 2: Append the commands block**

Edit `roles/dotfiles/tasks/configure_claude_code.yml`. Append at the end of the file (after the last existing task):

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

- [ ] **Step 3: Syntax-check**

Run:

```bash
ansible-playbook -i roles/dotfiles/tests/inventory roles/dotfiles/tests/test.yml --syntax-check
```

Expected: no errors.

- [ ] **Step 4: Render-test with an inline-content command**

Set up scratch:

```bash
mkdir -p /tmp/ars-test && cd /tmp/ars-test && cp -r /var/home/phillip/Boxes/Homes/DotDev/Code/github.com/pbonh/ars/roles . && cp /var/home/phillip/Boxes/Homes/DotDev/Code/github.com/pbonh/ars/roles/dotfiles/tests/test.yml ./test.yml
```

Create `/tmp/ars-test/extra-vars.yml`:

```yaml
claude_commands:
  - name: "smoke-inline-cmd"
    description: "Inline command smoke"
    allowed_tools: "Bash"
    argument_hint: "<args>"
    model: "opus"
    content: |
      Inline command body.
```

Run:

```bash
cd /tmp/ars-test && ansible-playbook -i roles/dotfiles/tests/inventory test.yml \
  --extra-vars "@extra-vars.yml" \
  --tags claude --check --diff 2>&1 | tail -50
```

Expected: `Ensure commands directory exists` and `Template command files` tasks both run; diff shows frontmatter with `description`, `allowed-tools`, `argument-hint`, `model` and the inline body.

- [ ] **Step 5: Render-test with a `content_file` command**

```bash
mkdir -p /tmp/ars-test/roles/dotfiles/files/claude/commands
cat > /tmp/ars-test/roles/dotfiles/files/claude/commands/smoke-file-cmd.md <<'EOF'
File-backed command body.
EOF
```

Replace `/tmp/ars-test/extra-vars.yml`:

```yaml
claude_commands:
  - name: "smoke-file-cmd"
    description: "File-backed command smoke"
    allowed_tools: "Bash"
    argument_hint: "<args>"
    model: "opus"
    content_file: "claude/commands/smoke-file-cmd.md"
```

Run:

```bash
cd /tmp/ars-test && ansible-playbook -i roles/dotfiles/tests/inventory test.yml \
  --extra-vars "@extra-vars.yml" \
  --tags claude --check --diff 2>&1 | tail -50
```

Expected: diff shows the file-backed command body.

- [ ] **Step 6: Clean up**

Run: `rm -rf /tmp/ars-test`

- [ ] **Step 7: Commit**

```bash
git add roles/dotfiles/tasks/configure_claude_code.yml
git commit -m "[Claude] Deploy claude_commands to ~/.claude/commands/"
```

---

## Task 5: Write the SKILL.md recipe

**Purpose:** Author the per-book recipe Claude follows for one PDF. This is a Markdown document, not code — its contract is the prose Claude reads.

**Files:**
- Create: `roles/dotfiles/files/claude/skills/split-textbooks/SKILL.md`

- [ ] **Step 1: Create the directory**

Run:

```bash
mkdir -p roles/dotfiles/files/claude/skills/split-textbooks
```

Expected: directory exists, no error.

- [ ] **Step 2: Write the SKILL.md recipe**

Create `roles/dotfiles/files/claude/skills/split-textbooks/SKILL.md` with this content:

````markdown
# split-textbooks

You are processing a single PDF textbook. The slash command driving you (`/split-textbooks` or `/split-textbook`) supplies the absolute path to one PDF and tells you whether to overwrite an existing output directory.

## Output layout

Given input `<dir>/book.pdf`:

```
<dir>/
├── book.pdf                       (untouched original)
├── book.ocr.pdf                   (sidecar OCR — only if scanned)
└── book/                          (output subfolder, name matches stem)
    ├── manifest.json
    ├── toc.pdf  +  toc.md
    ├── 00-preface.pdf  +  00-preface.md
    ├── 01-chapter-01-limits.pdf  +  01-chapter-01-limits.md
    ├── ...
    ├── glossary.pdf  +  glossary.md
    └── sources.pdf  +  sources.md
```

- Chapters / appendices / front-matter use a numeric prefix `NN-<slug>` for order.
- Special files (`toc`, `glossary`, `sources`, `index`, `bibliography`) are unprefixed.

## Step 0 — Environment self-check (once per session)

Run:

```bash
command -v pdfinfo pdftotext pdffonts qpdf ocrmypdf
```

If any are missing, print install hints and abort:

- macOS (Homebrew): `brew install poppler qpdf ocrmypdf`
- Linux (devbox/nix): `devbox add poppler qpdf ocrmypdf`

Re-run the relevant Ansible role (`just homebrew` or `just devbox`) afterwards.

## Step 1 — Resolve canonical PDF (scanned vs. text-layered)

Given input `<path>/book.pdf`:

1. Run `pdffonts <path>/book.pdf | tail -n +3` — output past the 2-line header. Empty → no embedded fonts.
2. AND `pdftotext -l 5 <path>/book.pdf -` produces empty/whitespace-only output (no extractable text in first 5 pages).
3. → Scanned PDF. Run:

   ```bash
   ocrmypdf --skip-text --output-type pdf <path>/book.pdf <path>/book.ocr.pdf
   ```

   Canonical PDF for downstream steps is `<path>/book.ocr.pdf`. Set `is_scanned: true` in the manifest.
4. Otherwise canonical = original. Set `is_scanned: false`.

`--skip-text` makes `ocrmypdf` idempotent on mixed-content PDFs.

## Step 2 — Detect sections (cascade)

Each path produces an ordered list of `{title, start_page, kind}`. End pages are computed as `next.start_page - 1`; the final section ends at `pdfinfo`'s reported page count.

### 2a — Bookmarks (preferred)

```bash
pdfinfo -outline <canonical>
```

If the top-level outline has at least 3 entries that look like sections (matching: preface, intro, chapter, appendix, glossary, sources, bibliography, index — case-insensitive), accept and build the manifest from outline entries. Set `detection_method: "bookmarks"`.

### 2b — TOC text parsing (fallback)

```bash
pdftotext -layout -l 30 <canonical> -
```

Find the first page containing "Contents" or "Table of Contents" as a heading. Continue capturing pages until the dotted-leader pattern stops.

Parse entries with regex:

```
^(.+?)\s*\.{2,}\s*(\d+|[ivxlcdm]+)$
```

Resolve **page-number offset**: locate the first chapter title in the body text, compute the delta between the printed page number and the PDF page index, apply globally. Set `detection_method: "toc_parse"`.

### 2c — LLM fallback (last resort)

```bash
pdftotext -l 30 <canonical> -
```

Read the front matter and emit the section list as JSON yourself. Resolve offset the same way as 2b. Set `detection_method: "llm"`.

### Section-kind classification

Apply to each title (case-insensitive):

| Pattern                                                                                                          | `kind`         |
|------------------------------------------------------------------------------------------------------------------|----------------|
| `^(preface|foreword|introduction|prologue|acknowledgments|table of contents|contents)`                           | `front_matter` |
| `^(chapter\b|^\d+\b|^part\b|^lesson\b|^unit\b)`                                                                  | `chapter`      |
| `^(appendix\b|appendix [a-z\d]+)`                                                                                | `appendix`     |
| `^(glossary|bibliography|references|sources|index|about the author|colophon)`                                    | `back_matter` |
| (no match)                                                                                                        | `chapter`     |

## Step 3 — Slice

For each section:

```bash
qpdf --empty --pages <canonical> <start>-<end> -- <out>/<filename>.pdf
```

Filename rules:

- Chapters / appendices / front-matter (other than `toc`): `NN-<slug>.pdf` where `NN` is two-digit zero-padded section index, `<slug>` is the lowercased title with non-alphanumeric runs collapsed to `-`.
- Special files: `toc.pdf`, `glossary.pdf`, `sources.pdf`, `index.pdf`, `bibliography.pdf` — unprefixed.
- The `toc` slice uses the page range detected in 2b (or the outline's "Contents" entry range in 2a).

## Step 4 — Extract markdown

For each sliced PDF:

```bash
pdftotext -layout <slice>.pdf - | <minimal cleanup> > <slice>.md
```

Minimal cleanup only:

- Collapse runs of 3+ blank lines to 2.
- Strip form-feed (`\f`) characters.

Nothing more. The raw extracted text is the contract; for OCR'd books, quality is whatever Tesseract produced.

## Step 5 — Write manifest, mark complete

Write `<book>/manifest.json` with `status: "complete"` using the schema below. This is the marker `--force`-less batch reruns check.

### Manifest schema (single source of truth per book)

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

- `canonical_pdf` — file actually used for slicing. Same as `source_pdf` when not scanned.
- `page_offset` — printed-page minus PDF-page index. `0` when outline-based detection didn't need it.
- `kind` enum: `front_matter` | `chapter` | `appendix` | `back_matter`.
- `slug` is the title-derived identifier (`chapter-01-limits`); `filename` is what's on disk (`01-chapter-01-limits` with prefix, or unprefixed for special files).
- `tool_versions` — captured at run time. Get from `<tool> --version` output.
- `detection_method`: `bookmarks` | `toc_parse` | `llm`.
- `failed_step` (only when `status: "failed"`): `detect_outline` | `detect_toc` | `detect_llm` | `ocr` | `slice` | `extract`.

## Manual override path

If the user has manually edited `manifest.json` to set `status: "failed"` and adjusted `page_offset`, respect the edited offset — skip the offset-resolution step in 2b/2c and use the manifest value directly.

## Failure handling

Any step failure → write `manifest.json` with `status: "failed"`, populate `failed_step` and `error_message`. Do NOT abort the calling batch — `/split-textbooks` will continue to the next book. The user retries one book at a time via `/split-textbook <pdf>`.

| Failure                                | Detected at              | Behavior                                                                    |
|----------------------------------------|--------------------------|-----------------------------------------------------------------------------|
| Required tool missing                  | Step 0 self-check        | Print install instructions; abort the run. No partial work.                |
| Source PDF corrupt / not a PDF         | `pdfinfo` non-zero       | `failed_step: "detect_outline"`. Skip book; continue batch.                |
| OCR pass fails                         | `ocrmypdf` non-zero      | `failed_step: "ocr"`. If `*.ocr.pdf` is zero/missing, delete it.           |
| All three detection methods fail       | After 2c                 | `failed_step: "detect_llm"`. `sections: []`; include front-matter dump.    |
| `qpdf` slice fails for one section     | During slicing loop      | `failed_step: "slice"`; record offending index in `error_message`.         |
| `pdftotext` fails (e.g., disk full)    | During extraction        | `failed_step: "extract"`. Slices retained; markdown sidecars partial.      |

**Guiding principle:** every failure is recorded in `manifest.json`; never abort the batch; the user has one command (`/split-textbook`) to retry one book.
````

- [ ] **Step 3: Verify the file is present and parseable**

Run:

```bash
ls -la roles/dotfiles/files/claude/skills/split-textbooks/SKILL.md
wc -l roles/dotfiles/files/claude/skills/split-textbooks/SKILL.md
```

Expected: file exists, ~200 lines.

- [ ] **Step 4: Commit**

```bash
git add roles/dotfiles/files/claude/skills/split-textbooks/SKILL.md
git commit -m "[Claude] Add split-textbooks skill recipe"
```

---

## Task 6: Write the batch slash command body

**Purpose:** `/split-textbooks <directory> [--force]` enumerates PDFs and dispatches each to the skill. Skip-if-done lives here.

**Files:**
- Create: `roles/dotfiles/files/claude/commands/split-textbooks.md`

- [ ] **Step 1: Create the commands directory**

Run:

```bash
mkdir -p roles/dotfiles/files/claude/commands
```

- [ ] **Step 2: Write the command body**

Create `roles/dotfiles/files/claude/commands/split-textbooks.md` with this content:

````markdown
You are running the **batch** PDF textbook split workflow.

## Arguments

`$ARGUMENTS` is `<directory> [--force]`.

- The first non-flag argument is the directory containing PDFs.
- `--force` (optional) means re-process books whose `<book>/manifest.json` reports `status: "complete"`.

## What to do

1. Resolve the directory to an absolute path. If it doesn't exist or isn't a directory, abort with an error.
2. Enumerate `*.pdf` in the directory, **excluding** `*.ocr.pdf` sidecars. Use:

   ```bash
   find <abs-dir> -maxdepth 1 -type f -name '*.pdf' ! -name '*.ocr.pdf' | sort
   ```

3. For each PDF:
   - Compute `<book> = <dirname>/<stem>` (output dir alongside the PDF).
   - **Skip-if-done check:** if `--force` is absent and `<book>/manifest.json` exists with `"status": "complete"`, log "skip: already complete" and continue.
   - Otherwise, dispatch to the **`split-textbooks`** skill with the path to this PDF. The skill writes its own manifest and handles its own failures.
   - If the skill reports a failure, log it and continue to the next PDF. **Do not abort the batch.**
4. After all PDFs are processed, print a summary:
   - Number processed, number skipped, number failed.
   - For each failed book, name the `failed_step` from its manifest.

## Constraints

- Run the Step 0 environment self-check from the skill once at the start of the batch (not per book).
- Never modify the original `*.pdf` files.
- Never delete a `*.ocr.pdf` sidecar except per the skill's failure rules.
````

- [ ] **Step 3: Verify**

Run: `ls -la roles/dotfiles/files/claude/commands/split-textbooks.md`

Expected: file exists.

- [ ] **Step 4: Commit**

```bash
git add roles/dotfiles/files/claude/commands/split-textbooks.md
git commit -m "[Claude] Add /split-textbooks batch command"
```

---

## Task 7: Write the single-book retry slash command body

**Purpose:** `/split-textbook <path-to-pdf>` overwrites prior output for one book without prompting.

**Files:**
- Create: `roles/dotfiles/files/claude/commands/split-textbook.md`

- [ ] **Step 1: Write the command body**

Create `roles/dotfiles/files/claude/commands/split-textbook.md` with this content:

````markdown
You are running the **single-book retry** of the PDF textbook split workflow.

## Arguments

`$ARGUMENTS` is `<path-to-pdf>`.

The user opted in to overwrite by invoking the retry, so do **not** prompt before deleting prior output.

## What to do

1. Resolve the path to an absolute path. If it doesn't exist or isn't a file ending in `.pdf` (and is not a `*.ocr.pdf` sidecar), abort with an error.
2. Compute `<book> = <dirname>/<stem>`. Inspect any existing `<book>/manifest.json`:
   - If `status: "failed"` and the user has manually edited `page_offset`, **preserve that offset** for the recipe (the skill respects manifest overrides per its "Manual override path" section).
   - Otherwise, delete the entire `<book>/` directory and the `<dirname>/<stem>.ocr.pdf` sidecar (if present) before running.
3. Run the Step 0 environment self-check from the **`split-textbooks`** skill.
4. Dispatch to the `split-textbooks` skill on this single PDF.
5. Print the resulting manifest's `status` and (if failed) `failed_step` + `error_message`.

## Constraints

- Single-book scope only: never iterate over a directory.
- The override-preserving branch (step 2) is the one path that does NOT wipe prior state. Everything else is a fresh run.
````

- [ ] **Step 2: Verify**

Run: `ls -la roles/dotfiles/files/claude/commands/split-textbook.md`

Expected: file exists.

- [ ] **Step 3: Commit**

```bash
git add roles/dotfiles/files/claude/commands/split-textbook.md
git commit -m "[Claude] Add /split-textbook retry command"
```

---

## Task 8: Wire concrete entries into the node role defaults

**Purpose:** Register the skill and two commands so the role actually deploys them.

**Files:**
- Modify: `roles/node/defaults/main/claude.yml`

- [ ] **Step 1: Read the current state**

Run: `cat roles/node/defaults/main/claude.yml`

Expected: file ends with `claude_voltagent_agents: []` (and the `claude_commands_dir` + empty `claude_commands: []` added in Task 3).

- [ ] **Step 2: Replace the empty `claude_skills: []` line with the workflow entry**

Edit `roles/node/defaults/main/claude.yml`. Find:

```yaml
claude_skills: []
```

Replace with:

```yaml
claude_skills:
  - name: "split-textbooks"
    description: "Split a PDF textbook into per-section PDF slices and extracted markdown."
    allowed_tools: "Bash,Read,Write,Edit,Glob"
    content_file: "claude/skills/split-textbooks/SKILL.md"
```

- [ ] **Step 3: Replace the empty `claude_commands: []` line with the workflow entries**

Find:

```yaml
claude_commands: []
```

Replace with:

```yaml
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

- [ ] **Step 4: Syntax-check the node playbook**

Run:

```bash
ansible-playbook node.yml --syntax-check
```

Expected: no errors.

- [ ] **Step 5: Render-test in `--check --diff` mode**

Run:

```bash
ansible-playbook node.yml --tags claude --check --diff 2>&1 | tail -80
```

Expected: diffs for `~/.claude/skills/split-textbooks/SKILL.md`, `~/.claude/commands/split-textbooks.md`, `~/.claude/commands/split-textbook.md`. The skill diff should include the recipe content; the command diffs should include their respective prose.

- [ ] **Step 6: Commit**

```bash
git add roles/node/defaults/main/claude.yml
git commit -m "[Claude] Wire split-textbooks skill and commands into node role"
```

---

## Task 9: Add CLI tools to `dev_packages`

**Purpose:** Ensure `pdfinfo`, `pdftotext`, `pdffonts`, `qpdf`, `ocrmypdf` are installed by Homebrew (macOS) and devbox/nix (Linux). The `Brewfile.j2` template auto-includes anything in `dev_packages.<name>.brew`.

**Files:**
- Modify: `group_vars/all.yml`

- [ ] **Step 1: Locate the `dev_packages` block**

Run:

```bash
grep -n "^dev_packages:" group_vars/all.yml
```

Expected: line ~102.

- [ ] **Step 2: Append three entries to `dev_packages`**

Edit `group_vars/all.yml`. The `dev_packages` map is alphabetically loose but uses two-space indentation per entry. Insert these three entries (a sensible spot is at the end of the existing `dev_packages` map; if a `pdf*` cluster doesn't exist, just append):

```yaml
  poppler:
    brew:
      - "poppler"
    devbox:
      - "poppler_utils"
  qpdf:
    brew:
      - "qpdf"
    devbox:
      - "qpdf"
  ocrmypdf:
    brew:
      - "ocrmypdf"
    devbox:
      - "ocrmypdf"
```

Notes:

- `poppler` (Homebrew) ships `pdfinfo`, `pdftotext`, `pdffonts`. The nixpkgs equivalent is `poppler_utils` (the `_utils` package contains the CLI binaries).
- `ocrmypdf` pulls `tesseract` and `ghostscript` transitively on both platforms.
- The `nonroot` field is intentionally omitted — none of these tools are typically available as standalone user-space binaries; users without root should rely on devbox/nix.

- [ ] **Step 3: Render the Brewfile to confirm new entries appear**

Run:

```bash
ansible-playbook homebrew.yml --tags config --skip-tags install --check --diff 2>&1 | tail -40
```

Expected: diff includes `brew "poppler"`, `brew "qpdf"`, `brew "ocrmypdf"` lines in the rendered Brewfile.

- [ ] **Step 4: Commit**

```bash
git add group_vars/all.yml
git commit -m "[Packages] Add poppler/qpdf/ocrmypdf for split-textbooks workflow"
```

---

## Task 10: Add fixtures + README

**Purpose:** Three small PDFs and a README describing them, used for manual smoke verification of the recipe. Not run by CI.

**Files:**
- Create: `roles/dotfiles/files/claude/skills/split-textbooks/fixtures/README.md`
- Create: `roles/dotfiles/files/claude/skills/split-textbooks/fixtures/outline-text.pdf`
- Create: `roles/dotfiles/files/claude/skills/split-textbooks/fixtures/toc-text.pdf`
- Create: `roles/dotfiles/files/claude/skills/split-textbooks/fixtures/scanned.pdf`

The fixtures need to be small, generated synthetically, and committed to the repo. The plan below produces them with `pdflatex` (text fixtures) and ImageMagick (scanned fixture). If those aren't available, see Step 5's alternative.

- [ ] **Step 1: Create the fixtures directory**

Run: `mkdir -p roles/dotfiles/files/claude/skills/split-textbooks/fixtures`

- [ ] **Step 2: Write `outline-text.pdf` — text PDF with embedded outline**

Create a temporary LaTeX source `/tmp/outline-text.tex`:

```latex
\documentclass{book}
\usepackage{hyperref}
\hypersetup{bookmarksopen=true}
\begin{document}
\frontmatter
\chapter{Preface}
This is the preface. \newpage Some preface text continues.
\mainmatter
\chapter{Chapter One: Foundations}
Chapter one body text here. \newpage More chapter one.
\chapter{Chapter Two: Operations}
Chapter two body text here. \newpage More chapter two.
\backmatter
\chapter{Glossary}
A: definition. B: definition. \newpage More glossary.
\end{document}
```

Run:

```bash
cd /tmp && pdflatex -interaction=nonstopmode outline-text.tex
cp /tmp/outline-text.pdf roles/dotfiles/files/claude/skills/split-textbooks/fixtures/outline-text.pdf
```

Then verify the outline is present:

```bash
pdfinfo -outline roles/dotfiles/files/claude/skills/split-textbooks/fixtures/outline-text.pdf
```

Expected: outline lists Preface / Chapter One / Chapter Two / Glossary entries.

- [ ] **Step 3: Write `toc-text.pdf` — text PDF with explicit "Contents" page, no outline**

Create `/tmp/toc-text.tex`:

```latex
\documentclass{book}
\begin{document}
\section*{Contents}
\noindent
Preface \dotfill 1\\
Chapter 1: Limits \dotfill 5\\
Chapter 2: Derivatives \dotfill 12\\
Glossary \dotfill 18
\newpage
\section*{Preface}
Preface body. \newpage
\section*{Chapter 1: Limits}
Limits body. \newpage \newpage \newpage
\section*{Chapter 2: Derivatives}
Derivatives body. \newpage \newpage \newpage \newpage
\section*{Glossary}
A: one. B: two.
\end{document}
```

Run:

```bash
cd /tmp && pdflatex -interaction=nonstopmode toc-text.tex
cp /tmp/toc-text.pdf roles/dotfiles/files/claude/skills/split-textbooks/fixtures/toc-text.pdf
pdfinfo -outline roles/dotfiles/files/claude/skills/split-textbooks/fixtures/toc-text.pdf
```

Expected: `pdfinfo -outline` prints nothing (no outline). `pdftotext -layout -l 5 ...` should show the Contents page with dotted leaders.

- [ ] **Step 4: Write `scanned.pdf` — image-only PDF, no text layer**

Use ImageMagick to create a few image pages with rendered text, bundled into a single PDF with no text layer:

```bash
cd /tmp && for i in 1 2 3; do
  magick -size 612x792 xc:white -gravity center -pointsize 24 \
    -annotate 0 "This is fixture page $i — image only, no text layer." \
    page-$i.png
done
magick page-1.png page-2.png page-3.png scanned.pdf
cp /tmp/scanned.pdf roles/dotfiles/files/claude/skills/split-textbooks/fixtures/scanned.pdf
```

Verify there's no text layer:

```bash
pdftotext roles/dotfiles/files/claude/skills/split-textbooks/fixtures/scanned.pdf -
```

Expected: empty output (or whitespace only).

- [ ] **Step 5: Fallback if `pdflatex`/`magick` are not installed**

If the engineer's environment lacks these tools, document the omission and skip fixture generation for now — the fixtures are smoke aids, not required for the role to deploy. Add a `fixtures/.gitkeep` so the directory exists, and note in Step 6's README which fixtures are missing.

- [ ] **Step 6: Write the fixtures README**

Create `roles/dotfiles/files/claude/skills/split-textbooks/fixtures/README.md` with this content:

````markdown
# split-textbooks fixtures

Three small PDFs for manually verifying the recipe end-to-end. Not run by CI; not consumed by the recipe at deploy time.

| Fixture            | Exercises                       | Expected `detection_method` |
|--------------------|--------------------------------|-----------------------------|
| `outline-text.pdf` | Embedded outline → path 2a      | `bookmarks`                |
| `toc-text.pdf`     | "Contents" page parsing → 2b    | `toc_parse`                |
| `scanned.pdf`      | OCR sidecar + 2b/2c on the OCR | `toc_parse` or `llm`        |

## Expected output (rough)

After `/split-textbooks <fixtures-dir>`:

- `outline-text/` — manifest with `is_scanned: false`, `detection_method: "bookmarks"`, ~4 sections (preface, chapter 1, chapter 2, glossary).
- `toc-text/` — manifest with `is_scanned: false`, `detection_method: "toc_parse"`, ~4 sections, `page_offset: 1` (the "Contents" page itself).
- `scanned/` — `scanned.ocr.pdf` exists alongside; manifest with `is_scanned: true`, `canonical_pdf: "scanned.ocr.pdf"`, `detection_method: "toc_parse"` or `"llm"` (depends on OCR quality).

## Regenerating

The fixtures were generated with `pdflatex` and ImageMagick (`magick`). See the implementation plan, Task 10, for the exact source files used.
````

- [ ] **Step 7: Commit**

```bash
git add roles/dotfiles/files/claude/skills/split-textbooks/fixtures/
git commit -m "[Claude] Add split-textbooks fixtures + README"
```

---

## Task 11: End-to-end verification

**Purpose:** Confirm the role deploys all three assets to `~/.claude/` with correct content, then run the slash command on the fixtures.

- [ ] **Step 1: Run the node role for real**

Run:

```bash
just install-node-packages
```

Or directly: `ansible-playbook node.yml --tags claude`.

Expected: tasks complete without errors. Pay attention to the three `Template ... files` tasks for skills/agents/commands.

- [ ] **Step 2: Verify deployed file paths**

Run:

```bash
ls -la ~/.claude/skills/split-textbooks/SKILL.md \
       ~/.claude/commands/split-textbooks.md \
       ~/.claude/commands/split-textbook.md
```

Expected: all three files exist with non-zero size.

- [ ] **Step 3: Verify frontmatter on the deployed slash commands**

Run:

```bash
head -10 ~/.claude/commands/split-textbooks.md
head -10 ~/.claude/commands/split-textbook.md
```

Expected: each starts with `---`, has `description:`, `allowed-tools:`, `argument-hint:`, `model:` lines, then `---`.

- [ ] **Step 4: Verify the deployed SKILL.md matches the source**

Run:

```bash
diff roles/dotfiles/files/claude/skills/split-textbooks/SKILL.md \
     <(tail -n +"$(grep -n '^---$' ~/.claude/skills/split-textbooks/SKILL.md | sed -n '2p' | cut -d: -f1)" ~/.claude/skills/split-textbooks/SKILL.md | tail -n +2)
```

Expected: no diff (the body after the frontmatter matches the source file).

- [ ] **Step 5: Verify the CLI tools are installed**

Run:

```bash
command -v pdfinfo pdftotext pdffonts qpdf ocrmypdf
```

Expected: a path printed for each. If any are missing, run `just homebrew` (macOS) or `just devbox` (Linux) and re-check.

- [ ] **Step 6: Run `/split-textbooks` on the fixtures (manual)**

In Claude Code:

1. Copy the fixtures to a scratch directory: `cp -r roles/dotfiles/files/claude/skills/split-textbooks/fixtures /tmp/textbooks-smoke`
2. Invoke `/split-textbooks /tmp/textbooks-smoke` in Claude Code.
3. Inspect outputs: each fixture should produce a `<book>/manifest.json` with `status: "complete"` and slices on disk.

Expected per fixture:

- `outline-text/manifest.json` — `detection_method: "bookmarks"`, `is_scanned: false`, ~4 sections.
- `toc-text/manifest.json` — `detection_method: "toc_parse"`, `is_scanned: false`, ~4 sections.
- `scanned/manifest.json` — `is_scanned: true`, OCR sidecar present at `/tmp/textbooks-smoke/scanned.ocr.pdf`.

- [ ] **Step 7: Run `/split-textbook` on a deliberately broken fixture**

Truncate one fixture to corrupt it, then retry:

```bash
truncate -s 100 /tmp/textbooks-smoke/outline-text.pdf
rm -rf /tmp/textbooks-smoke/outline-text
```

Invoke `/split-textbook /tmp/textbooks-smoke/outline-text.pdf` in Claude Code.

Expected: `outline-text/manifest.json` with `status: "failed"`, `failed_step: "detect_outline"`, populated `error_message`.

- [ ] **Step 8: Clean up the scratch directory**

Run: `rm -rf /tmp/textbooks-smoke`

- [ ] **Step 9: Final commit (if any tweaks were needed)**

If Steps 6–7 surfaced bugs and you edited the recipe or commands, commit those fixes now:

```bash
git status
git add <changed-files>
git commit -m "[Claude] Fix recipe issues found during fixture run"
```

If nothing changed, skip this step.

---

## Self-review notes

The plan was checked against the spec on these dimensions:

- **Spec coverage:** every numbered item in the spec's "Implementation order" hint is covered by Tasks 1–10, with Task 11 picking up the manual verification described in the spec's "End-to-end manual test" section.
- **Schema parity:** `claude_commands_dir` and `claude_commands: []` are added to BOTH `roles/dotfiles/defaults/main/claude.yml` (so the dotfiles role is self-contained) AND `roles/node/defaults/main/claude.yml` (per the spec). This deviates from the spec's letter, which only mentions the node role file, but matches the existing pattern for `claude_skills` / `claude_agents` and avoids breaking the dotfiles role when run standalone.
- **Type consistency:** the manifest schema is identical wherever it appears (Task 5's recipe and the spec). The frontmatter keys (`description`, `allowed-tools`, `argument-hint`, `model`) match between `command.md.j2` (Task 3) and the values in `claude_commands` entries (Task 8).
- **`nonroot` packages:** intentionally omitted per the spec's scope ("`nonroot`: no change").
- **Smoke tests:** every template change has a `--check --diff` render test in the same task so regressions are caught before commit.
