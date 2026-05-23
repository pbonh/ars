---
title: "Decorators in TypeScript"
type: concept
tags: [concept, typescript, metaprogramming, object-oriented-programming]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Definition

A decorator in TypeScript is a special kind of declaration that can be attached to a class, method, accessor, property, or parameter to modify or replace its behavior. TypeScript 5 introduced standard decorators aligned with the forthcoming ECMAScript decorator proposal, replacing the earlier experimental decorator implementation.

## How It Works

A decorator is a function that receives the target feature and a context object describing the kind of feature being decorated (class, method, field, etc.). The decorator can return a replacement value or leave the feature unchanged.

Example:
```typescript
function log(target: any, context: ClassMethodDecoratorContext) {
    return function (...args: any[]) {
        console.log(`Calling ${String(context.name)}`);
        return target.apply(this, args);
    };
}

class Greeter {
    @log
    greet() { return "Hello"; }
}
```

Factory functions (higher-order functions) can accept configuration arguments and return the actual decorator. Initializer functions run during class instantiation to set up decorator state. Decorators can accumulate state by closing over external variables.

## Key Parameters

- Decorator contexts provide metadata: `kind`, `name`, `private`, `static`, and an `addInitializer` hook.
- Standard decorators in TypeScript 5 do not require the `experimentalDecorators` compiler flag.
- Legacy experimental decorators (used heavily in Angular before v14+) are still available behind the `experimentalDecorators` flag but are superseded by the standard form.

## When To Use

- Use decorators for cross-cutting concerns: logging, validation, serialization, dependency injection, and access control.
- Use factory decorators when the same decorator behavior needs to be parameterized.
- Prefer standard decorators for new code; reserve legacy decorators for maintaining existing Angular or old framework code.

## Risks & Pitfalls

- **Stage-3 dependency**: Standard decorators are a TC39 Stage 3 proposal; minor syntax or semantic changes may still occur before full standardization.
- **Debugging complexity**: Decorators add indirection that can make stack traces and step-through debugging harder to follow.
- **Over-decoration**: Excessive use of decorators scatters behavior across files, making it harder to understand the full execution path of a class.

## Related Concepts

- [[concepts/interfaces-in-typescript]]
- [[concepts/abstract-base-class]]
- [[concepts/inversion-of-control]]

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapter 14
