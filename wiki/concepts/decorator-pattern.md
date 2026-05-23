---
title: "Decorator Pattern"
type: concept
tags: [concept, design-pattern, functional-programming, extensibility]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

The decorator pattern is a structural design pattern that allows behavior to be added to an individual object, either statically or dynamically, without affecting the behavior of other objects from the same class. It provides a flexible alternative to subclassing for extending functionality.

## How It Works

- **Object-oriented form**: A decorator implements the same interface as the component it wraps. It delegates calls to the wrapped component and adds its own behavior before or after the delegation.
- **Functional form**: A decorator is a higher-order function that takes a function (the component) and returns a new function with additional behavior. This is often more concise than the class-based approach and naturally supports composition.
- Multiple decorators can be stacked, each adding a layer of behavior around the core component.

## Key Parameters

- **Interface stability**: Both the component and all decorators must honor the same contract so that clients cannot distinguish between decorated and undecorated objects.
- **Order of decoration**: The order in which decorators are applied matters if they have side effects or modify the result.
- **State sharing**: Functional decorators can capture state via closures, while OO decorators store state as object fields.

## When To Use

Use the decorator pattern when:
- You want to add responsibilities to objects dynamically and transparently.
- Extending functionality via subclassing would produce an explosion of subclasses for every combination of features.
- You need to layer cross-cutting concerns (logging, caching, authentication) around core business logic.

## Risks & Pitfalls

- **Debugging complexity**: A deeply decorated object hides its true composition behind a uniform interface, making stack traces harder to read.
- **Identity confusion**: A decorated object is not the same instance as the wrapped object, which can break identity-based equality checks.
- **Type erasure**: In some languages, the runtime type of a decorated object may not reflect the decorator chain.

## Related Concepts

- [[concepts/first-class-functions]] — functional decorators are higher-order functions
- [[concepts/closure]] — decorators often use closures to capture configuration or state
- [[concepts/composition-over-inheritance]] — decorators favor composition over subclassing

## Sources

- *Programming with Types*, Chapter 6 — Advanced applications of function types (section 6.1)
