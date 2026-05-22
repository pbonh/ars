---
title: "Iterative Deliberation"
type: concept
tags: [concept, llm-reasoning, iterative-refinement, test-time-scaling]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/arxiv-2605.02396.pdf"]
confidence: high
---

## Definition

Iterative deliberation is an optional extension of the heavy thinking framework in which the sequential deliberation stage is executed repeatedly. At each iteration t ≥ 2, the memory cache is augmented by concatenating the previous deliberation output back into the serialized context, allowing the model to progressively refine its reasoning by revisiting and synthesizing prior attempts.

## How It Works

1. **Round 1**: Execute standard parallel reasoning (K trajectories) → sequential deliberation (K^(1) summary outputs).
2. **Round t**: Modify the memory cache:
   - x_c^(t) = T_πϕ(x_c^(t-1), K^(t-1)) || x_c^(t-1)
   - The previous deliberation output is appended to the existing cache.
3. **Repeat**: Up to N iterations (typically N = 2–4).

Empirical results show a consistent upward trend in Heavy-Mean@K as iterations increase, demonstrating intrinsic scaling capabilities. However, Heavy-Pass@K degrades with iteration, suggesting that subsequent steps introduce cumulative noise or bias that constrains refinement space.

## Key Parameters

| Parameter | Typical Value | Description |
|-----------|---------------|-------------|
| N | 2–4 | Total number of deliberation iterations |
| K^(t) | 8 | Number of outputs per iteration (often fixed across rounds) |

## When To Use

Use iterative deliberation when:
- The problem is extremely challenging and single-pass deliberation is insufficient
- Inference budget allows for multiple sequential stages
- The task is correctness-oriented with verifiable answers

Avoid when:
- Latency or cost constraints are tight (each iteration adds sequential delay)
- The problem is simple enough that one deliberation pass suffices
- Working with smaller models where iterative noise accumulation outweighs gains

## Risks & Pitfalls

- **HP@K degradation**: While average performance (HM@K) improves, the best-case potential (HP@K) degrades, indicating that iterative depth trades off against information consistency.
- **Cumulative bias**: Each iteration may reinforce errors or biases from prior rounds.
- **Cost**: Iterations multiply the sequential inference cost.
- **Diminishing returns**: Gains typically plateau after 2–3 iterations.

## Related Concepts

- [[concepts/heavy-thinking]] — the parent pipeline
- [[concepts/sequential-deliberation]] — the stage being iterated
- [[concepts/serialized-memory-cache]] — modified at each iteration

## Sources

- Wang et al., "Heavy Skill: Heavy Thinking as the Inner Skill in Agentic Harness", arXiv:2605.02396, 2026.