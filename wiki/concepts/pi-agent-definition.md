---
title: "Pi Agent Definition"
type: concept
tags: [concept, pi, subagent, configuration, frontmatter]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/pi-subagents-readme.md"]
confidence: high
---

## Definition

A Pi agent definition is a Markdown file with YAML frontmatter and a system
prompt body that declares the specialist a [[concepts/pi-subagent|subagent]]
runs as. The frontmatter sets the model, tools, skills, context-inheritance,
and output behavior; the body is the system prompt loaded into the child Pi
process.

## How It Works

### Discovery and precedence

Agents are discovered from three scopes, lowest to highest priority:

| Scope | Path |
|-------|------|
| Builtin | `~/.pi/agent/extensions/subagent/agents/` |
| User | `~/.pi/agent/agents/**/*.md` |
| Project | `.pi/agents/**/*.md` (legacy `.agents/**/*.md` also read) |

Nested subdirectories are discovered recursively. On a runtime-name collision,
`.pi/agents/` wins over legacy `.agents/`, and project wins over user.
`agentScope: "user" | "project" | "both"` controls discovery; `both` is the
default. Because builtins load at lowest priority, a user or project agent with
the same name overrides a builtin.

### Frontmatter fields

Important fields include `name`, optional `package` (registers a runtime name
`{package}.{name}`), `tools`, `extensions`, `model`, `fallbackModels`,
`thinking`, `systemPromptMode`, `inheritProjectContext`, `inheritSkills`,
`defaultContext`, `skills`, `output`, `defaultReads`, `defaultProgress`,
`completionGuard`, and `maxSubagentDepth`.

### Prompt assembly

Custom agents are narrow by default — they do **not** inherit Pi's whole base
prompt, project instruction files, or the discovered [[concepts/pi-skill|skills]]
catalog. Opt in with:

| Field | Effect |
|-------|--------|
| `systemPromptMode: append` | Append the agent prompt to Pi's base prompt (`replace` is default). |
| `inheritProjectContext: true` | Keep `AGENTS.md` / `CLAUDE.md` style project instructions. |
| `inheritSkills: true` | Let the child see Pi's discovered skills catalog. |
| `defaultContext: fork` | Use [[concepts/pi-forked-context|forked]] context when a launch omits `context`. |

Builtins opt into project-instruction inheritance by default; `delegate` also
uses append mode because its job is orchestration inside the parent workflow.

### Builtin overrides

Instead of copying a whole builtin, override selected fields via
`subagents.agentOverrides.<name>` in `~/.pi/agent/settings.json` (user) or
`.pi/settings.json` (project, which beats user). Overridable fields: `model`,
`fallbackModels`, `thinking`, `systemPromptMode`, `inheritProjectContext`,
`inheritSkills`, `defaultContext`, `disabled`, `skills`, `tools`,
`systemPrompt`. Set `disabled: true` to hide one builtin, or
`subagents.disableBuiltins: true` for all.

### Tool selection

If `tools` is omitted, the child gets Pi's normal builtin tools. If present,
plain names become an explicit allowlist; `mcp:` entries forward direct MCP
tools (require [[entities/pi-mcp-adapter]]); path-like entries are treated as
tool-extension paths. Agents declaring only known read-only tools skip the
implementation completion guard; `completionGuard: false` exempts bash-enabled
validators/advisors from being judged as implementation agents. `tools: subagent`
authorizes child-safe nested fanout (see
[[concepts/pi-subagent-recursion-guard]]).

## Key Parameters

- Builtin agents do not pin a provider model; they inherit the current Pi
  default model unless `subagents.agentOverrides.<name>.model` is set.
- A one-off model override is inline: `/run reviewer[model=anthropic/claude-sonnet-4:high] "..."`.

## When To Use

- Define a custom agent when you need a repeatable specialist with a fixed
  prompt, tool allowlist, and model.
- Prefer `agentOverrides` for ordinary tweaks to a builtin; create a same-named
  user/project agent only when you want a totally different agent.

## Risks & Pitfalls

- Forgetting that agents are narrow by default — an agent that needs project
  rules must set `inheritProjectContext: true`.
- Name collisions across scopes silently resolve by precedence; check
  `subagent({ action: "list" })` to confirm which definition wins.
- `model` bare ids resolve by current provider then unique registry match; an
  ambiguous id can pick an unexpected model.

## Related Concepts

- [[concepts/pi-subagent]]
- [[concepts/pi-subagent-chain]]
- [[concepts/pi-skill]]
- [[concepts/pi-forked-context]]
- [[concepts/pi-subagent-child-safety-boundary]]

## Sources

- [pi-subagents README](raw/pi-subagents-readme.md)
</content>
