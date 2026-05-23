---
title: "Decomposition"
type: concept
tags: [concept, software-design, refactoring, python]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/"]
confidence: high
---

## Definition

Decomposition is the process of breaking a problem or system into small, manageable pieces. In software, it means separating sections of code that do a single thing into functions, classes, or modules. Like a mushroom breaking down a fallen tree into nitrogen and carbon dioxide that get recycled back into the ecosystem, decomposed code becomes reusable components within the software's ecosystem.

## How It Works

The decomposition process follows three steps:

1. **Identify unique tasks** in a long stretch of code. Group together lines that calculate intermediate values with the lines that calculate the final result.
2. **Wrap each task in a function** with a name that clearly indicates what it does. Give each input argument a name that conveys its intent.
3. **Reuse or recompose** the extracted functions as needed.

Decomposition is not just for code structure—it also applies to goals. Breaking "make a physics engine" into "calculate the velocity of a falling object" makes each sub-goal achievable and examinable incrementally.

## Key Parameters

- **Surgical changes**: Decomposed code allows for more precise changes with minimal impact on surrounding code. Over the course of a project, this saves significant time.
- **Readability vs. length**: Overall code length isn't so important; it's the length of individual functions and methods that matters. Decomposition often makes code longer overall but much easier to understand.
- **Cohesion**: When decomposition groups closely related behaviors and data, the result is high cohesion.

## When To Use

Use decomposition when:
- A function or script has grown long enough that its intent is no longer obvious at a glance.
- The same logic appears in multiple places (duplication).
- A function is doing more than one thing, making it hard to name or test.
- You want to enable abstraction by hiding lower-level steps behind well-named wrappers.

## Risks & Pitfalls

- **Over-decomposition**: Extracting too aggressively can create a proliferation of tiny functions that jump around and are hard to follow. Each extraction should clarify intent.
- **Wrong boundaries**: Decomposing along arbitrary boundaries (e.g., every 10 lines) is less effective than decomposing by concern.

## Related Concepts

- [[concepts/abstraction]] — builds on decomposition to hide details
- [[concepts/separation-of-concerns]] — the guiding principle for what to decompose
- [[concepts/encapsulation]] — groups decomposed pieces into larger constructs

## Sources

- *Practices of the Python Pro*, Chapter 2 — Separation of concerns
- *Practices of the Python Pro*, Chapter 3 — Abstraction and encapsulation
