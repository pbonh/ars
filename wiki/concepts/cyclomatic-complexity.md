---
title: "Cyclomatic Complexity"
type: concept
tags: [concept, code-quality, metrics, python]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/"]
confidence: high
---

## Definition

Cyclomatic complexity is a quantitative measure of the number of execution paths through a function or method. It was developed by Thomas J. McCabe in 1976 and is calculated by counting the conditional expressions and loops in a control flow graph. The higher the score, the more branches the code has, and the harder it tends to be to understand, test, and maintain.

## How It Works

To calculate cyclomatic complexity manually:

1. Draw a control flow graph of the function.
2. Count the nodes (decision points: `if`, `elif`, `else`, `for`, `while`, `return`, start, end).
3. Count the edges (paths between nodes).
4. Apply the formula: **M = E − N + 2**

For example, a function with 8 nodes and 10 edges has a cyclomatic complexity of **M = 10 − 8 + 2 = 4**.

Most sources recommend keeping complexity at **10 or lower** for a given function or method. This corresponds roughly to how much a developer can reasonably understand at once.

### Connection to testing
Cyclomatic complexity also predicts the minimum number of distinct test cases needed to cover every execution path. Each `if`, `while`, or `for` introduces a new branch that requires a different set of preconditions to test.

## Key Parameters

- **M**: The cyclomatic complexity score.
- **Nodes**: Start of function, `if`/`elif`/`else`, `for`, `while`, end of loop, `return`.
- **Edges**: Arrows connecting nodes along possible execution paths.

## When To Use

Measure cyclomatic complexity when:
- You need an objective signal for which code has grown too complex and should be refactored.
- You are setting code-quality gates in CI/CD.
- You want to identify areas where test coverage is likely insufficient (untested branches).

## Risks & Pitfalls

- **Not a panacea**: High complexity accurately flags code that is hard to read, but low complexity does not guarantee correctness or absence of bugs.
- **Context matters**: A function with complexity 12 that clearly maps a set of business rules may be acceptable; a function with complexity 8 that mixes unrelated concerns is worse.
- **Don't game the metric**: Combining conditions into one-line expressions or removing braces to reduce the count syntactically without simplifying logic is counterproductive.

## Related Concepts

- [[concepts/decomposition]] — the primary remedy for high cyclomatic complexity
- [[concepts/big-o-notation]] — another complexity measure, but for algorithms rather than code structure

## Sources

- *Practices of the Python Pro*, Chapter 9 — Keeping things lightweight
