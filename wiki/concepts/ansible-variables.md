---
title: "Ansible Variables"
type: concept
tags: [concept, automation, configuration, templating]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/ansible-user-guide.md"]
confidence: high
---

## Definition

Variables in Ansible are named values that parameterize tasks, templates, and playbooks. They can be defined in many locations and merged by Ansible at runtime according to a strict precedence order.

## How It Works

Variables are declared as key-value pairs, lists, or dictionaries. They are referenced in playbooks and templates with Jinja2 syntax (`{{ variable_name }}`). Ansible evaluates variables lazily at the point of use.

Precedence (lowest to highest):
1. command-line values (`-e`, `--extra-vars`)
2. role defaults
3. inventory `group_vars` / `host_vars`
4. playbook `group_vars` / `host_vars`
5. host facts / cached `set_facts`
6. play `vars`
7. play `vars_prompt`
8. play `vars_files`
9. role `vars`
10. block `vars`
11. task `vars`
12. include `vars`
13. `set_facts` / registered variables
14. role parameters (`vars:` in role import/include)
15. extra vars (`-e` always wins)

Note: The exact ordering above is a simplified summary; the official documentation provides the full 22-layer precedence chain.

## Key Parameters

- `vars` — inline variables in a play or task.
- `vars_files` — external YAML files loaded into a play.
- `vars_prompt` — interactive prompts at playbook start.
- `register` — captures task output into a variable for later tasks.
- `set_fact` — creates or updates a host-specific fact during execution.

## When To Use

Use variables to separate environment-specific data (IPs, credentials, paths) from generic playbook logic. Store sensitive variables in Vault-encrypted files and non-sensitive defaults in role defaults or group variables.

## Risks & Pitfalls

- **Precedence confusion.** Because there are many layers, it is easy to accidentally override a variable in an unexpected place.
- **Undefined variables.** Referencing an undefined variable causes a fatal error unless the `default` filter is used.
- **Mutable defaults.** Dictionary and list variables defined at the role-default level are shared across hosts unless explicitly cloned or scoped.

## Related Concepts

- [[concepts/ansible-inventory]] — host and group variables live in inventory.
- [[concepts/ansible-facts]] — facts are a special category of variables.
- [[concepts/ansible-vault]] — encrypts variable files that contain secrets.

## Sources

- Ansible User Guide — Using Ansible playbooks (variables) — https://docs.ansible.com/projects/ansible/latest/playbook_guide/index.html
