---
title: "Literal Value Types"
type: concept
tags: [concept, typescript, type-system, narrowing]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Definition

A literal value type in TypeScript restricts a variable to a single specific value rather than a general primitive type. String literals, number literals, and boolean literals can all serve as types, enabling precise modeling of fixed sets of acceptable values.

## How It Works

When a variable is declared with `const`, TypeScript automatically infers a literal type (`const x = "ready"` infers `"ready"`, not `string`). You can also declare literal types explicitly:

```typescript
type Status = "pending" | "active" | "complete";
let current: Status = "active";
```

Literal types are the building blocks of discriminated unions and are commonly combined with type aliases or interfaces to model state machines, action types, and configuration flags.

## Key Parameters

- `as const` assertion: Narrows an entire object or array to its literal types, making all properties readonly and preserving specific values.
- Template literal types: Combine string literals into patterns (e.g., `type EventName = `on${string}``).

## When To Use

- Use literal types when a variable or parameter accepts only a fixed set of string or number values.
- Use discriminated unions with a shared literal property (e.g., `kind: "A" | "B"`) for type-safe branching.
- Use `as const` on exported configuration objects to prevent accidental widening.

## Risks & Pitfalls

- **Widening**: `let` declarations and array literals widen to the base primitive unless constrained by an annotation or `as const`.
- **Exhaustiveness maintenance**: Adding a new literal to a union requires updating all switch/case blocks that narrow over it.

## Related Concepts

- [[concepts/type-unions]]
- [[concepts/type-aliases]]
- [[concepts/type-guards]]

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapter 9
