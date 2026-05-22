---
title: "Serialized Memory Cache"
type: concept
tags: [concept, llm-reasoning, context-window, agentic-harness]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/arxiv-2605.02396.pdf"]
confidence: high
---

## Definition

The serialized memory cache is a context-bridging mechanism in the heavy thinking framework that stores, prunes, and organizes the candidate trajectories generated during the parallel reasoning phase so they can be fed into the sequential deliberation stage. It is a serialized text context C(x_c) that balances completeness against the model's maximum context length limit.

## How It Works

1. **Collection**: After parallel reasoning completes, K trajectories are collected. Each trajectory typically contains extensive internal thinking content plus an answer.
2. **Pruning**: Complete trajectories often exceed available context when K is large (e.g., 8–16). The cache prunes trajectories to fit within length limits while preserving the reasoning structure and final answer.
3. **Shuffling**: The pruned trajectories are shuffled before serialization to prevent the deliberation model from developing position bias (e.g., overweighting the first or last trajectory).
4. **Formatting**: Trajectories are formatted with clear delimiters (e.g., `# ----- Thinker #1 -----`) and assembled into a single serialized prompt alongside the original problem and the deliberation instructions.
5. **Iteration support**: In iterative deliberation, the cache is modified by concatenating previous deliberation outputs back into the context for recursive refinement.

## Key Parameters

| Concern | Technique | Rationale |
|---------|-----------|-----------|
| Length limit | Pruning | Full reasoning chains are too long to serialize completely |
| Position bias | Shuffling | Prevents the deliberation model from favoring early/late trajectories |
| Readability | Delimiters | Clear separation between independent thinkers |

## When To Use

Use a serialized memory cache whenever:
- Bridging parallel reasoning outputs to a sequential deliberation stage
- Multiple independent agent outputs must be synthesized by a single model call
- Context window constraints require pruning or summarization of intermediate results
- Iterative refinement requires appending prior synthesis back into the context

## Risks & Pitfalls

- **Information loss**: Pruning may remove intermediate reasoning steps that the deliberation model needs to verify correctness.
- **Sequence length ceiling**: For K=16 with long reasoning models (e.g., DeepSeek R1), even pruned trajectories may hit context limits, causing truncation.
- **RLVR instability**: When K=16, RL training on serialized caches can suffer entropy collapse because the long context exceeds effective training capacity for smaller models.

## Related Concepts

- [[concepts/heavy-thinking]] — the parent pipeline using the cache
- [[concepts/parallel-reasoning]] — produces the trajectories stored in the cache
- [[concepts/sequential-deliberation]] — consumes the cache as input
- [[concepts/iterative-deliberation]] — modifies the cache across rounds

## Sources

- Wang et al., "Heavy Skill: Heavy Thinking as the Inner Skill in Agentic Harness", arXiv:2605.02396, 2026.