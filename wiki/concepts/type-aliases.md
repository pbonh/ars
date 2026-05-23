---
title: "Type Aliases"
type: concept
tags: [concept, typescript, type-system, abstraction]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Definition

A type alias in TypeScript is a named identifier that refers to an existing type, created with the `type` keyword. Aliases do not create new types; they provide a shorthand name for complex or repeatedly used type expressions.

## How It Works

Type aliases can name primitives, unions, tuples, object shapes, or any other valid type. They support generic parameters, making them a lightweight alternative to interfaces for describing reusable shapes.

Example:
```typescript
type Point = { x: number; y: number };
type ID = string | number;
type Result<T> = { data: T; error?: string };
```

Aliases are fully substitutable: wherever the aliased type is expected, a value of the alias type is accepted, and vice versa.

## Key Parameters

- Aliases cannot be reopened or merged; interfaces can be merged via declaration merging.
- Aliases can describe union types, which interfaces cannot.
- Aliases can be recursive if the recursion passes through a mapped type, conditional type, or object property.

## When To Use

- Use aliases to give a readable name to a complex union or tuple.
- Use aliases when you need a union type (interfaces cannot express unions).
- Use aliases for one-off shape descriptions; prefer interfaces for public object contracts that may need extension.

## Risks & Pitfalls

- **Aliasing vs. new type**: Because aliases are structural, two different alias names for the same shape are interchangeable, which can be surprising if you intended nominal branding.
- **Over-abstraction**: Creating aliases for every primitive (e.g., `type Email = string`) adds indirection without compile-time value unless paired with a branded-type pattern.

## Related Concepts

- [[concepts/interfaces-in-typescript]]
- [[concepts/type-unions]]
- [[concepts/literal-value-types]]

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapter 9
