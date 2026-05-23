---
title: "Declaration Files"
type: concept
tags: [concept, typescript, interoperability, types]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Definition

A declaration file (`.d.ts`) in TypeScript contains type declarations without implementation code. It describes the shape of JavaScript libraries or modules so that TypeScript can provide type checking and IntelliSense when consuming code written in plain JavaScript.

## How It Works

Declaration files declare variables, functions, classes, and modules with their types but no bodies. The compiler uses these files during type checking only; they emit no JavaScript. Third-party packages often ship `.d.ts` files in a `types` field or in the DefinitelyTyped repository (`@types/*` packages on npm).

Example:
```typescript
// myLib.d.ts
export function parse(input: string): unknown;
export const VERSION: string;
```

TypeScript's `declaration` compiler option generates `.d.ts` files automatically from TypeScript source, making it easy to publish typed libraries.

## Key Parameters

- `allowJs` / `checkJs`: Include JavaScript files in the compilation and optionally type-check them.
- `declaration`: Emit `.d.ts` files from `.ts` source.
- `types` / `typeRoots`: Configure which declaration packages the compiler includes.
- `paths`: Map module names to local declaration files for untyped third-party packages.

## When To Use

- Write `.d.ts` files when consuming a JavaScript library that lacks built-in types.
- Generate declaration files when publishing a TypeScript library so consumers get types without accessing your source.
- Use JSDoc comments in `.js` files as a lightweight alternative when full `.d.ts` files are not worth the overhead.

## Risks & Pitfalls

- **Drift**: Hand-written declaration files can become out of sync with the underlying JavaScript implementation, producing compile-time safety that does not match runtime behavior.
- `@ts-ignore` / `@ts-expect-error`: Suppressing errors instead of fixing declarations undermines the value of type checking.

## Related Concepts

- [[concepts/tsconfig-configuration]]
- [[concepts/static-typing-in-typescript]]
- [[concepts/shape-types]]

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapter 15
