---
title: "Structural Typing"
type: concept
tags: [concept, typescript, type-system, compatibility]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/", "raw/programming-with-types-book/"]
confidence: high
---

## Definition

Structural typing is a type system rule where type compatibility and equivalence are determined by the actual structure (members and their types) of a type, rather than by explicit inheritance relationships or nominal declarations. TypeScript uses structural typing as its core compatibility model.

## How It Works

In a structurally typed system, a value is assignable to a target type if the value contains at least all the required members with compatible types, regardless of the value's declared type or class hierarchy. This is often summarized as "duck typing": if it walks like a duck and quacks like a duck, it is a duck.

Example:
```typescript
interface Named { name: string; }
class Person { constructor(public name: string) {} }
let n: Named = new Person("Ada"); // OK, because Person has a `name` string
```

This contrasts with [[concepts/nominal-subtyping|nominal typing]] (used in Java, C#, and Swift), where compatibility is based on explicit class/interface declarations and inheritance. In nominal systems, two classes with identical shapes but no declared relationship are not interchangeable. In structural systems, they are.

## Key Parameters

- Excess property checks: Object literals undergo an additional check where undeclared properties trigger an error, even though the same object assigned via a variable would not.
- `private` and `protected` members introduce nominal-like constraints: two classes with identically shaped private members are not mutually assignable unless one inherits from the other.

## When To Use

- Structural typing is the default in TypeScript; no action is required to use it.
- Rely on structural compatibility when building flexible APIs that accept any object with the right shape.
- Use branding (intersecting with a unique literal or symbol) when nominal-like distinctness is needed.

## Risks & Pitfalls

- **Accidental compatibility**: Two unrelated types with the same shape are silently interchangeable, which can allow logically wrong assignments. This is the primary risk when representing domain concepts (e.g., units of measure) as plain shapes rather than branded types.
- **Nominal simulation cost**: Developers who need nominal safety in a structural language must apply branding techniques (unique symbols, phantom types) manually.
- **Excess property confusion**: The difference between object-literal and variable assignment rules is a frequent source of confusion for new TypeScript developers.

## Related Concepts

- [[concepts/nominal-subtyping]] — the alternative approach that prevents accidental shape-based substitution
- [[concepts/interfaces-in-typescript]]
- [[concepts/shape-types]]
- [[concepts/type-aliases]]

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapters 7, 11
