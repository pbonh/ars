---
title: "Interfaces in TypeScript"
type: concept
tags: [concept, typescript, type-system, object-oriented-programming]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Definition

An interface in TypeScript is a named contract that describes the shape an object or class must satisfy. Unlike classes, interfaces have no runtime representation; they are purely a compile-time construct used for type checking.

## How It Works

Interfaces declare properties, methods, and index signatures that implementing values must provide. Classes implement interfaces with the `implements` keyword, and objects are checked structurally against interfaces without explicit declaration.

Example:
```typescript
interface Shape {
    readonly name: string;
    getArea(): number;
}

class Circle implements Shape {
    constructor(public readonly name: string, public radius: number) {}
    getArea() { return Math.PI * this.radius ** 2; }
}
```

TypeScript supports declaration merging: multiple declarations of the same interface in the same scope are merged into a single interface. This is useful for augmenting external types.

## Key Parameters

- `extends`: Interfaces can inherit from other interfaces, accumulating members.
- `readonly`: Prevents mutation of the property after initialization.
- Optional members: Declared with `?`.
- Index signatures: Allow dynamic property names with a specified value type.

## When To Use

- Use interfaces to define public contracts for classes and APIs.
- Use interfaces when you expect declaration merging or augmentation (e.g., extending third-party types).
- Prefer interfaces over type aliases for object shapes that may need extension.

## Risks & Pitfalls

- **Declaration merging surprises**: Re-declaring an interface in a different file unexpectedly merges it, which can introduce hidden dependencies.
- **No runtime enforcement**: A class `implements` an interface is only checked by the compiler; the emitted JavaScript contains no interface metadata.

## Related Concepts

- [[concepts/shape-types]]
- [[concepts/type-aliases]]
- [[concepts/structural-typing]]
- [[concepts/abstract-base-class]]

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapter 11
