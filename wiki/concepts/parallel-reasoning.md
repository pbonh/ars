---
title: "Parallel Reasoning"
type: concept
tags: [concept, llm-reasoning, test-time-scaling, inference]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/arxiv-2605.02396.pdf"]
confidence: high
---

## Definition

Parallel reasoning is the first stage of the heavy thinking pipeline, where K independent reasoning trajectories are generated simultaneously for the same problem. Each trajectory is produced by an independent agent (or sampling pass) without access to the others' outputs, ensuring diversity of approach and maximizing the chance that at least one trajectory contains a correct solution.

## How It Works

Given a problem q, the goal is to obtain a set of trajectories T_πθ(q, K) = {y₁, ..., y_K}, where πθ is the LLM and each trajectory yᵢ is a complete chain-of-thought leading to an answer. The generation uses high temperature (1.0) and nucleus sampling (top-p=0.95, top-k=10) to encourage diversity. In an agentic harness, each trajectory corresponds to a subagent call spawned in parallel.

The authors identify two key quality factors for this stage:
- **Quality** of individual trajectories (determined by base model capability)
- **Diversity** of approaches across trajectories (encouraged by high temperature and different problem-solving strategies)

## Key Parameters

| Parameter | Typical Value | Description |
|-----------|---------------|-------------|
| K | 8–16 | Number of parallel trajectories |
| Temperature | 1.0 | High temperature encourages diverse reasoning paths |
| Top-p | 0.95 | Nucleus sampling |
| Top-k | 10 | Token sampling limit |

## When To Use

Use parallel reasoning as the first phase of heavy thinking whenever:
- The problem is complex enough that a single reasoning attempt may fail
- The answer is verifiable (math, code, STEM)
- The inference budget allows for K parallel samples
- There is a deliberation stage downstream to synthesize results

## Risks & Pitfalls

- **Redundancy without diversity**: If all trajectories converge on the same incorrect approach, parallel reasoning provides no benefit.
- **Cost**: K parallel samples consume K× the inference budget of a single attempt.
- **Context pressure**: Full trajectories (especially from reasoning models with long chains) must be pruned before the deliberation stage.
- **Length bias**: The Max-Length selection heuristic performs worse than Random or Max-Answer-Num, indicating verbosity does not correlate with correctness.

## Related Concepts

- [[concepts/heavy-thinking]] — the parent two-stage pipeline
- [[concepts/sequential-deliberation]] — the second stage that consumes parallel outputs
- [[concepts/serialized-memory-cache]] — how parallel outputs are prepared for deliberation

## Sources

- Wang et al., "Heavy Skill: Heavy Thinking as the Inner Skill in Agentic Harness", arXiv:2605.02396, 2026.