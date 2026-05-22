---
title: "Ansible User Guide"
type: summary
tags: [summary, automation, infrastructure, configuration-management]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/ansible-user-guide.md"]
confidence: high
---

## Overview

The Ansible User Guide is the canonical operational reference for Ansible, an open-source IT automation platform. The guide covers how to build inventories, write playbooks, manage secrets with Vault, reuse content via roles and collections, and execute tasks across diverse target systems including Linux, Windows, BSD, and z/OS UNIX. It is structured around practical, day-to-day usage rather than deep architectural internals, focusing on the tools and patterns that operators need to deploy, configure, and orchestrate infrastructure reliably.

The documentation treats Ansible as a **desired-state** engine: you describe the end-state of a system in YAML playbooks, and Ansible converges the managed nodes toward that state. The guide emphasizes idempotency—running the same playbook multiple times should not change the system after the first successful run. It also covers execution flow control, including conditionals, loops, error handling, asynchronous tasks, and delegation, so that users can adapt automation to real-world constraints such as long-running jobs, flaky network paths, or mixed operating-system estates.

## Key Claims

- **Inventory-first targeting.** Every Ansible operation starts with an inventory, a list of managed nodes and their metadata. The guide shows how to build static inventories in INI or YAML, create dynamic inventories for cloud APIs, and use patterns to target subsets of hosts. [[concepts/ansible-inventory]]
- **Playbooks as reusable orchestration units.** Playbooks combine plays (host mappings), tasks (module invocations), handlers (triggered actions), and blocks (grouped logic with error recovery) into version-controlled, repeatable workflows. [[concepts/ansible-playbook]]
- **Layered variable precedence.** Variables can live in inventory files, group/host variable directories, playbooks, roles, extra CLI arguments, and facts. Ansible merges them with a documented precedence order, allowing users to override values at the right granularity. [[concepts/ansible-variables]]
- **Fact-driven decision making.** Ansible gathers facts—automatically discovered host attributes—before playbook execution. Custom facts and caching strategies let users build data-rich, conditional automation without hard-coding host specifics. [[concepts/ansible-facts]]
- **Vault for secrets at rest.** Ansible Vault encrypts individual variables or whole files so that sensitive data can be stored in source control. The guide explains vault passwords, vault IDs, and how to integrate Vault with playbook execution. [[concepts/ansible-vault]]
- **Content reuse through roles and collections.** Roles package tasks, variables, templates, and handlers into a standard directory layout. Collections extend that model by bundling multiple roles, modules, and plugins into versioned, namespace-qualified packages distributed via Galaxy or private hubs. [[concepts/ansible-roles]] [[concepts/ansible-collections]]
- **Execution control primitives.** Conditionals (`when`), loops, blocks with `rescue`/`always`, asynchronous polling, task delegation, and check-mode/diff-mode give operators fine-grained control over *when*, *where*, and *how* tasks run. [[concepts/ansible-conditionals]] [[concepts/ansible-error-handling]] [[concepts/ansible-delegation]] [[concepts/ansible-async-tasks]] [[concepts/ansible-check-mode]]

## Source Metadata

- **Type:** Official project documentation (HTML, Sphinx/RTD)
- **Owner:** Ansible project contributors / Red Hat
- **URL:** https://docs.ansible.com/projects/ansible/latest/user_guide/index.html
- **License:** GNU General Public License v3.0+ (documentation CC-BY-SA 4.0)
- **Ingested on:** 2026-05-21
- **Scope note:** The deprecated `user_guide/index.html` landing page now redirects content into eight focused guides: inventories, command line tools, playbooks, vault, modules/plugins, collections, OS-specific usage (Windows/BSD/z/OS), and tips/tricks. The raw source was captured at depth-2 for each of these guide trees.

## Relevant Concepts

- [[concepts/ansible-inventory]]
- [[concepts/ansible-playbook]]
- [[concepts/ansible-variables]]
- [[concepts/ansible-facts]]
- [[concepts/ansible-vault]]
- [[concepts/ansible-roles]]
- [[concepts/ansible-collections]]
- [[concepts/ansible-conditionals]]
- [[concepts/ansible-error-handling]]
- [[concepts/ansible-delegation]]
- [[concepts/ansible-async-tasks]]
- [[concepts/ansible-check-mode]]
