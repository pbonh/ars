---
title: "Conditional Types"
type: concept
tags: [concept, typescript, type-system, metaprogramming]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Definition

A conditional type in TypeScript is a type-level `if` expression that selects one of two types based on a type relationship check. It is written `T extends U ? X : Y`, evaluating to `X` if `T` is assignable to `U`, otherwise `Y`.

## How It Works

Conditional types operate entirely at compile time and are a form of type-level metaprogramming. They are commonly combined with mapped types and template literal types to build sophisticated type transformations.

Example:
```typescript
type NonNullable<T> = T extends null | undefined ? never : T;
type A = NonNullable<string | null>; // string
```

Distributive behavior: When `T` is a union, the conditional type distributes over each member individually. This can be disabled by wrapping `T` in a tuple (`[T]`).

## Key Parameters

- `infer` keyword: Extracts a type variable from a matching type within the `extends` clause, enabling pattern matching on types.
- Distributivity: `T extends U ? X : Y` distributes over unions in `T` when `T` is a naked type parameter.
- Built-in helpers: `Exclude`, `Extract`, `NonNullable`, `ReturnType`, `Parameters`, `InstanceType`, and others are implemented as conditional types.

## When To Use

- Use conditional types for utility types that transform or filter other types (e.g., removing `null` from a union).
- Use `infer` to extract the element type of an array or the return type of a function.
- Use built-in conditional helpers before writing custom ones; they are well-tested and produce familiar error messages.

## Risks & Pitfalls

- **Complexity ceiling**: Deeply nested conditional types are hard to read and debug.
- **Distributivity surprises**: The automatic distribution over unions can produce unexpected results when you intended a single check on the whole union.
- **Performance**: Extremely complex conditional type chains can slow the compiler and produce unwieldy tooltips.

## Related Concepts

- [[concepts/typescript-generics]]
- [[concepts/generic-constraints]]

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapter 13
