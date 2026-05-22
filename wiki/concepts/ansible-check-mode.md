---
title: "Ansible Check Mode"
type: concept
tags: [concept, automation, testing, dry-run]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/ansible-user-guide.md"]
confidence: high
---

## Definition

Check mode (often called dry-run) is an Ansible execution mode that predicts what changes a playbook would make without actually applying them. It is a safety mechanism for validating playbooks in production or CI pipelines before committing to modifications.

## How It Works

- **`--check` CLI flag.** When `ansible-playbook` is invoked with `--check`, modules that support check mode report whether they would change the system, but do not write any changes.
- **Diff mode.** Adding `--diff` shows the exact differences that would be applied, such as file line changes or template renderings, making it easier to audit planned modifications.
- **Skipping non-checkable tasks.** Some modules cannot predict their effect without executing (e.g., `command`, `shell`, custom API calls). These tasks are skipped by default in check mode unless explicitly forced with `check_mode: no`.
- **Forcing check mode.** A task can declare `check_mode: yes` to always run in dry-run style, or `check_mode: no` to bypass the global `--check` flag for that specific task. This is useful for prerequisite probes that must run to gather state before the main tasks can be evaluated.

## Key Parameters

- `--check` / `-C` — global dry-run flag.
- `--diff` — show textual diffs for changed resources.
- `check_mode: yes` / `check_mode: no` — per-task override.
- `changed_when` — can be used to improve check-mode accuracy for shell tasks.

## When To Use

Use check mode as a gate in CI/CD pipelines: run the playbook against a staging environment (or a representative production host) with `--check --diff` and abort the pipeline if unexpected changes appear. Use it when onboarding a new playbook to an existing environment to avoid collateral damage. Use `check_mode: no` sparingly on data-gathering tasks that are prerequisites for the rest of the playbook.

## Risks & Pitfalls

- **False negatives.** Modules that do not implement check mode will be skipped, so the dry-run report may under-report changes.
- **Side effects in data-gathering tasks.** If a prerequisite task with `check_mode: no` actually modifies state (e.g., creates a temporary token), the dry-run is no longer truly dry.
- **Vault exposure in audit logs.** Check mode still decrypts Vault-encrypted content to evaluate tasks. Running check mode on an untrusted CI runner may expose secrets in memory or logs.

## Related Concepts

- [[concepts/ansible-playbook]] — check mode is a playbook execution option.
- [[concepts/ansible-vault]] — vault content is decrypted even in check mode.
- [[concepts/ansible-conditionals]] — `changed_when` and `check_mode` interact for shell tasks.

## Sources

- Ansible User Guide — Ansible tips and tricks (check mode) — https://docs.ansible.com/projects/ansible/latest/tips_tricks/index.html
