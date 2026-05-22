---
title: "Ansible Asynchronous Tasks"
type: concept
tags: [concept, automation, performance, concurrency]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/ansible-user-guide.md"]
confidence: high
---

## Definition

Asynchronous tasks let long-running operations execute without blocking the SSH connection or subsequent tasks. Ansible can fire a task in the background, poll for its completion, or check the result later in the play.

## How It Works

- **`async` keyword.** Specifies the maximum runtime (in seconds) that Ansible will allow the task to run. If the task exceeds this limit, Ansible considers it failed.
- **`poll` keyword.** Defines how often (in seconds) Ansible checks the status of the async job. Setting `poll: 0` fires the task and immediately moves on without polling; the job runs truly in the background.
- **Job IDs.** When a task runs asynchronously, Ansible stores a job ID on the remote host (in `~/.ansible_async/`). You can use the `async_status` module later to retrieve the result using that ID.
- **Ad hoc async.** The `ansible` CLI also supports `-B` (background) and `-P` (poll) flags for one-off background commands.

## Key Parameters

- `async: <seconds>` — maximum allowed runtime.
- `poll: <seconds>` — polling interval; `0` means fire-and-forget.
- `jid` — the job identifier used with `async_status`.
- `mode: status` — required argument for `async_status`.

## When To Use

Use async tasks for operations that risk SSH timeouts: large file transfers, database migrations, package upgrades that restart services, or firmware flashes. Use `poll: 0` combined with a later `async_status` task when you want to perform other work while the long job runs.

## Risks & Pitfalls

- **Orphaned jobs.** If the playbook aborts or the control node disconnects, background jobs may continue on the remote host indefinitely. Implement timeouts and cleanup tasks.
- **Poll interval tuning.** Too frequent polling wastes control-node CPU and network bandwidth; too infrequent polling delays failure detection.
- **Not all modules support async.** Modules that rely on persistent connections or interactive prompts may behave incorrectly when run asynchronously.

## Related Concepts

- [[concepts/ansible-playbook]] — async is a task-level execution modifier.
- [[concepts/ansible-error-handling]] — async tasks can still fail, and their results must be checked.

## Sources

- Ansible User Guide — Asynchronous actions and polling — https://docs.ansible.com/projects/ansible/latest/playbook_guide/index.html
