---
title: "Loose Coupling"
type: concept
tags: [concept, software-design, maintainability, python]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/"]
confidence: high
---

## Definition

Loose coupling is the ability of two pieces of code to interact to accomplish a task without either relying heavily on the details of the other. It is achieved through shared abstractions, well-defined interfaces, and encapsulation. Tight coupling, the opposite, occurs when classes, modules, or functions are highly interdependent, such that changing one frequently requires changing the other.

## How It Works

Coupling can be thought of as a mesh running through a codebase. Where interdependency is high, the mesh is taut; where it is low, the mesh is flexible.

Common forms of coupling and how to address them:

- **Feature envy**: Code that performs several tasks using mainly features from another area should be rolled up into a single entry point back at the source.
- **Shotgun surgery**: One change requires peppering edits far and wide. Address by separating concerns, encapsulating logic, and introducing shared abstractions.
- **Leaky abstraction**: An abstraction that doesn't sufficiently hide its details, forcing consumers to know about low-level behavior. Fix by strengthening the interface and moving error handling or configuration inside the abstraction.

Strategies for achieving loose coupling:
1. **Encapsulate** related logic behind a stable interface (e.g., `clean_query(query)` instead of exposing every transform function).
2. **Use shared abstractions** (e.g., a `PersistenceLayer` interface so commands don't depend on SQLite specifics).
3. **Think in messages**: Frame interconnections as the questions you ask of an object or the commands you give it, rather than focusing on the objects themselves.
4. **Return statuses and results**: Decouple business logic from presentation by having commands return `(success, result)` tuples, letting the presentation layer decide how to display outcomes.

## Key Parameters

- **Continuum**: Coupling is measured along a continuum, not as a binary. Some tight coupling is acceptable when it reflects high cohesion within a single concern.
- **Message-oriented programming**: Thinking about interactions as messages (queries and commands) helps identify whether the right objects are talking to each other.

## When To Use

Strive for loose coupling when:
- You want to work on one feature while a teammate works on another without constant merge conflicts.
- You need to swap out a persistence layer, UI framework, or external service with minimal disruption.
- You are building a library or package consumed by multiple clients.
- You find yourself jumping across many files to make a single logical change.

## Risks & Pitfalls

- **Over-abstraction**: Introducing interfaces between every pair of classes can make the code harder to follow. Abstraction should earn its keep.
- **Indirection fatigue**: Too many layers can obscure the actual flow of execution. Balance loose coupling with readability.

## Related Concepts

- [[concepts/separation-of-concerns]] — divides code into pieces that are easier to keep loosely coupled
- [[concepts/encapsulation]] — hides internals so consumers depend only on interfaces
- [[concepts/inversion-of-control]] — enables swapping implementations without editing consumers

## Sources

- *Practices of the Python Pro*, Chapter 10 — Achieving loose coupling
