---
title: "tsconfig Configuration"
type: concept
tags: [concept, typescript, compiler, configuration]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Definition

`tsconfig.json` is the configuration file for the TypeScript compiler (`tsc`). It specifies which files to compile, which compiler options to apply, and how the emitted JavaScript should be structured.

## How It Works

The compiler reads `tsconfig.json` from the project root (or the directory passed to `--project`). The file contains a JSON object with `compilerOptions`, `include`, `exclude`, and `files` fields. Options control the target ECMAScript version, module system, output directory, strictness, and interop behavior.

Key compiler options:
- `target`: ECMAScript version for emitted code (`ES2022`, `ESNext`, etc.).
- `module`: Module format (`commonjs`, `ES2022`, `NodeNext`).
- `strict`: Enables all strict type-checking options.
- `outDir` / `rootDir`: Control the output file layout.
- `declaration`: Emit `.d.ts` declaration files.
- `jsx`: Controls how JSX/TSX is transformed (`react`, `react-jsx`, `preserve`).
- `lib`: Specifies which built-in API declarations are available (`ES2022`, `DOM`, etc.).

## Key Parameters

- `noImplicitAny`: Prevents implicit `any` types.
- `strictNullChecks`: Treats `null` and `undefined` as distinct types.
- `noImplicitReturns`: Requires all code paths in a function to return a value.
- `noUnusedParameters` / `noUnusedLocals`: Warn on unused variables.
- `esModuleInterop`: Enables smoother importing from CommonJS modules.
- `skipLibCheck`: Skips type checking of declaration files to speed up compilation.

## When To Use

- Always create a `tsconfig.json` for any non-trivial TypeScript project.
- Enable `strict: true` for new projects.
- Tune `target` and `module` to match your runtime environment (Node.js version, bundler, or browser support matrix).

## Risks & Pitfalls

- **Misaligned `target`**: Emitting modern syntax for an old runtime causes runtime errors.
- **Overly permissive options**: Disabling `strictNullChecks` or `noImplicitAny` hides a large class of bugs.
- **Monolithic configs**: A single `tsconfig.json` for both source and tests can produce conflicting settings or emit unwanted files.

## Related Concepts

- [[concepts/static-typing-in-typescript]]
- [[concepts/declaration-files]]
- [[concepts/jsx-in-typescript]]

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapter 5
