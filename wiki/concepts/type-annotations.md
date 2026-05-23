---
title: "Type Annotations"
type: concept
tags: [concept, typescript, type-system, syntax]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Definition

A type annotation in TypeScript is an explicit declaration of the data type for a variable, function parameter, or return value. It is written after a colon (`:`) following the identifier, telling the compiler exactly which types are permitted.

## How It Works

When an annotation is present, the compiler uses it as the source of truth instead of inferring a type from the assigned value. If code later attempts to assign an incompatible value, the compiler reports an error at build time.

Example:
```typescript
let count: number = 0;
function greet(name: string): string {
    return `Hello, ${name}`;
}
```

Annotations can describe primitive types (`number`, `string`, `boolean`), object shapes, arrays, tuples, unions, and user-defined types.

## Key Parameters

- Annotations are optional. TypeScript infers types when they are omitted and an initial value is provided.
- The `any` annotation effectively removes type checking for that identifier.
- Function signatures can annotate both parameters and the return type.

## When To Use

- Annotate function parameters and return types in public APIs to create a self-documenting contract.
- Annotate variables when they are declared without an initial value.
- Annotate when inference would produce a wider type than intended (e.g., inferring `string[]` when you actually want a tuple).

## Risks & Pitfalls

- **Over-annotating**: Adding annotations to every local variable creates noise without benefit when inference already captures the correct type.
- **Incorrect annotations**: An annotation that is too narrow can cause unnecessary compile errors; one that is too broad (e.g., `any`) hides bugs.

## Related Concepts

- [[concepts/type-inference]]
- [[concepts/static-typing-in-typescript]]
- [[concepts/type-aliases]]

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapter 7
