---
title: "HeavySkill"
type: entity
tags: [entity, ai-research, project, llm-reasoning]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/arxiv-2605.02396.pdf"]
confidence: high
---

## Overview

HeavySkill is a research project and perspective introduced by Wang et al. from the Meituan LongCat Team and Peking University in May 2026. It proposes that "heavy thinking" — parallel reasoning followed by sequential deliberation — is not merely an orchestration pattern in agentic harnesses but an *inner skill* that can be internalized within a single LLM's parameters. The project includes a training-free framework, a serialized memory cache mechanism, an iterative deliberation protocol, and a portable readable skill document.

## Characteristics

- **Training-free framework**: Can be executed immediately on any capable LLM or agentic harness without fine-tuning.
- **Readable skill document**: A plain-text, human-readable specification that Claude Code, Hermes, and custom harnesses can interpret and autonomously execute.
- **Open-source artifacts**: The paper references https://github.com/wjn1996/HeavySkill for implementation resources.
- **RLVR extension**: Demonstrates how reinforcement learning from verifiable rewards can optimize both reasoning breadth and depth within the heavy thinking paradigm.

## Common Strategies

- Deploy as a readable skill in [[entities/claude-code]] or [[entities/hermes-agent]] by loading the HeavySkill.md document into the orchestrator context.
- Use K=8 parallel trajectories for stable RLVR training; avoid K=16 with smaller models due to entropy collapse.
- Apply primarily to correctness-oriented tasks (math, code, STEM) rather than preference-oriented tasks (chat alignment).
- Combine with frontier models (GPT-5-Thinking, DeepSeek R1-0528, Kimi K2 Thinking) to approach Pass@K upper bounds.

## Sources

- Wang et al., "Heavy Skill: Heavy Thinking as the Inner Skill in Agentic Harness", arXiv:2605.02396, 2026.
- https://github.com/wjn1996/HeavySkill