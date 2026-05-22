---
title: "Sequential Deliberation"
type: concept
tags: [concept, llm-reasoning, synthesis, agentic-harness]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/arxiv-2605.02396.pdf"]
confidence: high
---

## Definition

Sequential deliberation is the second stage of the heavy thinking pipeline, where a model πϕ critically analyzes and synthesizes multiple reasoning trajectories produced during the parallel reasoning stage. Rather than simply voting or selecting the most common answer, the deliberation model evaluates the logical soundness of each trajectory, compares approaches, and synthesizes a superior final answer — even re-deriving the solution from scratch if all input trajectories are judged incorrect.

## How It Works

After parallel reasoning produces K trajectories, they are serialized into a memory cache C(x_c). The deliberation model receives:
- The original problem
- The serialized trajectories (pruned and shuffled to prevent position bias)
- A carefully designed prompt that instructs the model to:
  1. Classify the query type to determine analysis depth
  2. Critically evaluate each thinker's reasoning rather than naively following the majority
  3. Re-derive the answer when all thinkers are judged incorrect
  4. Maintain language and format consistency with the original query

The output is a summary analysis followed by a definitive final answer containing only the answer (no meta-analysis). Format conventions must match the domain (e.g., `\boxed{}` for math, code blocks for programming).

## Key Parameters

| Parameter | Typical Value | Description |
|-----------|---------------|-------------|
| K^(1) | 4 | Number of deliberation attempts generated |
| Model πϕ | Same or different from πθ | Can be a larger instruction-following model |

## When To Use

Sequential deliberation is required whenever:
- Multiple parallel reasoning trajectories have been generated
- The problem demands correctness over speed
- The task has clear right/wrong answers (STEM, code, verifiable reasoning)
- There is sufficient context window to hold the serialized cache

It is less effective for preference-oriented tasks (e.g., chat alignment, open-ended creative writing) where stylistic nuance matters more than logical correctness.

## Risks & Pitfalls

- **Majority bias**: The prompt must explicitly instruct the model *not* to default to the most frequent answer, because the correct answer may come from very few or even zero input trajectories.
- **Superficial concatenation**: Without careful prompting, the model may simply echo or average inputs rather than genuinely synthesize.
- **Context truncation**: Pruned trajectories may lose critical reasoning steps.
- **Model capability dependency**: The deliberation stage relies more on general synthesis and instruction-following capability than on peak intrinsic reasoning power. Counter-intuitively, a model like Qwen2.5-32B-Instruct with lower solo reasoning scores can still deliver strong deliberation gains.

## Related Concepts

- [[concepts/heavy-thinking]] — the parent two-stage pipeline
- [[concepts/parallel-reasoning]] — the stage that produces inputs for deliberation
- [[concepts/serialized-memory-cache]] — the context format consumed by deliberation
- [[concepts/iterative-deliberation]] — recursive application of deliberation

## Sources

- Wang et al., "Heavy Skill: Heavy Thinking as the Inner Skill in Agentic Harness", arXiv:2605.02396, 2026.