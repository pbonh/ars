---
title: "Ansible Delegation"
type: concept
tags: [concept, automation, networking, control-flow]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/ansible-user-guide.md"]
confidence: high
---

## Definition

Delegation is an Ansible execution primitive that runs a task on a different host than the one currently being managed by the play. It is commonly used to interact with load balancers, DNS APIs, or monitoring systems while configuring application servers.

## How It Works

- **`delegate_to`.** Attached to a task, `delegate_to: some_host` causes the task to execute on the specified host using that host’s connection parameters, while the task’s result is still associated with the original managed node in the play.
- **`delegate_facts`.** When set to `true`, facts gathered by a delegated task are assigned to the original host rather than the delegated host.
- **`local_action`.** A shorthand for `delegate_to: localhost`, useful for tasks that must run on the control node, such as generating local reports or adding a node to a local inventory file.
- **Parallel execution.** Delegated tasks still respect the play’s `strategy` and `serial` settings. Multiple hosts can delegate to the same target simultaneously; the target host must handle the concurrency (e.g., an API rate limit or a thread-safe local task).

## Key Parameters

- `delegate_to` — target hostname or inventory alias.
- `delegate_facts: true` — stores discovered facts on the original managed node.
- `local_action` — syntactic sugar for `delegate_to: localhost`.

## When To Use

Use delegation when a task needs to affect infrastructure outside the managed node: removing a node from a load balancer pool before deployment, updating a DNS record after provisioning, or sending a monitoring alert from the control node. Use `local_action` for control-node side effects such as writing a local CSV report.

## Risks & Pitfalls

- **Connection parameter mismatch.** The delegated host may need different credentials, Python interpreter, or connection type (`ansible_connection: local` vs `ssh`). These must be defined in inventory or task variables.
- **Fact attribution errors.** Without `delegate_facts: true`, a delegated `setup` task stores facts on the delegated host, which is usually not what you want.
- **Loop delegation complexity.** When `delegate_to` is combined with `loop`, each loop iteration runs on the same delegated host, which can create a bottleneck or race condition.

## Related Concepts

- [[concepts/ansible-playbook]] — delegation is a task-level execution control.
- [[concepts/ansible-inventory]] — delegated hosts must be resolvable in inventory or via DNS.

## Sources

- Ansible User Guide — Controlling where tasks run: delegation and local actions — https://docs.ansible.com/projects/ansible/latest/playbook_guide/index.html
