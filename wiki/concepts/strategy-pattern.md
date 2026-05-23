---
title: "Strategy Pattern"
type: concept
tags: [concept, design-pattern, functional-programming, first-class-functions]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

The strategy pattern is a behavioral design pattern that defines a family of interchangeable algorithms, encapsulates each one as a separate component, and makes them interchangeable at run time. The client selects which strategy to use without altering the code that consumes the strategy.

## How It Works

- **Object-oriented form**: A common interface declares the strategy contract. Concrete strategy classes implement the interface. The client holds a reference to the interface and delegates work to the concrete strategy.
- **Functional form**: A function type serves as the strategy contract. Concrete strategies are simply functions matching that type. The client takes a function argument and invokes it directly. This eliminates the need for strategy classes and interfaces.
- Both forms allow adding new strategies without modifying the client, satisfying the open/closed principle.

## Key Parameters

- **Statefulness**: OO strategies can hold mutable state; functional strategies are typically stateless (or rely on closures for state).
- **Type signature**: The strategy contract must be precise enough to cover all required inputs and outputs without leaking implementation details.
- **Selection mechanism**: Strategies can be injected at construction, selected via configuration, or chosen dynamically based on input.

## When To Use

Use the strategy pattern when:
- You have multiple ways to perform the same task (sorting, validation, pricing, routing).
- You want to isolate volatile algorithmic details from stable orchestration code.
- You need to vary behavior at run time based on user input, configuration, or context.

## Risks & Pitfalls

- **Over-abstraction**: A single algorithm with no variants does not need a strategy abstraction.
- **State synchronization**: Stateful strategies may need to share or synchronize state with the context, reintroducing coupling.
- **Type proliferation**: In OO languages, every strategy becomes a class, which can bloat the codebase if there are many simple variants.

## Related Concepts

- [[concepts/first-class-functions]] — functional strategies rely on functions as values
- [[concepts/decorator-pattern]] — decorators wrap strategies to add behavior without changing the strategy itself
- [[concepts/inversion-of-control]] — the strategy pattern inverts control by delegating behavior selection to the caller

## Sources

- *Programming with Types*, Chapter 5 — Function types (section 5.1)
