---
title: "Wiki Lint"
type: concept
tags: [concept, knowledge-management, llm, workflow]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/llm-wiki.md"]
confidence: high
---

## Definition

**Wiki lint** is the periodic health-check operation on an LLM wiki. The LLM scans the wiki for structural and semantic problems — contradictions between pages, stale claims superseded by newer sources, orphan pages with no inbound links, missing concept pages, missing cross-references, and data gaps that could be filled with web search.

## How It Works

A typical lint flow:

1. **LLM reads the full set of wiki pages** (or a representative sample at large scale).
2. **Checks for contradictions:** Compare claims across concept pages and flag where newer sources contradict older ones.
3. **Checks for staleness:** Identify claims that reference outdated information and should be updated or deprecated.
4. **Checks for orphans:** Find pages with no inbound wiki-links that may be unreachable or irrelevant.
5. **Checks for missing pages:** Identify important concepts or entities mentioned inline but lacking their own page.
6. **Checks for broken cross-references:** Verify that all `[[...]]` links resolve to existing pages.
7. **Checks for data gaps:** Suggest web searches or new sources that would fill holes in the knowledge base.
8. **LLM reports findings** to the user and proposes fixes (updates, merges, new pages, deletions are rare — pages are edited, not deleted).
9. **User approves or refines** the proposed fixes; the LLM applies them.

## Key Parameters

| Check | Frequency | Severity |
|-------|-----------|----------|
| Contradictions | After every 3–5 ingests, or when sources are known to conflict | High |
| Stale claims | Weekly or monthly, depending on domain velocity | Medium |
| Orphan pages | Monthly | Low |
| Missing concept pages | After every ingest | Medium |
| Broken cross-references | After every ingest | High |
| Data gaps | As needed, or during dedicated research phases | Suggestion |

## When To Use

Run a lint pass when:
- You have ingested several sources and suspect the wiki is becoming inconsistent.
- You are about to write a synthesis or deliverable and need confidence that the underlying pages are coherent.
- You notice a contradiction while querying and want a systematic review.
- The wiki has grown beyond your ability to manually track every page.

Skip linting when:
- The wiki is very small (< 10 pages) and you can eyeball consistency.
- You are in rapid ingest mode and intend to lint after the batch completes.

## Risks & Pitfalls

- **False contradictions:** The LLM may flag a contradiction that is actually a nuanced distinction (e.g., two tools solve the same problem differently). Human review is essential before "resolving" a flagged contradiction.
- **Over-eager pruning:** The lint operation should edit pages, not delete them. A page that seems orphaned may be a hub that the link-checker missed. The schema should prohibit deletion.
- **Scope creep:** A lint pass can expand into a full rewrite of the wiki. Set boundaries: fix structural issues and obvious contradictions, but defer large-scale reorganization to a dedicated refactor session.
- **Stale index:** If `index.md` is not maintained during ingest, the lint pass may miss pages or misreport orphan status. The index should be a lint priority.
- **Automation fatigue:** If linting is too frequent or produces too much noise, the user stops paying attention. Calibrate frequency to wiki size and rate of change.

## Related Concepts

- [[concepts/llm-wiki-pattern]] — the pattern that defines lint as one of three core operations
- [[concepts/compounding-knowledge]] — linting keeps the compounding healthy
- [[concepts/wiki-ingest]] — lint often follows a batch of ingests
- [[concepts/agent-schema-document]] — the document that defines what checks to run and how to report them
- [[entities/skills-ref]] — a CLI tool for agent-skills validation; analogous idea in a different domain

## Sources

- [LLM Wiki](raw/llm-wiki.md) — Andrej Karpathy's description of the lint operation
