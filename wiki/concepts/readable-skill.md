---
title: "Readable Skill"
type: concept
tags: [concept, agentic-harness, llm-prompting, skill-system]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/arxiv-2605.02396.pdf"]
confidence: high
---

## Definition

A readable skill is a structured natural-language document that serves as an executable specification for an LLM orchestrator in an agentic harness. It specifies when to activate, how to execute a capability, and what to output — all without requiring code changes to the harness itself. The skill is loaded into the orchestrator's context window at inference time, and the orchestrator autonomously executes the prescribed protocol via its in-context learning capability.

## How It Works

A readable skill document typically contains four components:

1. **Activation Conditions** — Declarative rules for when the skill should trigger (e.g., "activate when facing complex reasoning tasks; remain dormant for simple factual queries"). This ensures additional inference cost is only incurred when justified.

2. **Execution Protocol** — Step-by-step instructions for the orchestrator. In the Heavy Skill example, this includes spawning K independent reasoning agents in parallel, collecting their outputs into a serialized memory cache, and performing deliberation in a subsequent generation step.

3. **Deliberation Prompt** — A carefully designed prompt template for the synthesis stage that instructs the model to classify query type, critically evaluate each trajectory, re-derive if all are wrong, and maintain format consistency.

4. **Output Constraints** — Rules for the final response (e.g., contain only the answer, follow domain format conventions, match the original query language).

Because the skill is plain text with no framework-specific dependencies, the same document can be injected into any harness that supports skill loading and subagent spawning. The authors verified the same Heavy Skill document works under both Claude Code and custom orchestration harnesses without modification.

## Key Parameters

| Component | Purpose |
|-----------|---------|
| Activation conditions | Gate skill invocation by task complexity |
| Parallel reasoning protocol | Spawn K independent subagents |
| Deliberation prompt | Guide critical synthesis |
| Output constraints | Enforce format and content rules |

## When To Use

Use a readable skill when:
- You want to add a capability to an agentic harness without modifying harness code
- The capability can be expressed as procedural instructions
- The target orchestrator has strong in-context learning and subagent spawning support
- Portability across multiple harnesses (Claude Code, Hermes, custom) is desired

## Risks & Pitfalls

- **Orchestrator capability dependency**: The harness must support skill loading and parallel subagent spawning; weaker orchestrators may fail to execute multi-step protocols faithfully.
- **Instruction ambiguity**: Natural-language specifications can be misinterpreted; the skill must be carefully written to avoid ambiguous steps.
- **No runtime validation**: Unlike code, a readable skill has no compile-time or static checks; errors manifest as misbehavior at inference time.
- **Context overhead**: The skill document itself consumes context window space.

## Related Concepts

- [[concepts/heavy-thinking]] — the canonical example of a readable skill
- [[concepts/agent-skills-format]] — related agent-skills specification from agentskills-io
- [[entities/claude-code]] — a harness supporting readable skills
- [[entities/hermes-agent]] — a harness supporting readable skills

## Sources

- Wang et al., "Heavy Skill: Heavy Thinking as the Inner Skill in Agentic Harness", arXiv:2605.02396, 2026.