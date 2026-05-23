---
title: "Test Pyramid"
type: concept
tags: [concept, software-testing, strategy, python]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/"]
confidence: high
---

## Definition

The testing pyramid is a model that recommends the relative proportions of different testing types in a healthy test suite. The base is wide (many fast, granular tests) and the top is narrow (fewer slow, broad tests). It was first described by Mike Cohn in *Succeeding with Agile* (2009).

## How It Works

The pyramid has three main layers:

1. **Unit testing** (base, widest) — Verifies individual units (functions, methods, small classes) in isolation. These are fast, numerous, and provide the foundational safety net.
2. **Integration testing** (middle) — Verifies that multiple units work together correctly. These are fewer in number and slower than unit tests because they thread more code together.
3. **End-to-end / manual / load testing** (top, narrowest) — Verifies full workflows from the user's perspective or under realistic load. These are the most expensive and brittle, so they should be used conservatively and reserved for mission-critical paths.

The idea is to get the most "bang for your buck" by making sure the little pieces work, then making sure they work together. Automating the lower layers frees up time for exploratory testing and innovation.

## Key Parameters

- **Granularity**: Unit tests are most granular; end-to-end tests are least granular.
- **Speed**: Lower layers run faster; higher layers run slower.
- **Brittleness**: End-to-end tests span wide swathes of functionality, so a single broken step can fail the whole test.

## When To Use

Apply the test pyramid as a rule of thumb when designing a testing strategy:
- Invest most effort in unit tests for new code.
- Add integration tests at system boundaries (databases, APIs, external services).
- Reserve end-to-end and load tests for high-value business workflows.

## Risks & Pitfalls

- **Inverted pyramid (ice cream cone)**: Some teams write many slow UI tests and few unit tests, leading to long build times and late feedback.
- **Testing only at the top**: Without unit and integration tests, failures in end-to-end tests are hard to diagnose because they could stem from any layer.

## Related Concepts

- [[concepts/test-driven-development]] — TDD produces the unit-test base of the pyramid

## Sources

- *Practices of the Python Pro*, Chapter 5 — Testing your software
