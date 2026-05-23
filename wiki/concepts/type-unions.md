---
title: "Type Unions"
type: concept
tags: [concept, typescript, type-system, composite-types]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Definition

A type union in TypeScript describes a value that may be one of several types. It is written with the pipe (`|`) operator between type names, creating a new type whose permissible values are the union of the individual types' values.

## How It Works

The union type restricts a variable to a fixed set of types. When a value has a union type, TypeScript only permits operations that are valid on **all** members of the union (the intersection of their APIs). To use type-specific features, the value must first be narrowed with a type guard.

Example:
```typescript
function calculateTax(amount: number, format: boolean): string | number {
    const calcAmount = amount * 1.2;
    return format ? `$${calcAmount.toFixed(2)}` : calcAmount;
}
```

Accessing `.toFixed` on the result requires narrowing first, because `toFixed` does not exist on `string`.

## Key Parameters

- Unions can combine any number of types, including primitives, object shapes, and other unions.
- `null` and `undefined` are commonly unioned with other types when `strictNullChecks` is enabled.
- Discriminated unions (objects with a shared literal property, e.g., `kind`) enable safe narrowing via switch statements.

## When To Use

- Use unions when a function may return different types depending on its arguments or internal logic.
- Use unions to model optional/nullable values (`string | null | undefined`).
- Use discriminated unions to represent a fixed set of related object shapes in a type-safe way.

## Risks & Pitfalls

- **Common-API limitation**: Only members shared by all union constituents are accessible without narrowing.
- **Exhaustiveness**: When narrowing with `switch`, forgetting a case for a union member can leave a variable in an unexpectedly wide type.

## Related Concepts

- [[concepts/type-guards]]
- [[concepts/type-intersections]]
- [[concepts/nullable-types]]
- [[concepts/literal-value-types]]

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapter 7
