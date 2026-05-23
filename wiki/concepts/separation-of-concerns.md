---
title: "Separation of Concerns"
type: concept
tags: [concept, software-design, python, modularity]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/"]
confidence: high
---

## Definition

Separation of concerns is the practice of dividing a software system into distinct sections, each addressing a separate concern. A *concern* is a distinct behavior or piece of knowledge the software deals with, ranging from fine-grained operations (calculating a square root) to coarse-grained domains (managing payments in an e-commerce system).

## How It Works

In Python, separation of concerns is achieved through a hierarchy of structural tools:

1. **Functions** — Extract named behaviors from procedural code. Small functions that do one thing reduce the amount of knowledge a reader must hold at once.
2. **Classes** — Group closely related data and behaviors into objects with high cohesion.
3. **Modules** — Group related classes and functions into `.py` files, creating namespaces that prevent collisions and guide code discovery.
4. **Packages** — Group related modules into directories with `__init__.py`, adding a further level of hierarchy to manage naming and navigation.

Each level follows the Unix philosophy: "do one thing and do it well."

## Key Parameters

- **Granularity**: There are no steadfast rules about how deep or shallow to make the hierarchy. The goal is to group like activities together and keep dissimilar activities isolated.
- **Cohesion**: A class or module has high cohesion when its contents make sense together as a whole. High cohesion is a signal that concerns are well separated.
- **Coupling**: When a class depends heavily on another class, they are tightly coupled. Separation of concerns aims for loose coupling so that changes in one area don't ripple unpredictably into others.

## When To Use

Apply separation of concerns continuously, as an iterative seasoning rather than a one-time upfront design. Use it when:
- A function grows too long or mixes multiple concepts.
- Several functions share the same input data and work in tandem.
- A module becomes too large to navigate or remember.
- Name collisions start occurring between unrelated behaviors.
- You need to make a change and find yourself doing [[concepts/loose-coupling|shotgun surgery]].

## Risks & Pitfalls

- **Premature abstraction**: Don't guess categories up front; they change frequently as your mental model evolves. Wait until a sensible organization presents itself.
- **Over-engineering**: Not every one-liner needs to be a function, and not every pair of functions needs a class. Keep the hierarchy proportional to the complexity of the problem.
- **Wrong abstraction**: Once separated, concerns can still be poorly bounded. If adding a feature requires editing many existing files, the current boundaries may be wrong.

## Related Concepts

- [[concepts/abstraction]] — hides details behind interfaces
- [[concepts/encapsulation]] — groups related data and behavior into barriers
- [[concepts/decomposition]] — breaks problems into smaller pieces
- [[concepts/loose-coupling]] — the desired outcome of good separation

## Sources

- *Practices of the Python Pro*, Chapter 2 — Separation of concerns
- *Practices of the Python Pro*, Chapter 6 — Separation of concerns in practice (Bark application)
