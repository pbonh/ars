---
title: "Hermes Skills System"
type: concept
tags: [concept, ai-agent, skills, procedural-memory, agentskills-io]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-agent-docs/website/docs"]
confidence: high
---

## Definition

The Hermes Skills System is an on-demand knowledge document framework that provides procedural memory for the agent. Skills are portable, shareable documents following the [agentskills.io](https://agentskills.io/specification) open standard. The agent can load them progressively to minimize token usage, create new skills from experience, and improve existing skills during use.

## How It Works

Skills live in `~/.hermes/skills/` — the primary directory and source of truth. On fresh install, bundled skills are copied from the repo. Hub-installed and agent-created skills also go here. The agent can modify or delete any skill.

### Progressive Disclosure

Skills use a three-level loading pattern to stay token-efficient:

| Level | Function | Content | Token Cost |
|-------|----------|---------|------------|
| 0 | `skills_list()` | Name + description + category list | ~3k tokens |
| 1 | `skill_view(name)` | Full SKILL.md content + metadata | Varies |
| 2 | `skill_view(name, path)` | Specific reference file | Varies |

The agent only loads full skill content when it actually needs it.

### SKILL.md Format

```markdown
---
name: my-skill
description: Brief description of what this skill does
version: 1.0.0
platforms: [macos, linux]
metadata:
  hermes:
    tags: [python, automation]
    category: devops
    fallback_for_toolsets: [web]
    requires_toolsets: [terminal]
    config:
      - key: my.setting
        description: "What this controls"
        default: "value"
        prompt: "Prompt for setup"
---

# Skill Title

## When to Use
## Procedure
## Pitfalls
## Verification
```

### Agent-Managed Skills

The agent creates, updates, and deletes its own skills via the `skill_manage` tool:

| Action | Use For |
|--------|---------|
| `create` | New skill from scratch |
| `patch` | Targeted fixes (preferred — token-efficient) |
| `edit` | Major structural rewrites |
| `delete` | Remove a skill entirely |
| `write_file` / `remove_file` | Add/update supporting files |

Trigger conditions for skill creation:
- After completing a complex task (5+ tool calls) successfully
- When it hit errors or dead ends and found the working path
- When the user corrected its approach
- When it discovered a non-trivial workflow

### Skills Hub

Browse, search, install, and manage skills from online registries:

| Source | Example |
|--------|---------|
| `official` | `official/security/1password` |
| `skills-sh` | `skills-sh/vercel-labs/json-render/json-render-react` |
| `well-known` | `well-known:https://mintlify.com/docs/.well-known/skills/mintlify` |
| `github` | `openai/skills/k8s` |
| `url` | `https://sharethis.chat/SKILL.md` |

All hub-installed skills go through a security scanner checking for data exfiltration, prompt injection, destructive commands, and supply-chain signals.

### Skill Bundles

Bundles are tiny YAML files that group skills under a single slash command. Live in `~/.hermes/skill-bundles/<slug>.yaml`:

```yaml
name: backend-dev
description: Backend feature work — review, test, PR workflow.
skills:
  - github-code-review
  - test-driven-development
  - github-pr-workflow
instruction: |
  Always start by writing failing tests, then implement.
```

Bundles take precedence over individual skills when slugs collide.

## Key Parameters

| Parameter | Location | Description |
|-----------|----------|-------------|
| `platforms` | SKILL.md frontmatter | OS restriction (`macos`, `linux`, `windows`) |
| `fallback_for_toolsets` | `metadata.hermes` | Show ONLY when listed toolsets are unavailable |
| `requires_toolsets` | `metadata.hermes` | Show ONLY when listed toolsets are available |
| `external_dirs` | `config.yaml` skills section | Additional skill directories to scan |

## When To Use

- **Users**: Load a skill via `/skill-name` slash command or natural chat to give the agent domain expertise for a specific task.
- **Developers**: Publish reusable workflows as skills or skill bundles to codify team conventions.
- **Agent operators**: Let the agent build skills from experience to accumulate procedural memory over time.

## Risks & Pitfalls

- **Token bloat**: Loading many skills simultaneously inflates the system prompt. Use bundles or progressive disclosure to keep costs bounded.
- **Security**: Third-party skills from `community` trust sources can be overridden with `--force`, but `dangerous` scan verdicts stay blocked.
- **Platform mismatch**: Skills with `platforms` restrictions are hidden on incompatible OSes — verify before relying on a skill.
- **Bundled skill drift**: User-modified bundled skills are skipped on update. Use `hermes skills reset` to re-baseline.

## Related Concepts

- [[concepts/hermes-persistent-memory]]
- [[concepts/hermes-agent-loop]]
- [[concepts/hermes-plugin-system]]
- [[entities/agentskills-io]]

## Sources

- `user-guide/features/skills.md`
- `developer-guide/creating-skills.md`
