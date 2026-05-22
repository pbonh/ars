---
title: "Pi Package"
type: concept
tags: [concept, pi, packaging, npm, distribution]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/pi-repo/packages/coding-agent/docs/packages.md"]
confidence: high
---

## Definition

A Pi package is a distributable bundle of extensions, skills, prompt templates, and/or themes that can be shared via npm, git, or local paths and installed into Pi.

## How It Works

1. A package declares resources in `package.json` under the `pi` key or uses conventional directories (`extensions/`, `skills/`, `themes/`, `prompts/`).
2. Users install packages with `pi install npm:@scope/pkg`, `pi install git:github.com/user/repo`, or local paths.
3. Installed packages are tracked in `settings.json` (user or project level via `-l`).
4. Project settings can be shared with a team; Pi auto-installs missing packages on startup.
5. Packages can be scoped and deduplicated; updates use `pi update`.

## Key Parameters

- Install targets: npm registry, git repos, local paths, raw URLs
- Settings key: `pi` in `package.json` or conventional directories
- Scope: user (`~/.pi/agent/settings.json`) or project (`.pi/settings.json`)
- Temporary load: `pi -e <package>`

## When To Use

Create a Pi package when:
- You want to share extensions, skills, themes, or prompts across projects or teams.
- You are building a reusable integration (e.g., a company-specific deployment workflow).
- You want versioned distribution via npm or git tags.

## Risks & Pitfalls

- Packages run with full system access; review third-party source code before installing.
- npm packages execute install scripts by default; Pi recommends `--ignore-scripts` for installs.
- Project settings with auto-install may pull in unexpected updates if versions are not pinned.
- Deduplication rules can suppress duplicate resources from different packages.

## Related Concepts

- [[concepts/pi-extension]]
- [[concepts/pi-skill]]
- [[concepts/pi-theme]]
- [[concepts/pi-prompt-template]]

## Sources

- [Pi Packages Documentation](raw/pi-repo/packages/coding-agent/docs/packages.md)
