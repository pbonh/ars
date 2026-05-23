---
title: "Command Pattern"
type: concept
tags: [concept, design-pattern, software-design, python]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/"]
confidence: high
---

## Definition

The command pattern is a behavioral design pattern in which an action or request is encapsulated as an object. The object contains all the information needed to perform the action, and it exposes a uniform interface (typically an `execute` method) so that invokers do not need to know the concrete details of the action.

## How It Works

In the command pattern:

- **Command** — An object that knows how to perform a specific action. It exposes a uniform method (e.g., `execute()`).
- **Invoker** — The entity that decides when to run a command. It calls `execute()` without knowing what happens inside.
- **Receiver** — The underlying system or object that the command acts upon (e.g., a database).

In the book's Bark application, each menu option maps to a command class (`AddBookmarkCommand`, `ListBookmarksCommand`, etc.). The presentation layer creates an `Option` object that pairs display text with a command instance. When the user selects an option, `Option.choose()` calls `command.execute()`. This decouples the text presented to the user from the business logic triggered by that choice.

## Key Parameters

- **Uniform interface**: All commands must implement the same interface so the invoker can treat them polymorphically.
- **Decoupling**: The presentation layer knows only that it has an object with an `execute` method; it does not know about SQL, HTTP, or file operations.
- **Extensibility**: Adding a new feature means adding a new command class and wiring it into the menu, without modifying existing commands.

## When To Use

Use the command pattern when:
- You need to decouple the object that invokes an operation from the object that performs it.
- You want to queue, log, or undo operations.
- You are building a menu system, toolbar, or macro recorder where multiple triggers map to the same action.
- You want to parameterize objects with operations (passing commands as arguments).

## Risks & Pitfalls

- **Overkill for simple cases**: If there is only one action, the pattern may add unnecessary indirection.
- **Proliferation of classes**: Each command becomes a class, which can feel verbose in small projects.

## Related Concepts

- [[concepts/extensibility]] — command pattern enables adding features without editing existing code
- [[concepts/loose-coupling]] — the pattern's primary benefit

## Sources

- *Practices of the Python Pro*, Chapter 6 — Separation of concerns in practice
