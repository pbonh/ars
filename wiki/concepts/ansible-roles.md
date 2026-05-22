---
title: "Ansible Roles"
type: concept
tags: [concept, automation, reuse, modularity]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/ansible-user-guide.md"]
confidence: high
---

## Definition

A role is a structured, reusable bundle of Ansible content—tasks, handlers, variables, templates, files, and modules—organized in a standard directory layout. Roles allow operators to share and consume common automation patterns without copy-pasting playbook tasks.

## How It Works

- **Directory layout.** A role contains directories such as `tasks/main.yml`, `handlers/main.yml`, `vars/main.yml`, `defaults/main.yml`, `templates/`, `files/`, and `meta/main.yml`. Only directories that exist are loaded.
- **Defaults vs. vars.** `defaults/main.yml` holds variables with the lowest precedence, intended to be overridden easily. `vars/main.yml` holds variables with higher precedence that are less likely to change.
- **Dependencies.** `meta/main.yml` can declare role dependencies; Ansible ensures dependent roles run first.
- **Embedding in playbooks.** Roles are invoked with the `roles:` play keyword (static, at play start) or with `import_role` / `include_role` tasks (static or dynamic, inside the task list).
- **Ansible Galaxy integration.** Roles can be published to Galaxy and installed via `ansible-galaxy role install`.

## Key Parameters

- `defaults/` — lowest-precedence variables.
- `vars/` — higher-precedence, role-internal variables.
- `tasks/main.yml` — the main entry point for task execution.
- `meta/main.yml` — role metadata and dependencies.
- `allow_duplicates` — meta setting that lets the same role run multiple times in a play.

## When To Use

Use a role when you have a self-contained configuration story (e.g., "install and configure nginx") that you want to reuse across playbooks or share with the community. Roles are the standard unit of content reuse before collections.

## Risks & Pitfalls

- **Tight coupling.** Roles that hard-code hostnames or assume specific network layouts become brittle when reused in new environments.
- **Duplicate execution.** By default, a role runs only once per play even if referenced multiple times, unless `allow_duplicates: true` is set.
- **Precedence surprises.** Variables in `vars/main.yml` override many other sources, which can frustrate playbook authors who try to customize behavior.

## Related Concepts

- [[concepts/ansible-collections]] — collections supersede standalone roles by bundling roles, modules, and plugins into versioned packages.
- [[concepts/ansible-playbook]] — playbooks consume roles via `roles:`, `import_role`, or `include_role`.
- [[concepts/ansible-variables]] — role defaults and vars are critical layers in the precedence stack.

## Sources

- Ansible User Guide — Creating reusable files and roles — https://docs.ansible.com/projects/ansible/latest/playbook_guide/index.html
