---
title: "Heavy Skill: Heavy Thinking as the Inner Skill in Agentic Harness"
type: summary
tags: [summary, ai-research, llm-reasoning, agentic-harness, test-time-scaling]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/arxiv-2605.02396.pdf"]
confidence: high
---

## Overview

This paper by Wang et al. (Meituan LongCat Team / Peking University) proposes **Heavy Skill** — a perspective that treats "heavy thinking" not merely as an orchestration pattern in agentic harnesses, but as an *inner skill* internalized within a single LLM's parameters. The authors argue that complex agentic harnesses (Claude Code, Hermes, CodeX, OpenClaw) achieve their success largely through a two-stage pipeline that can be abstracted and executed directly by a capable LLM without brittle external infrastructure.

The core insight is that heavy thinking decomposes into **parallel reasoning** (generating multiple independent reasoning trajectories for the same problem) followed by **sequential deliberation** (critically synthesizing those trajectories into a final answer). The authors provide a training-free framework, a serialized memory cache mechanism, and an iterative refinement protocol. They conduct extensive experiments across STEM, coding, and general reasoning benchmarks, showing that heavy thinking consistently outperforms single-trajectory reasoning and traditional Best-of-N / majority-voting strategies. Stronger models can even approach their theoretical Pass@K upper bounds. Finally, they show that reinforcement learning from verifiable rewards (RLVR) can be applied to heavy thinking trajectories to further scale both reasoning breadth and depth.

## Key Claims

- Heavy thinking is an *inner skill* — a two-stage pipeline of [[concepts/parallel-reasoning]] then [[concepts/sequential-deliberation]] — that can operate beneath any agentic harness, not just an artifact of system design.
- The framework introduces a [[concepts/serialized-memory-cache]] to bridge the two phases: trajectories are pruned, shuffled, and serialized to fit context limits while preventing position bias.
- [[concepts/iterative-deliberation]] enables recursive refinement by feeding prior deliberation outputs back into the memory cache.
- The authors distill the workflow into a [[concepts/readable-skill]] — a plain-text, human-readable document that any sufficiently capable LLM orchestrator can interpret and autonomously execute.
- Performance hierarchy on verifiable STEM tasks: Heavy-Pass@k ≥ Heavy-Mean@K ≥ Vote@K ≥ Mean@k. Frontier models approach Pass@k bounds.
- [[concepts/heavy-thinking-rlvr]] can optimize both reasoning breadth (via parallel generation) and depth (via deliberation), offering a path toward self-evolving LLMs.

## Source Metadata

- **Type**: Preprint / Research Paper
- **Authors**: Jianing Wang, Linsen Guo, Zhengyu Chen, Qi Guo, Hongyu Zang, Wenjie Shi, Haoxiang Ma, Xiangyu Xi, Xiaoyu Li, Wei Wang, Xunliang Cai
- **Affiliation**: Meituan LongCat Team; National Engineering Research Center for Software Engineering, Peking University
- **URL**: https://arxiv.org/abs/2605.02396
- **License**: arXiv preprint (assumed standard arXiv license)
- **Ingested-on**: 2026-05-21

## Relevant Concepts

- [[concepts/heavy-thinking]] — the central two-stage reasoning paradigm
- [[concepts/parallel-reasoning]] — generating multiple independent trajectories
- [[concepts/sequential-deliberation]] — critical synthesis of trajectories
- [[concepts/serialized-memory-cache]] — context bridging mechanism
- [[concepts/iterative-deliberation]] — recursive refinement loop
- [[concepts/readable-skill]] — transferable skill document format
- [[concepts/heavy-thinking-rlvr]] — RL optimization of heavy thinking

## Relevant Entities

- [[entities/heavyskill]] — the paper and open-source project
- [[entities/kimi-k2]] — Moonshot AI model cited as an early heavy-thinking implementation
- [[entities/pacore]] — StepFun-AI's parallel coordinated reasoning framework
- [[entities/longcat-flash-thinking]] — Meituan LongCat Team's own reasoning model
- [[entities/claude-code]] — agentic harness mentioned as a skill-loading target
- [[entities/hermes-agent]] — agentic harness mentioned as a skill-loading target