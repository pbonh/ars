---
title: "Primitive Obsession"
type: concept
tags: [concept, software-design, antipattern, type-safety]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

Primitive obsession is an antipattern in which developers use built-in primitive types—such as `number`, `string`, or `boolean`—to represent domain concepts that deserve their own types. Examples include storing a postal code as a raw number, a phone number as a raw string, or a physical measurement as an unadorned `number`.

## How It Works

When a value is represented as a primitive, its meaning exists only in the developer’s head or in comments. The type checker sees only `number`, so it cannot prevent a pound-force-second value from being passed where a Newton-second is expected. By wrapping the primitive in a dedicated type (e.g., `class Ns { ... }`), the type checker becomes a partner in enforcing correct usage.

## Key Parameters

- **Cost of wrapping**: In many languages, a simple wrapper class or branded type is enough; the overhead is typically compiled away.
- **Nominal vs. structural**: In structurally typed languages (e.g., TypeScript), two wrappers with identical shapes may still be substitutable unless a nominal branding technique (such as a unique symbol) is applied.
- **Scope of replacement**: Not every primitive needs wrapping. Replace primitives when the value carries domain meaning, has units, or is subject to constraints.

## When To Use

Replace primitive types with dedicated types when:
- The value represents a domain concept with units (momentum, currency, distance).
- Different parts of the codebase use incompatible interpretations of the same primitive.
- You want the compiler to reject accidental mixing of semantically different values.

## Risks & Pitfalls

- **Over-engineering**: Wrapping every integer or string creates unnecessary boilerplate. Reserve wrappers for values with clear domain semantics.
- **Serialization friction**: Dedicated types may require extra serialization/deserialization logic. Plan for this at API boundaries.
- **False confidence**: A wrapper type alone does not validate ranges (e.g., a `PositiveInteger` wrapper should still enforce the constraint at construction).

## Related Concepts

- [[concepts/type-safety]] — primitive obsession undermines safety by leaving meaning outside the type system
- [[concepts/nominal-subtyping]] — nominal types prevent accidental substitution of similarly shaped wrappers
- [[concepts/encapsulation]] — wrapping primitives is a form of encapsulating domain meaning

## Sources

- *Programming with Types*, Chapter 4 — Type safety (section 4.1)
