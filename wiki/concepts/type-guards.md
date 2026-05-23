---
title: "Type Guards"
type: concept
tags: [concept, typescript, type-system, narrowing]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Definition

A type guard in TypeScript is a runtime check that narrows a union or broad type to a more specific type within a code block, enabling the compiler to permit type-specific operations that would otherwise be disallowed.

## How It Works

Type guards leverage JavaScript runtime checks to refine types at compile time. Common guard patterns include:

- **`typeof` checks** for primitive types:
  ```typescript
  if (typeof value === "string") { /* value is string here */ }
  ```
- **`instanceof` checks** for class instances.
- **`in` operator** for object property presence:
  ```typescript
  if ("name" in obj) { /* obj has a name property */ }
  ```
- **User-defined type predicates** (`is` functions):
  ```typescript
  function isString(val: unknown): val is string {
      return typeof val === "string";
  }
  ```

Once a guard succeeds, TypeScript narrows the variable's type for the remainder of the block.

## Key Parameters

- Guards must be deterministic expressions that the compiler can analyze.
- Custom predicate functions return `boolean` but carry a return-type annotation `arg is Type`.
- Assert functions (using the `asserts` keyword in TypeScript) throw if a condition fails, narrowing types after the call.

## When To Use

- Use `typeof` for primitive unions (`string | number`).
- Use `instanceof` when distinguishing class instances.
- Use custom predicates when a complex runtime check determines membership in a type.
- Use discriminated unions with a shared literal property (e.g., `kind: "circle"`) for elegant narrowing via `switch`.

## Risks & Pitfalls

- **Guard mismatch**: A predicate function with an incorrect implementation (returning `true` for the wrong shape) leads to narrowed types that do not match runtime reality.
- **Exhaustiveness**: Failing to handle all union members in a `switch` or `if-else` chain leaves variables in an un-narrowed state.

## Related Concepts

- [[concepts/type-unions]]
- [[concepts/type-assertions]]
- [[concepts/shape-types]]

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapters 7, 8, 10
