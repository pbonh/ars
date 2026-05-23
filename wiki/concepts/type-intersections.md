---
title: "Type Intersections"
type: concept
tags: [concept, typescript, type-system, composite-types]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Definition

A type intersection in TypeScript combines two or more types into a single type that has all the members of each constituent type. It is written with the ampersand (`&`) operator.

## How It Works

Intersections are the logical opposite of unions. Where a union says "this value is either A or B," an intersection says "this value is both A and B." The resulting type contains every property and method from all intersected types.

Example:
```typescript
type Named = { name: string };
type Aged = { age: number };
type Person = Named & Aged; // { name: string; age: number }
```

When intersecting object types with conflicting property types, the property becomes a type error unless the conflict is itself a valid intersection (e.g., `string & number` becomes `never`).

## Key Parameters

- Intersections are most useful for composing object shapes from smaller, reusable pieces.
- Intersecting with `unknown` produces the other type; intersecting with `any` produces `any`.
- Intersections can combine interfaces, type aliases, and anonymous object shapes.

## When To Use

- Use intersections to mix in capabilities or traits (similar to mixins) in a type-safe way.
- Use intersections to extend an existing type with additional properties for a specific use case.
- Prefer interfaces with `extends` for classical inheritance; use intersections for ad-hoc composition.

## Risks & Pitfalls

- **Conflicting properties**: Intersecting types that define the same property with incompatible types produces `never` for that property, which can be hard to diagnose.
- **Excessive composition**: Deeply nested intersections create verbose types and error messages.

## Related Concepts

- [[concepts/type-unions]]
- [[concepts/shape-types]]
- [[concepts/interfaces-in-typescript]]

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapter 10
