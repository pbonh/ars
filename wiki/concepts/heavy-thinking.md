---
title: "Heavy Thinking"
type: concept
tags: [concept, llm-reasoning, test-time-scaling, agentic-harness, ai-research]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/arxiv-2605.02396.pdf"]
confidence: high
---

## Definition

Heavy thinking is a test-time scaling (TTS) strategy that decomposes complex problem-solving into two distinct stages executed by a single LLM: (1) **parallel reasoning** — generating multiple independent reasoning trajectories for the same problem, and (2) **sequential deliberation** — critically analyzing and synthesizing those trajectories to produce a superior final answer. It can be viewed as an *inner skill* internalized within the model's parameters rather than an artifact of external orchestration infrastructure.

## How It Works

The inference pipeline operates as follows:

1. A user query arrives.
2. The model (or orchestrator) spawns **K independent reasoning agents** in parallel, each solving the problem from scratch without seeing the others' work.
3. The resulting trajectories are pruned, shuffled, and serialized into a **memory cache** to fit within context limits.
4. A second reasoning pass (which may use the same or a different model) performs **sequential deliberation** over the cached trajectories, analyzing differences, identifying errors, and synthesizing the best answer.
5. Optionally, the deliberation output can be fed back into the cache for **iterative refinement**.

## Key Parameters

| Parameter | Typical Value | Description |
|-----------|-------------|-------------|
| K (parallel trajectories) | 8–16 | Number of independent reasoning paths generated |
| K^(1) (deliberation outputs) | 4 | Number of summary attempts in deliberation |
| N (iterations) | 1–4 | Number of iterative deliberation rounds |
| Temperature | 1.0 | High temperature encourages trajectory diversity |
| Top-p | 0.95 | Nucleus sampling for parallel generation |
| Top-k | 10 | Limits token sampling diversity |

## When To Use

Activate heavy thinking when:
- The task involves complex mathematical or STEM reasoning
- The problem requires deep logical deduction
- The task is a code competition or algorithmic challenge
- Correctness is critical and verifiable
- A single chain-of-thought may be insufficient or error-prone

Avoid for:
- Simple factual questions
- Casual conversation
- Straightforward code edits with obvious solutions
- Information-retrieval tasks without reasoning depth

## Risks & Pitfalls

- **Context window limits**: Serializing complete trajectories can exceed model context length; pruning is necessary but may discard useful reasoning.
- **Iterative degradation**: While HM@K improves with iteration, HP@K can degrade due to cumulative noise and bias from prior deliberation steps.
- **Preference-oriented tasks**: Gains are marginal or negative on subjective alignment tasks (e.g., Arena-Hard), where correctness-oriented synthesis does not match stylistic nuance.
- **Deliberation model dependency**: The deliberation stage relies heavily on general capability (instruction following, synthesis) rather than peak intrinsic reasoning power.
- **RLVR instability**: Training on K=16 trajectories can cause entropy collapse due to sequence length limits; K=8 shows more stable RL training.

## Related Concepts

- [[concepts/parallel-reasoning]] — the first stage of heavy thinking
- [[concepts/sequential-deliberation]] — the second stage of heavy thinking
- [[concepts/serialized-memory-cache]] — mechanism bridging the two stages
- [[concepts/iterative-deliberation]] — recursive refinement extension
- [[concepts/readable-skill]] — skill-document distillation of heavy thinking
- [[concepts/heavy-thinking-rlvr]] — reinforcement learning optimization

## Sources

- Wang et al., "Heavy Skill: Heavy Thinking as the Inner Skill in Agentic Harness", arXiv:2605.02396, 2026.