---
title: "Nullable Types"
type: concept
tags: [concept, typescript, type-system, null-safety]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Definition

Nullable types in TypeScript are types that explicitly include `null` or `undefined` as permitted values. Under `strictNullChecks`, `null` and `undefined` are no longer assignable to every other type by default; they must be declared as part of a union (e.g., `string | null`).

## How It Works

With `strictNullChecks` enabled, the compiler treats `null` and `undefined` as distinct types that can only be assigned where explicitly allowed. This prevents the billion-dollar mistake of accidentally dereferencing a null value. Values of a nullable type cannot be used without first narrowing away the null case, typically with a guard or non-null assertion.

Example:
```typescript
function printLength(s: string | null): void {
    if (s !== null) {
        console.log(s.length);
    }
}
```

## Key Parameters

- `strictNullChecks`: The compiler option that enables nullable-type enforcement.
- Non-null assertion (`!`): A postfix operator that tells the compiler to remove `null` and `undefined` from the type for that expression.
- Optional properties and parameters implicitly include `undefined` in their type.

## When To Use

- Enable `strictNullChecks` on all new projects to catch null-dereference errors at compile time.
- Use `| null` or `| undefined` when a value may legitimately be absent.
- Use non-null assertions only when the absence case is provably impossible at that point.

## Risks & Pitfalls

- **Non-null assertion abuse**: Overusing `!` defeats the safety `strictNullChecks` provides.
- **Third-party types**: Libraries without declaration files may not mark nullable return types, requiring defensive wrapping.

## Related Concepts

- [[concepts/type-unions]]
- [[concepts/type-guards]]
- [[concepts/type-assertions]]

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapter 7
