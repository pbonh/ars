---
title: "Ansible Vault"
type: concept
tags: [concept, automation, security, encryption]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/ansible-user-guide.md"]
confidence: high
---

## Definition

Ansible Vault is a feature that encrypts sensitive data—either individual variables or entire files—so that playbooks and roles can be stored in source control without exposing plaintext secrets.

## How It Works

- **Password-based encryption.** Vault content is encrypted with AES-256 using a user-supplied password. The password can be provided interactively, via a password file, via a script, or through an environment variable.
- **Vault IDs.** Multiple vault passwords can be managed by assigning each a vault ID (e.g., `dev`, `prod`). The `--vault-id` CLI flag selects which password to use for which encrypted content.
- **Inline encrypted variables.** A variable can be encrypted in place inside a YAML file using the `!vault` tag, which stores the ciphertext as a single string.
- **Encrypted files.** Whole files (e.g., `secrets.yml`) can be encrypted. Ansible transparently decrypts them when they are loaded as `vars_files`.
- **CLI tools.** `ansible-vault create`, `encrypt`, `decrypt`, `edit`, `rekey`, and `view` manage the lifecycle of vault content.

## Key Parameters

- `--ask-vault-pass` / `--vault-password-file` — password sources at runtime.
- `--vault-id` — selects a specific vault identity.
- `ansible.cfg` settings: `vault_password_file`, `vault_identity_list`.

## When To Use

Use Vault whenever a playbook needs to handle passwords, API keys, private keys, or other credentials that must not appear in plaintext in a repository. Combine Vault with `no_log: true` on sensitive tasks to prevent decrypted values from appearing in playbook output.

## Risks & Pitfalls

- **Data at rest only.** Vault protects secrets in files and version control, but once decrypted during a run, the plaintext is visible in memory and potentially in logs unless `no_log` is used.
- **Password management.** Losing the vault password means the encrypted content is unrecoverable. Use a team password manager or a corporate secret store, not sticky notes.
- **Accidental commit of passwords.** Never commit the vault password file alongside the encrypted content; keep the password outside the repository.

## Related Concepts

- [[concepts/ansible-variables]] — vault-encrypted values are variables.
- [[concepts/ansible-playbook]] — playbooks reference vault files via `vars_files`.
- [[concepts/ansible-check-mode]] — check mode still decrypts vault content; do not run check mode with production vaults on untrusted audit systems.

## Sources

- Ansible User Guide — Protecting sensitive data with Ansible vault — https://docs.ansible.com/projects/ansible/latest/vault_guide/index.html
