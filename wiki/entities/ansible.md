---
title: "Ansible"
type: entity
tags: [entity, tool, automation, configuration-management, orchestration]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/ansible-user-guide.md"]
confidence: high
---

## Overview

Ansible is an open-source IT automation platform that handles configuration management, application deployment, intra-service orchestration, and provisioning. It is agentless, using SSH (or WinRM on Windows) to push small programs called modules to managed nodes, execute them, and clean up. The controlling machine needs only Python and the Ansible installation; target nodes need Python and an accessible transport, nothing else pre-installed.

## Characteristics

- **Agentless architecture.** No daemon or persistent software runs on managed nodes. Ansible opens a connection, ships a module payload, runs it, and tears the connection down.
- **YAML-driven.** Playbooks, inventories, variable files, and roles are all expressed in YAML (or INI for simple inventories), making them diff-friendly and reviewable in source control.
- **Idempotent by design.** Most built-in modules are written to detect the current state and only make changes when necessary, so repeated runs are safe.
- **Extensible.** Users can write custom modules in any language that returns JSON, custom plugins in Python, and package reusable content as roles or collections.

## Common Strategies

- **Push-based deployment.** The operator runs `ansible-playbook` from a control node; Ansible pushes changes out to the inventory. This fits CI/CD pipelines well.
- **Pull-based self-configuration.** `ansible-pull` inverts the model: each host periodically pulls a Git repository of playbooks and runs them locally, useful for autoscaling groups or devices without a dedicated control node.
- **Mixed-OS estates.** The same playbook can target Linux, Windows, BSD, and z/OS UNIX hosts by selecting OS-specific tasks with `when` conditionals or by delegating to OS-specific roles inside a collection.

## Sources

- Ansible User Guide — https://docs.ansible.com/projects/ansible/latest/user_guide/index.html
