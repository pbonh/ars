---
title: "Extensibility"
type: concept
tags: [concept, software-design, maintainability, python]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/"]
confidence: high
---

## Definition

Extensibility is the property of a software system that allows new behaviors to be added with little or no impact on existing behaviors. In an ideal extensible system, adding a feature means adding new classes, methods, functions, or data without changing existing code. It is a spectrum, and it improves iteratively through practices like separation of concerns and loose coupling.

## How It Works

Extensibility is achieved by designing code so that new functionality can be introduced as additions rather than modifications:

- **Plugin systems** (e.g., browser extensions) are canonical examples of extensibility. The host application doesn't know about specific extensions in advance, but it provides hooks that extensions can use.
- **Configuration over conditionals**: Replacing long `if/elif` chains with data structures (dictionaries mapping inputs to behavior) makes adding new cases a matter of adding entries, not editing control flow.
- **Inversion of control**: Letting callers supply dependencies means new variants can be injected without editing the class that uses them.
- **Shared abstractions / interfaces**: When high-level code relies on agreed-upon interfaces rather than low-level details, new implementations can be swapped in freely.

The opposite of extensibility is rigidity, where adding a feature requires peppering changes throughout the codebase—a phenomenon known as [[concepts/loose-coupling|shotgun surgery]].

## Key Parameters

- **Spectrum**: Extensibility is not binary. Real systems are rarely ideal; the goal is to maximize the proportion of changes that are additive.
- **Duplication as a stepping stone**: Duplicating code and altering the copy to see how the two versions differ is a valid intermediate step toward making the original code more extensible.
- **Kent Beck's rule**: "For each desired change, make the change easy (warning: this may be hard), then make the easy change."

## When To Use

Design for extensibility when:
- You are building a product that will accumulate features over time.
- Multiple teams or developers will work on different areas simultaneously.
- You want to minimize regression risk when adding new capabilities.
- You are creating a framework, library, or plugin system.

## Risks & Pitfalls

- **Premature abstraction**: Don't try to predict every future feature. Build for the known use cases, keep the code clean, and abstract when a real need arises.
- **Wrong abstraction**: An abstraction that doesn't fit new use cases can be worse than none. See the rule: "duplication is better than the wrong abstraction."

## Related Concepts

- [[concepts/inversion-of-control]] — enables swapping implementations without editing internals
- [[concepts/loose-coupling]] — reduces the ripple effects of changes
- [[concepts/separation-of-concerns]] — keeps features isolated

## Sources

- *Practices of the Python Pro*, Chapter 7 — Extensibility and flexibility
