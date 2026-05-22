---
title: "Ansible Error Handling"
type: concept
tags: [concept, automation, resilience, control-flow]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/ansible-user-guide.md"]
confidence: high
---

## Definition

Error handling in Ansible determines how a playbook reacts when a task returns a non-zero exit code, a module reports failure, or a host becomes unreachable. The default behavior is to stop executing on the failing host and continue on others, but Ansible provides primitives to customize this.

## How It Works

- **Blocks.** A `block` groups tasks. It can contain a `rescue` section that runs only if a task inside the block fails, and an `always` section that runs regardless of success or failure, similar to try/catch/finally.
- **`any_errors_fatal`.** When set at the play or block level, a failure on any host immediately stops execution on *all* hosts. This is useful for clustered deployments where partial progress is dangerous.
- **`max_fail_percentage`.** Limits how many hosts may fail before the play aborts entirely, allowing tolerance for small subsets of bad nodes.
- **`ignore_errors`.** Marks a task so that its failure does not stop the play. The failure is still recorded in the result object and visible in the output.
- **`force_handlers`.** Ensures that notified handlers run even if a later task in the play fails.

## Key Parameters

- `block`, `rescue`, `always` — structural keywords.
- `any_errors_fatal: true` — global abort trigger.
- `max_fail_percentage: <number>` — threshold before play abort.
- `ignore_errors: true` — per-task failure suppression.
- `force_handlers: true` — play-level handler guarantee.

## When To Use

Use blocks with `rescue`/`always` when a set of tasks has a cleanup story (e.g., release a lock, delete a temporary file). Use `any_errors_fatal` when deploying to tightly coupled systems such as database clusters where inconsistency is unacceptable. Use `ignore_errors` sparingly, only for probes or health checks whose failure is informational.

## Risks & Pitfalls

- **Silent failures with `ignore_errors`.** Subsequent tasks may assume the ignored task succeeded. Always inspect the `registered` result with `is failed` before depending on the outcome.
- **Handler suppression.** If a task that notifies a handler fails before the handler would run, and `force_handlers` is not set, the handler is skipped, potentially leaving the system in a half-configured state.
- **Rescue scope confusion.** Variables set inside a `rescue` block are available to subsequent tasks in the same play, but facts set inside a failed block before the failure may not be registered.

## Related Concepts

- [[concepts/ansible-playbook]] — blocks, rescue, and always live inside playbooks.
- [[concepts/ansible-conditionals]] — `failed_when` and `changed_when` customize failure semantics.

## Sources

- Ansible User Guide — Error handling in playbooks — https://docs.ansible.com/projects/ansible/latest/playbook_guide/index.html
