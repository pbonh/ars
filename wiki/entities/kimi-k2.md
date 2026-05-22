---
title: "Kimi K2"
type: entity
tags: [entity, llm, reasoning-model, moonshot-ai]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/arxiv-2605.02396.pdf"]
confidence: high
---

## Overview

Kimi K2 is a large language model developed by Moonshot AI (Bai et al., 2025), cited in the Heavy Skill paper as one of the early implementations demonstrating heavy thinking capabilities. It decomposes reasoning into two distinct stages: a parallel reasoning stage that provides independent trajectories, followed by a sequential deliberation stage that aggregates them.

## Characteristics

- **Architecture**: Close-weight model from Moonshot AI
- **Reasoning mode**: Native heavy thinking support with explicit two-stage decomposition
- **Performance**: Achieves near-perfect scores on several STEM benchmarks when combined with heavy thinking (e.g., 95.4% on AIME25 with K=8)
- **Relationship to Heavy Skill**: Serves as empirical evidence that heavy thinking patterns can be natively built into model architecture and training rather than only orchestrated externally

## Common Strategies

- Used as a reference implementation for heavy thinking in model design
- Benchmarked in Heavy Skill experiments showing strong Pass@K and Heavy-Mean@K performance
- Compared against other frontier models (GPT-5-Thinking, Claude 4.5 Thinking, Gemini 3 Pro Preview)

## Sources

- Bai et al., "Kimi K2: open agentic intelligence", CoRR abs/2507.20534, 2025.
- Wang et al., "Heavy Skill: Heavy Thinking as the Inner Skill in Agentic Harness", arXiv:2605.02396, 2026.