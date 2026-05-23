---
title: "Generic Constraints"
type: concept
tags: [concept, typescript, type-system, generics]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Definition

A generic constraint in TypeScript limits the set of types that can be used as a type argument for a generic parameter. It is declared with the `extends` keyword inside the generic declaration, requiring the type argument to be assignable to the constraint type.

## How It Works

Constraints allow generic code to safely access properties or methods known to exist on the constrained type. Without a constraint, a generic parameter `T` has no known members other than those shared by all types.

Example:
```typescript
function longest<T extends { length: number }>(a: T, b: T): T {
    return a.length >= b.length ? a : b;
}
```

Here, `T` must have a `length` property, so the function works with arrays, strings, and any other length-bearing type.

## Key Parameters

- Constraints can reference interfaces, type aliases, primitive types, or other generic parameters.
- `keyof` constraints: `T extends keyof SomeType` restricts `T` to valid property names.
- Multiple constraints cannot be expressed directly with intersection syntax, but can be composed via an intermediate interface.

## When To Use

- Use constraints when generic logic requires access to specific properties or methods.
- Use `keyof` constraints when writing utility functions that operate on object keys.
- Avoid constraints that are too broad (equivalent to no constraint) or too narrow (rejecting valid use cases).

## Risks & Pitfalls

- **Constraint over-specification**: Requiring more properties than the generic code actually uses limits reusability.
- **Circular constraints**: Recursive generic constraints can produce complex error messages and occasionally hit compiler limits.

## Related Concepts

- [[concepts/typescript-generics]]

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapter 12
