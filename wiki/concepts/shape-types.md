---
title: "Shape Types"
type: concept
tags: [concept, typescript, type-system, objects]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Definition

A shape type (or object type literal) in TypeScript describes the expected structure of an object by listing the names and types of its properties. Shape types are the basis of TypeScript's structural typing system: a value is compatible with a shape type if it contains at least the required properties with compatible types.

## How It Works

Shape types are declared inline or via aliases/interfaces:

```typescript
let point: { x: number; y: number } = { x: 10, y: 20 };
```

Properties can be marked optional with `?`, readonly with `readonly`, or indexed with an index signature (`[key: string]: number`). TypeScript's structural rules mean extra properties on a value are generally allowed during assignment (with some restrictions around excess property checks on object literals).

## Key Parameters

- Optional properties: `{ name?: string }`
- Readonly properties: `{ readonly id: number }`
- Index signatures: `{ [key: string]: number }` for objects with dynamic keys
- Excess property checking: Object literals assigned to a shape type cannot contain properties not declared in the type unless the type has an index signature.

## When To Use

- Use shape types to describe the expected form of function arguments, API responses, and configuration objects.
- Use index signatures when an object acts as a dictionary or map with homogenous values.
- Prefer interfaces over inline shape types for shapes reused across a codebase.

## Risks & Pitfalls

- **Excess property errors**: Passing an object literal with extra properties directly to a function expecting a narrower shape triggers a compile error, even though a pre-declared variable with extra properties would not.
- **Optional vs. undefined**: `{ name?: string }` allows omission, but `{ name: string | undefined }` requires the key to be present even if the value is undefined.

## Related Concepts

- [[concepts/interfaces-in-typescript]]
- [[concepts/type-aliases]]
- [[concepts/structural-typing]]
- [[concepts/type-guards]]

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapter 10
