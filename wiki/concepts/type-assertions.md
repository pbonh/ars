---
title: "Type Assertions"
type: concept
tags: [concept, typescript, type-system, casting]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Definition

A type assertion in TypeScript is a compile-time instruction that tells the compiler to treat a value as a specific type, overriding the type the compiler has inferred or assigned. It does not perform any runtime conversion or validation.

## How It Works

Type assertions use either the `as` keyword or angle-bracket syntax (the latter is disallowed in JSX/TSX files):

```typescript
let someValue: unknown = "this is a string";
let strLength = (someValue as string).length;
```

The compiler trusts the assertion and allows operations valid for the asserted type. If the assertion is wrong, the error surfaces at runtime, not compile time.

## Key Parameters

- Assertions can only narrow or re-label types within a reasonable structural overlap; an assertion to a completely unrelated type requires the `unknown` or `any` intermediate.
- The non-null assertion (`!`) is a special case that removes `null` and `undefined` from a union type.
- The definite assignment assertion (`!` after a variable declaration) tells the compiler a variable will be assigned before use even when the compiler cannot verify it.

## When To Use

- Use assertions when you know more about a value's type than the compiler does (e.g., after a DOM query or a third-party library call).
- Use non-null assertions sparingly, only when you are certain a value cannot be null at that point.

## Risks & Pitfalls

- **No runtime safety**: A mistaken assertion produces a compile-time lie; the emitted JavaScript will execute with the wrong assumption and may crash.
- **Overuse**: Frequent assertions suggest the underlying types or data sources are not modeled accurately.

## Related Concepts

- [[concepts/type-guards]]
- [[concepts/unknown-type]]
- [[concepts/nullable-types]]

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapter 7
