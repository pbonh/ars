---
title: "Zellij Terminology"
type: summary
tags: [summary, zellij, terminal, terminology]
created: 2026-05-21
sources: ["raw/zellij-repo/docs/TERMINOLOGY.md"]
updated: 2026-05-21
confidence: high
---

## Overview

This document defines the low-level terminal primitives that Zellij operates on: the ANSI/VT byte stream, its sub-protocols (CSI and OSC), and the pseudoterminal (pty) abstraction. These are the foundational terms that appear throughout the architecture and user-facing documentation.

## Key Claims

- ANSI/VT is the text-and-control stream read from the primary side of a pty.
- CSI sequences control terminal-emulator behavior (colors, cursor position).
- OSC sequences control the operating system (e.g., window title changes).
- A pty is a pair of endpoints: primary (emulator side) and secondary (shell side).
- Zellij creates one pty pair per terminal pane.

## Source Metadata

- **Type**: Markdown documentation
- **Owner**: Zellij Contributors
- **URL**: https://github.com/zellij-org/zellij/tree/main/docs/TERMINOLOGY.md
- **License**: MIT
- **Ingested on**: 2026-05-21

## Relevant Concepts

- [[concepts/ansi-vt-stream]]
- [[concepts/csi]]
- [[concepts/osc]]
- [[concepts/pty]]