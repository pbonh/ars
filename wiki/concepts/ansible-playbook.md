---
title: "Ansible Playbook"
type: concept
tags: [concept, automation, orchestration, yaml]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/ansible-user-guide.md"]
confidence: high
---

## Definition

A playbook is a YAML file that declares a set of plays, each mapping a group of hosts to a sequence of tasks. Playbooks are the primary reusable unit of Ansible automation, turning ad hoc commands into version-controlled, repeatable workflows.

## How It Works

- **Plays** are the top-level list items. Each play specifies a target (`hosts`), a privilege escalation method (`become`), and a list of tasks.
- **Tasks** invoke modules with arguments. Tasks run in order by default, and each task blocks the next unless run asynchronously.
- **Handlers** are special tasks triggered only when notified by another task that reports a change. They run once at the end of the play, after all regular tasks.
- **Blocks** group tasks together and can define `rescue` (error recovery) and `always` (cleanup) sections, similar to try/catch/finally.

## Key Parameters

- `hosts` — inventory pattern that selects target machines.
- `gather_facts` — boolean controlling whether Ansible collects system facts before task execution.
- `become` / `become_user` — privilege escalation directives.
- `tags` — labels that let you run only a subset of tasks or plays via `--tags`.
- `strategy` — execution strategy (`linear`, `free`, `host_pinned`) controlling how hosts progress through tasks.

## When To Use

Use a playbook whenever you need to perform a multi-step operation more than once, especially across multiple hosts. Playbooks are ideal for provisioning, configuration drift correction, application deployments, and rolling updates.

## Risks & Pitfalls

- **Missing idempotency checks.** Custom shell/command tasks that are not idempotent will report "changed" every run and may trigger handlers unnecessarily.
- **Handler flapping.** If a task incorrectly reports `changed: true`, handlers fire and may restart services repeatedly.
- **Play-level variable shadowing.** Variables defined at the play level override inventory-level values but may be overridden by `vars_prompt`, extra vars, or role defaults, leading to confusion.

## Related Concepts

- [[concepts/ansible-inventory]] — playbooks reference inventory groups.
- [[concepts/ansible-roles]] — roles are imported or included inside playbooks to share content.
- [[concepts/ansible-error-handling]] — blocks and rescue/always live inside playbooks.
- [[concepts/ansible-check-mode]] — playbooks support dry-run execution.

## Sources

- Ansible User Guide — Using Ansible playbooks — https://docs.ansible.com/projects/ansible/latest/playbook_guide/index.html
