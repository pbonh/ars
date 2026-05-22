---
title: "Heavy Thinking RLVR"
type: concept
tags: [concept, llm-reasoning, reinforcement-learning, test-time-scaling]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/arxiv-2605.02396.pdf"]
confidence: medium
---

## Definition

Heavy Thinking RLVR is the application of Reinforcement Learning from Verifiable Rewards (RLVR) to heavy thinking trajectories, treating both the parallel reasoning stage (breadth) and the sequential deliberation stage (depth) as jointly optimizable via outcome-based rewards. The goal is to push a model's reasoning capabilities beyond the limits achievable with a fixed base model and pure test-time sampling.

## How It Works

The authors reuse parallel reasoning trajectories generated during experiments, select queries with pass rates in [0, 0.625], and sample K ∈ {8, 16} trajectories to form serialized memory caches. Training is performed using:

- **Framework**: VeRL (HybridFlow)
- **Algorithm**: GSPO (Group Sequence Policy Optimization)
- **Backbone**: R1-Distill-Qwen-7B
- **Reward**: Outcome-based verifiable rewards from math/coding tasks

The training optimizes the model to improve both:
- **Reasoning breadth** — quality and diversity of parallel trajectories
- **Reasoning depth** — quality of deliberation over those trajectories

Results show approximately 10% improvement in HM@4 during the first 100 training steps. However, stability diverges by K: K=16 suffers entropy collapse after ~100 steps, while K=8 remains stable throughout. The authors attribute this to maximum sequence length limitations when handling longer serialized contexts.

## Key Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| K | 8 or 16 | Number of trajectories per training sample |
| RL framework | VeRL | HybridFlow RLHF framework |
| RL algorithm | GSPO | Group Sequence Policy Optimization |
| Backbone | R1-Distill-Qwen-7B | Base reasoning model |
| Query filter | pass rate ∈ [0, 0.625] | Focus on hard queries where heavy thinking has headroom |

## When To Use

Consider Heavy Thinking RLVR when:
- A base model already demonstrates heavy thinking capability but needs optimization
- The task domain provides verifiable rewards (math, code, formal logic)
- Sufficient compute is available for RL training on long serialized contexts
- The target model has enough context length to handle K=8 or K=16 trajectories without truncation

## Risks & Pitfalls

- **Entropy collapse**: K=16 configurations can become unstable due to context length pressure.
- **Sequence length limits**: Smaller models may truncate or receive suboptimal training signals on long caches.
- **Narrow reward signal**: Outcome-based rewards provide sparse gradients; step-wise rewards may help but are not explored in this paper.
- **Early-stage dynamics**: Most gains occur in the first 100 steps; long-horizon training behavior is not well characterized.

## Related Concepts

- [[concepts/heavy-thinking]] — the parent pipeline being optimized
- [[concepts/parallel-reasoning]] — the breadth component optimized by RL
- [[concepts/sequential-deliberation]] — the depth component optimized by RL
- [[concepts/serialized-memory-cache]] — the long context that causes RL instability

## Sources

- Wang et al., "Heavy Skill: Heavy Thinking as the Inner Skill in Agentic Harness", arXiv:2605.02396, 2026.