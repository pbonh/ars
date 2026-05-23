---
title: "TypeScript"
type: entity
tags: [entity, programming-language, microsoft, compiler]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Overview

TypeScript is a strongly typed programming language developed and maintained by Microsoft. It is a structural superset of JavaScript that adds optional static typing, interfaces, generics, enums, and advanced type system features. TypeScript code compiles to plain JavaScript, allowing it to run in any browser or JavaScript runtime (including Node.js and Deno).

## Characteristics

- **Static typing**: Compile-time type checking with type erasure at runtime.
- **Structural typing**: Type compatibility is determined by shape, not by inheritance or declaration name.
- **Compiler-driven**: The `tsc` compiler transforms `.ts` and `.tsx` files to `.js`, performing type checking as a separate phase.
- **JavaScript superset**: All valid JavaScript is valid TypeScript, enabling gradual adoption.
- **Active evolution**: Major releases align with ECMAScript proposals (e.g., standard decorators in TypeScript 5, mapped types, conditional types).

## Common Strategies

- Gradual migration of JavaScript codebases by renaming files to `.ts` and adding types incrementally.
- Publishing libraries with generated `.d.ts` declaration files for typed consumption.
- Using `strict` compiler mode for maximum type safety on greenfield projects.
- Combining TypeScript with frameworks like React, Angular, Vue, and Svelte via TSX and framework-specific type definitions.

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapters 1–21
- [typescriptlang.org](https://www.typescriptlang.org)
