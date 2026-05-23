---
title: "Big O Notation"
type: concept
tags: [concept, algorithms, performance, python, complexity-analysis]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/"]
confidence: high
---

## Definition

Big O notation is a shorthand used in asymptotic analysis to describe the worst-case performance of an algorithm as its inputs grow. It expresses how much more execution time, memory, or disk storage software needs relative to the size of its inputs. It is not an exact quantitative measurement, but a qualitative tool for contrasting different ways of achieving the same task.

## How It Works

Common complexity classes, from best to worst:

- **O(1) — Constant time/space**: Does not depend on input size. Ideal. Python `dict` and `set` lookups, insertions, and deletions are O(1) on average.
- **O(n) — Linear**: Time or space grows proportionally with the number of inputs. A single `for` loop over a list is typically O(n).
- **O(n²) — Quadratic**: Time grows proportional to the square of inputs. Nested loops over the same sequence often produce O(n²).

Other notations include big Ω (best-case) and big θ (tight bounds when upper and lower are the same), though big O is the most commonly used.

### Time complexity
Measures how quickly code performs a task as inputs increase. A steeply linear O(n) task may be slower than an O(n²) task for small inputs, but given enough inputs, the higher-order complexity always dominates.

### Space complexity
Measures how memory or disk usage grows with inputs. For example, reading an entire multi-gigabyte file into a list is O(n) space; reading it line-by-line in a `for` loop is O(1) space because only the current line is held in memory.

## Key Parameters

- **n**: The variable representing the number of inputs.
- **Worst case**: Big O always measures the worst-case scenario to give an upper bound on what the code is capable of.
- **Apples to apples**: Complexity is useful for comparing algorithms that solve the same task, not unrelated tasks.

## When To Use

Use complexity analysis when:
- You have multiple candidate algorithms for the same task and need to choose one.
- You suspect nested loops or large in-memory structures will become bottlenecks at scale.
- You want to justify a design decision (e.g., using a `set` instead of a `list` for membership checks).
- You need to communicate performance characteristics to teammates in a compact, standard form.

## Risks & Pitfalls

- **Premature optimization**: Don't optimize before measuring. "Make it work, make it right, make it fast"—complexity analysis belongs in the "make it fast" phase.
- **Ignoring constants**: Big O drops constant factors. An O(n) algorithm with a huge constant may be slower than another O(n) algorithm for realistic input sizes.
- **Real-world variance**: Actual performance depends on hardware, Python's garbage collector, and other runtime factors. Use tools like `timeit` and `cProfile` to verify hypotheses.

## Related Concepts

- [[concepts/lazy-evaluation]] — reduces space complexity by producing values one at a time
- [[concepts/cyclomatic-complexity]] — measures code structural complexity, not algorithmic complexity

## Sources

- *Practices of the Python Pro*, Chapter 4 — Designing for high performance
