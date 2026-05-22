---
title: "Ansible Conditionals"
type: concept
tags: [concept, automation, control-flow, jinja2]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/ansible-user-guide.md"]
confidence: high
---

## Definition

Conditionals in Ansible control whether a task, block, play, or handler executes based on runtime data. They are expressed with the `when` keyword and evaluated using Jinja2 tests and filters.

## How It Works

- **`when` keyword.** Attached to a task or block, `when` accepts a Jinja2 expression. If the expression evaluates to `true` (or a truthy value), the task runs; otherwise it is skipped.
- **Tests and filters.** Ansible supports standard Jinja2 comparisons (`==`, `!=`, `<`, `>`) plus Ansible-specific tests such as `is succeeded`, `is failed`, `is changed`, `is directory`, and `is subset`.
- **Conditionals on loops.** When combined with `loop`, the `when` clause is evaluated for each iteration independently.
- **Conditionals on includes and imports.** Dynamic and static reuse statements (`include_tasks`, `import_tasks`, `import_playbook`) also accept `when`, applying the condition to the entire included content.
- **`failed_when` and `changed_when`.** These let you redefine what constitutes failure or change for a task, which is critical for shell commands or custom modules with non-standard exit codes.

## Key Parameters

- `when` — primary conditional clause.
- `failed_when` — overrides the default failure detection.
- `changed_when` — overrides the default change detection.
- `ansible_facts` and `registered` variables — common inputs for conditional logic.

## When To Use

Use conditionals when a playbook must adapt to heterogeneous environments (different OS families, varying hardware, feature flags) or when a task should run only if a prior task produced a specific result. Use `changed_when` and `failed_when` to make command/shell tasks idempotent and reliable.

## Risks & Pitfalls

- **Type coercion surprises.** Jinja2 comparisons between strings and integers can behave unexpectedly; use the `|int` or `|string` filters explicitly.
- **Undefined variables in conditionals.** A `when` clause referencing an undefined variable fails unless protected with `is defined` or `default()`.
- **Over-complex `when` lists.** Combining many conditions with `and`/`or` inline Jinja2 can become unreadable; refactor into variables or separate task files.

## Related Concepts

- [[concepts/ansible-variables]] — conditionals consume variables.
- [[concepts/ansible-facts]] — facts are the most common data source for `when` clauses.
- [[concepts/ansible-playbook]] — conditionals are attached to tasks, blocks, and plays.

## Sources

- Ansible User Guide — Conditionals — https://docs.ansible.com/projects/ansible/latest/playbook_guide/index.html
