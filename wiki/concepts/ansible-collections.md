---
title: "Ansible Collections"
type: concept
tags: [concept, automation, packaging, distribution]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/ansible-user-guide.md"]
confidence: high
---

## Definition

Collections are a distribution format for Ansible content that bundles multiple roles, modules, plugins, and playbooks into a single, namespace-qualified, versioned package. They replace the older standalone-role model for sharing complex, multi-component automation.

## How It Works

- **Namespace and name.** Every collection is identified as `namespace.name` (e.g., `community.general`). This prevents naming collisions between independently maintained content.
- **Directory structure.** A collection contains `roles/`, `plugins/` (modules, filters, lookups, etc.), `playbooks/`, and a `galaxy.yml` or `MANIFEST.json` manifest.
- **Building and publishing.** The `ansible-galaxy collection build` command creates a tarball from the source directory. The tarball can be published to Ansible Galaxy, Red Hat Automation Hub, or an internal artifact server.
- **Installing.** `ansible-galaxy collection install` fetches collections from a configured server, a Git repository, a URL, or a local tarball. The `requirements.yml` file declares dependencies for reproducible installs.
- **Execution.** Collections are installed into configured collection paths (e.g., `~/.ansible/collections`). Ansible automatically finds modules and plugins inside installed collections when referenced by their fully qualified collection name (FQCN).

## Key Parameters

- `galaxy.yml` — manifest with namespace, name, version, dependencies, and metadata.
- `requirements.yml` — dependency declaration for CI/CD or offline installs.
- `--collections-path` / `-p` — installation target directory.
- FQCN — fully qualified collection name used to reference a module or plugin (`namespace.name.module_name`).

## When To Use

Use collections when you need to distribute more than a single role—especially when the content includes custom modules, filters, or multiple roles that work together. Collections are the required packaging format for certified content on Automation Hub.

## Risks & Pitfalls

- **Version pinning drift.** Without a lock file or strict `requirements.yml`, `ansible-galaxy collection install` may pull newer minor versions unexpectedly.
- **Namespace squatting.** Public Galaxy namespaces are first-come, first-served; publish early or use a private hub.
- **Runtime dependency on ansible-core version.** Collections declare a minimum `ansible-core` version in `meta/runtime.yml`; installing a collection on an older engine can cause cryptic import errors.

## Related Concepts

- [[concepts/ansible-roles]] — collections contain roles as sub-components.
- [[entities/ansible-galaxy]] — the registry and CLI used to distribute collections.

## Sources

- Ansible User Guide — Using Ansible collections — https://docs.ansible.com/projects/ansible/latest/collections_guide/index.html
