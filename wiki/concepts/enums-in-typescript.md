---
title: "Enums in TypeScript"
type: concept
tags: [concept, typescript, type-system, constants]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Definition

An enum in TypeScript is a named grouping of related constant values. Enums can be numeric (auto-incrementing or explicitly assigned), string-based, or heterogeneous. At compile time, enums become a type; at runtime, they emit an object mapping names to values and (for numeric enums) values back to names.

## How It Works

Numeric enums assign incremental integers starting from 0 unless overridden:

```typescript
enum Status {
    Pending,    // 0
    Active,     // 1
    Complete    // 2
}
```

String enums require every member to have an explicit string value and do not generate a reverse mapping:

```typescript
enum Direction {
    Up = "UP",
    Down = "DOWN"
}
```

`const enum`s are inlined at compile time and do not emit a runtime object, which reduces bundle size but prevents reverse mapping.

## Key Parameters

- Numeric enums generate a bidirectional mapping object at runtime.
- String enums are unidirectional and tree-shake better.
- `const enum`: Inlines values, emits no object, but cannot be used with `isolatedModules` in some configurations.
- `declare enum`: Describes an enum defined externally (e.g., in a `.d.ts` file).

## When To Use

- Use enums when you need a closed set of named constants that are used in multiple places.
- Prefer string enums over numeric enums when the values are serialized (APIs, configs, databases) because numeric enum values are fragile across refactors.
- Consider literal unions (`"active" | "inactive"`) as a lightweight alternative when you don't need the runtime object or reverse mapping.

## Risks & Pitfalls

- **Numeric enum fragility**: Adding a member in the middle of a numeric enum shifts subsequent values, breaking any persisted data or external contracts.
- **Const enum limitations**: `const enum` values disappear at runtime, so dynamic access (`Status[someVar]`) fails.
- **Type safety gap**: Numeric enums accept any number assignable to them, not just the declared members, which can allow invalid values to pass type checking.

## Related Concepts

- [[concepts/literal-value-types]]
- [[concepts/type-unions]]
- [[concepts/type-aliases]]

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapter 9
