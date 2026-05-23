---
title: "Node.js"
type: entity
tags: [entity, runtime, javascript, server-side]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Overview

Node.js is an open-source, cross-platform JavaScript runtime built on Chrome's V8 JavaScript engine. It enables JavaScript execution outside the browser, making it the dominant runtime for server-side applications, build tools, CLIs, and development workflows. TypeScript compiles to JavaScript that runs on Node.js.

## Characteristics

- **Event-driven, non-blocking I/O**: Scalable network applications using an asynchronous, single-threaded event loop.
- **V8 engine**: Shares the same high-performance JIT compiler as Google Chrome.
- **NPM ecosystem**: Ships with npm, the world's largest package registry.
- **CommonJS and ESM**: Supports both `require`/`module.exports` and ES Module `import`/`export` syntax.
- **LTS releases**: Predictable long-term support schedule for production deployments.

## Common Strategies

- Using Node.js as the execution target for compiled TypeScript in backend services and tooling.
- Managing TypeScript projects via `npm` and `package.json`, including installing the `typescript` compiler as a dev dependency.
- Running TypeScript directly in development with tools like `ts-node` or `tsx` before compiling for production.

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapters 2, 5
- [nodejs.org](https://nodejs.org)
