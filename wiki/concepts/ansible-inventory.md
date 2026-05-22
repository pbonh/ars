---
title: "Ansible Inventory"
type: concept
tags: [concept, automation, infrastructure, inventory]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/ansible-user-guide.md"]
confidence: high
---

## Definition

An inventory is a list of managed nodes (hosts) and metadata that Ansible uses to know which machines to target and how to reach them. Inventories can be static files, dynamic scripts or plugins that query cloud APIs, or combinations organized in directories.

## How It Works

- **Static inventories** are written in INI or YAML. Hosts are grouped logically (e.g., `[webservers]`, `[dbservers]`), and groups can nest inside other groups.
- **Dynamic inventories** are provided by plugins or scripts that return JSON at runtime. This is essential for ephemeral infrastructure where hosts start and stop constantly (e.g., AWS EC2, OpenStack).
- **Patterns** let you target subsets of the inventory at execution time. For example, `webservers:dbservers` targets the union, `webservers:!staging` targets webservers except those also in staging.
- **Behavioral parameters** (e.g., `ansible_user`, `ansible_port`, `ansible_connection`) can be attached to hosts or groups to define how Ansible connects.

## Key Parameters

- `hosts` / `groups` — the structural units of an inventory.
- `host_vars` and `group_vars` — directories or file sections that assign variables to individual hosts or groups.
- `ansible_connection` — transport protocol (`ssh`, `winrm`, `local`, `paramiko`, etc.).
- `children` — nested group relationships in YAML inventories.

## When To Use

Use a static inventory when you have a relatively stable set of machines with known hostnames or IPs. Use a dynamic inventory when operating in cloud or container environments where the host list changes continuously. Combine both by placing a dynamic inventory file and static override files in the same directory; Ansible merges them.

## Risks & Pitfalls

- **Duplicated host entries** across groups can cause conflicting variable assignments if precedence is not understood.
- **Missing behavioral parameters** for Windows or non-standard SSH ports lead to connection failures that look like credential errors.
- **Dynamic inventory caching:** without `--cache` or a cache plugin, dynamic inventories can slow down every playbook run because they re-query the cloud API.

## Related Concepts

- [[concepts/ansible-variables]] — variables defined in inventory are the lowest precedence layer.
- [[concepts/ansible-playbook]] — playbooks map plays to inventory groups.
- [[concepts/ansible-facts]] — facts can be used in inventory patterns or host/group vars logic.

## Sources

- Ansible User Guide — Building Ansible Inventories — https://docs.ansible.com/projects/ansible/latest/inventory_guide/index.html
