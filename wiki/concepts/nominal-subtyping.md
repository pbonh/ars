---
title: "Nominal Subtyping"
type: concept
tags: [concept, type-system, object-oriented-programming]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

Nominal subtyping establishes a subtype relationship based on an explicit declaration, typically by name or by an `implements`/`extends` clause. Two types with identical structures are not considered subtypes of each other unless the programmer explicitly states the relationship.

## How It Works

- In nominally typed languages (e.g., Java, C#, Swift), a class `B` is a subtype of class `A` only if `B` explicitly extends or implements `A`.
- The type checker looks at the declared hierarchy, not at the fields and methods present in each type.
- This prevents accidental substitution: a `Lbfs` (pound-force-seconds) type and a `Ns` (Newton-seconds) type will never be interchangeable, even if both wrap a single `number` field.
- In languages with structural subtyping (e.g., TypeScript), nominal behavior can be simulated using branding techniques such as unique symbols or private fields.

## Key Parameters

- **Declaration overhead**: Every intended subtype relationship must be explicitly declared, which can be verbose but precise.
- **Cross-library compatibility**: Nominal types from different libraries with the same shape cannot be substituted, which may require adapter code.
- **Refactoring safety**: Renaming a type or breaking an inheritance chain is a visible, compiler-checked change.

## When To Use

Prefer nominal subtyping when:
- Types represent semantically different domain concepts that happen to share structure (units of measure, currency, identifiers).
- You want the compiler to enforce that only explicitly approved types can be substituted.
- You are modeling a true "is-a" hierarchy where inheritance reflects domain taxonomy.

## Risks & Pitfalls

- **Boilerplate**: Declaring wrapper types and explicit inheritance for every domain concept adds code.
- **Library friction**: If an external library defines a type with the same shape as your interface, you cannot use it directly unless the library author declares the relationship.
- **False security**: Nominal typing prevents accidental substitution but does not prevent logical errors within the declared hierarchy.

## Related Concepts

- [[concepts/structural-typing]] — the alternative approach where shape alone determines subtyping
- [[concepts/primitive-obsession]] — nominal wrappers are the cure for primitive obsession
- [[concepts/variance]] — variance rules apply regardless of whether subtyping is nominal or structural

## Sources

- *Programming with Types*, Chapter 7 — Subtyping (section 7.1)
