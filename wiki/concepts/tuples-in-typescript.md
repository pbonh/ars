---
title: "Tuples in TypeScript"
type: concept
tags: [concept, typescript, type-system, arrays]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Definition

A tuple in TypeScript is a typed array with a fixed length and a specific type for each element position. Tuples extend JavaScript arrays with compile-time enforcement of length and element-type order.

## How It Works

Tuple types are declared with square brackets listing the element types:

```typescript
let point: [number, number] = [10, 20];
let nameAge: [string, number] = ["Ada", 36];
```

TypeScript checks that assignments match both the length and the per-position types. Tuples can include optional elements (`[string, number?]`) and rest elements (`[string, ...number[]]`) for variable-length tails.

## Key Parameters

- Optional elements: `[string, number?]` requires at least one element, up to two.
- Rest elements: `[string, ...number[]]` requires a first string followed by any number of numbers.
- Readonly tuples: `readonly [string, number]` prevent mutation after creation.
- Labeled tuples: `[x: number, y: number]` improve readability and tooltips without changing semantics.

## When To Use

- Use tuples to represent fixed-shape data (coordinates, RGB values, key-value pairs) where position carries semantic meaning.
- Use tuples for function return values that need to return multiple distinct values.
- Prefer regular arrays (`Type[]`) when the length is not fixed or when all elements share the same type.

## Risks & Pitfalls

- **Out-of-bounds access**: Accessing an index beyond the declared tuple length produces a compile error only with `noUncheckedIndexedAccess`; otherwise it returns the element's union type.
- **Array method confusion**: Tuple methods like `push` and `pop` are technically available at runtime but can break the tuple's length guarantee, and the compiler may not flag all violations.

## Related Concepts

- [[concepts/type-aliases]]
- [[concepts/type-inference]]
- [[concepts/literal-value-types]]

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapter 9
