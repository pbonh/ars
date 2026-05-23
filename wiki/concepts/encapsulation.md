---
title: "Encapsulation"
type: concept
tags: [concept, software-design, object-oriented-programming, python]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/", "raw/programming-with-types-book/"]
confidence: high
---

## Definition

Encapsulation is the grouping of related functions and data into a larger construct that acts as a barrier (or capsule) to the outside world. It is the basis for object-oriented programming: decomposition groups code into functions, while encapsulation groups related functions and data into classes, modules, or packages.

## How It Works

Encapsulation applies across languages and paradigms:

**Python constructs** (from smallest to largest):

1. **Class** — The most common encapsulation unit. Functions become methods; data becomes attributes. Methods receive the instance as `self`, allowing them to access or mutate state.
2. **Module** — A `.py` file that groups multiple related classes and functions. For example, an HTTP module might contain request/response classes and URL-parsing utilities.
3. **Package** — A directory with `__init__.py` that encapsulates related modules. Packages can be nested to create navigable hierarchies.

**Type-system perspective** (from *Programming with Types*):
- The type checker enforces encapsulation by rejecting references to private or read-only variables outside their scope.
- Immutability is a form of encapsulation: declaring data as read-only prevents external mutation, so internal state cannot be corrupted by callers.
- Even when data in memory is physically accessible, the type system can make certain operations illegal at compile time, providing a stronger guarantee than runtime access control.

Encapsulation creates a "castle wall" around code. The functions and methods are the drawbridge for getting information in or out. Cooperation between encapsulated activities is coordinated at a higher level.

## Key Parameters

- **Privacy convention**: Python has no true private methods or data. The underscore prefix (`_method`) signals that a member is not part of the public interface and may change.
- **Interface vs. implementation**: The public methods and data form the interface; everything else is implementation detail. Loose coupling is achieved when consumers depend only on the interface.
- **Information hiding**: Encapsulation and abstraction work together to hide internals, allowing rapid internal change without forcing other code to change at the same rate.

## When To Use

Use encapsulation when:
- Several functions share the same input data and work in tandem.
- You need to protect internal state from being manipulated directly by external code.
- A set of behaviors and data clearly belongs to a single concept (e.g., a shopping cart, a database connection).
- You want to distribute code as a reusable package via PyPI.
- You are leveraging a type system to enforce visibility or immutability at compile time, preventing an entire class of state-corruption bugs.

## Risks & Pitfalls

- **Leaky encapsulation**: Exposing too many internals (or requiring consumers to know them) defeats the purpose. Keep the interface minimal and stable.
- **Tight coupling**: If a class depends on the internals of another class, encapsulation has failed. Consumers should depend on interfaces, not implementation details.

## Related Concepts

- [[concepts/type-safety]] — type checkers enforce encapsulation by restricting access to private and read-only members
- [[concepts/immutability]] — a strong form of encapsulation that prevents mutation
- [[concepts/abstraction]] — hides details behind simplified interfaces
- [[concepts/separation-of-concerns]] — divides distinct behaviors into separate pieces
- [[concepts/loose-coupling]] — the desired outcome of strong encapsulation

## Sources

- *Practices of the Python Pro*, Chapter 3 — Abstraction and encapsulation
- *Programming with Types*, Chapter 1 — Benefits of type systems (encapsulation and immutability)
