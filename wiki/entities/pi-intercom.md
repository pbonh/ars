---
title: "pi-intercom"
type: entity
tags: [entity, tool, pi-extension, coordination, subagent]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/pi-subagents-readme.md"]
confidence: medium
---

## Overview

`pi-intercom` is an optional companion [[concepts/pi-extension|extension]] for
[[entities/pi|Pi]] that lets child [[concepts/pi-subagent|subagents]] talk back
to the parent Pi session while they are running. [[entities/pi-subagents]] works
without it; install it only when you want children to request a decision rather
than guessing. Once installed, `pi-subagents` can automatically give child
agents a private coordination channel back to the parent.

## Characteristics

- **Install**: `pi install npm:pi-intercom` (the bridge also recognizes legacy
  local extension checkouts).
- **Child coordination tool**: `contact_supervisor` — the child contacts the
  parent/supervisor that delegated the task. Use `reason: "need_decision"` for
  blocking decisions or clarification, and `reason: "progress_update"` for short
  non-blocking updates when a discovery changes the plan.
- **Parent-side delivery**: with the bridge active, `pi-subagents` sends grouped
  completion results through `pi-intercom` — one grouped message per foreground
  parent `subagent` run and one per completed async result file, including child
  intercom targets, full child summaries, and compact nested summaries.
- **Acknowledged delivery** returns a compact receipt with artifact/session
  paths; unacknowledged delivery preserves the normal full output.
- **Bridge config** (`intercomBridge` in `pi-subagents` config): `mode`
  (`always` default, `fork-only`, or `off`) and `instructionFile` (a Markdown
  template with `{orchestratorTarget}` interpolation).
- **Activation requirements**: `pi-intercom` installed and enabled, a targetable
  current session name or fallback alias, and `pi-intercom` present in any
  explicit agent `extensions` allowlist.

## Common Strategies

- "Run this implementation in the background. If the worker gets blocked or
  needs a product decision, have it ask me through intercom."
- "Ask oracle to review this plan. If it sees a decision I need to make, have it
  ask me instead of assuming."
- Avoid routine completion handoffs from the child — those are not expected;
  reserve `contact_supervisor` for genuine decisions and meaningful updates.
- Run `/subagents-doctor` if intercom messages do not show up.

## Sources

- [pi-subagents README](raw/pi-subagents-readme.md)
</content>
