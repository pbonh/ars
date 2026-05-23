---
title: "Test-Driven Development"
type: concept
tags: [concept, software-testing, agile, python]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/"]
confidence: high
---

## Definition

Test-driven development (TDD) is a school of thought in which tests are written before the implementation code they verify. The practice puts testing first, guiding developers toward a working implementation based on explicit requirements. TDD is both a mindset and a philosophy that influences how developers think about correctness, edge cases, and design.

## How It Works

The TDD cycle is often described as:

1. **Write a failing test** that describes a desired behavior.
2. **Write the minimum code** needed to make the test pass.
3. **Refactor** the code while keeping the test green.

TDD encourages developers to be "chaos engineers"—to deliberately think of extremes that code can endure and throw them at it. In Python, the exception system allows code to respond predictably to rare or unexpected situations.

Coverage is a useful metric, but increasing coverage beyond a certain point can have diminishing returns. The goal is not to test every line at all costs, but to use tests as a specification and a safety net.

## Key Parameters

- **Red-green-refactor**: The canonical TDD loop.
- **Test as specification**: A good test reads like a requirement. "Given the list [1, 2, 3, 4], the expected output of `calculate_mean` is 2.5."
- **Behavior-driven development (BDD)**: A related practice that frames tests in natural language from the user's perspective, often using tools like Cucumber.

## When To Use

Use TDD when:
- You want tests to drive design and surface unclear requirements early.
- You need confidence to refactor aggressively without breaking existing behavior.
- You are working on critical business logic where regressions are costly.
- You want to reduce the feedback loop between writing code and verifying correctness.

## Risks & Pitfalls

- **Brittle tests**: If awkwardness is introduced only to make testing easier or coverage stronger, the code may suffer. Refactor to make testing easier *and* the code more coherent.
- **Tight coupling in tests**: Tests that mirror implementation structure too closely break often when the implementation changes. Aim to verify outcomes, not internal steps.
- **Not a silver bullet**: TDD does not guarantee bug-free software. It is a discipline for building confidence and catching regressions.

## Related Concepts

- [[concepts/test-pyramid]] — guides where to invest testing effort

## Sources

- *Practices of the Python Pro*, Chapter 5 — Testing your software
