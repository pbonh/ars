---
title: "ansible-core"
type: entity
tags: [entity, product, engine, python-package]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/ansible-user-guide.md"]
confidence: high
---

## Overview

`ansible-core` is the open-source engine and command-line package that powers Ansible. It contains the runtime, the executor, the plugin loader, and a core set of modules and plugins. Prior to Ansible 2.9, the engine and community content shipped together in a single `ansible` package; starting with Ansible 2.10, the project was split so that `ansible-core` provides the platform and the `ansible` community package bundles `ansible-core` plus a curated set of collections.

## Characteristics

- **Minimal footprint.** `ansible-core` includes only the framework and a limited set of built-in modules; extended functionality arrives via collections.
- **Versioned independently.** Its release cadence is separate from the broader `ansible` community package, allowing faster iteration on the engine.
- **CLI entry points.** Provides `ansible`, `ansible-playbook`, `ansible-doc`, `ansible-vault`, `ansible-galaxy`, `ansible-pull`, and other core CLI tools.

## Common Strategies

- **Downstream packaging.** Distributions and vendors (e.g., Red Hat Ansible Automation Platform) often ship `ansible-core` as the supported runtime, with additional certified collections layered on top.
- **Collection development.** When building a collection, developers target `ansible-core` compatibility versions and declare them in `meta/runtime.yml`.

## Sources

- Ansible User Guide — https://docs.ansible.com/projects/ansible/latest/user_guide/index.html
