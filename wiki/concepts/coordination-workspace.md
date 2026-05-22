---
title: "Coordination Workspace"
type: concept
tags: [concept, workspace, multi-repo, planning, openspec]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/openspec-docs"]
confidence: medium
---

## Definition

A coordination workspace is a durable planning home in OpenSpec that links multiple repositories or folders under stable names, allowing cross-repo changes to be planned from a single surface without requiring repo-local `openspec/` state in every linked location.

## How It Works

A workspace lives in a global data directory (e.g., `~/.local/share/openspec/workspaces/<name>/`) and contains:

```text
workspace-folder/
├── changes/                       # Workspace-level planning
└── .openspec-workspace/
    ├── workspace.yaml             # Shared identity + stable link names
    └── local.yaml                 # This machine's absolute paths
```

`workspace.yaml` stores portable metadata:

```yaml
version: 1
name: platform
links:
  api: {}
  web: {}
```

`local.yaml` stores machine-specific paths:

```yaml
version: 1
paths:
  api: /repos/api
  web: /repos/web
```

Commands:
- `openspec workspace setup` — create and link repos
- `openspec workspace link` / `relink` — add or repair paths
- `openspec workspace doctor` — verify resolvability
- `openspec workspace open` — open the working set in an editor or agent
- `openspec workspace update` — refresh agent skills

Workspace visibility is not change commitment: you link repos so OpenSpec knows about them, then create changes later when ready to plan specific work.

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| Workspace name | Kebab-case identifier, recorded in a global registry |
| Links | Stable names mapped to absolute paths per machine |
| Opener | Preferred agent or editor for `workspace open` |
| Skills | Agent-specific workflow skills installed in the workspace root |

## When To Use

Use a coordination workspace when:
- Work spans multiple repositories (e.g., API + web + mobile)
- A monorepo is so large that different teams plan against subfolders
- You want a single `openspec list` view across disparate codebases

Stick to repo-local `openspec/` when:
- One repo owns the full planning, implementation, and archive flow
- Cross-repo work is rare enough that separate changes suffice

## Risks & Pitfalls

- **Beta stability:** OpenSpec explicitly warns that workspace commands, state files, and JSON output are under active development and can change without notice. Do not build long-lived automation on them.
- **Path portability:** `local.yaml` contains absolute paths and is gitignored by design. Each team member must run `workspace link` or `relink` on their own machine.
- **WSL/Windows path confusion:** Native Windows, PowerShell, and WSL2 each keep their own path strings. OpenSpec does not translate between `D:\repo`, `/mnt/d/repo`, and UNC paths.
- **No repo-local state required for planning:** Linked folders do not need `openspec/` directories to participate in workspace planning, but later implementation or archive workflows may require repo readiness.

## Related Concepts

- [[concepts/opsx-workflow]] — The workflow engine that workspaces extend
- [[concepts/fluid-workflow]] — Workspaces add cross-repo fluidity

## Sources

- OpenSpec Concepts Guide (`raw/openspec-docs/concepts.md`)
- OpenSpec CLI Reference (`raw/openspec-docs/cli.md`)
