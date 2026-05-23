---
title: "npm"
type: entity
tags: [entity, package-manager, registry, javascript]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Overview

npm (Node Package Manager) is the default package manager for Node.js and the registry for the JavaScript ecosystem. It handles dependency installation, version management, script execution, and package publishing. TypeScript projects rely on npm to install the TypeScript compiler, type definitions (`@types/*`), and third-party libraries.

## Characteristics

- **Registry**: Hosts over two million packages, including frameworks, utilities, and type declaration packages.
- **SemVer**: Uses semantic versioning (`major.minor.patch`) for dependency resolution.
- `package.json`: The manifest that declares dependencies, scripts, and project metadata.
- `node_modules`: The local directory where installed packages reside.
- `package-lock.json`: Locks dependency versions for reproducible installs.

## Common Strategies

- Installing TypeScript globally or per-project via `npm install -D typescript`.
- Installing type definitions for untyped libraries with `npm install -D @types/<package>`.
- Using `npx` to run locally installed CLI tools (e.g., `npx tsc`) without global installation.
- Publishing compiled TypeScript libraries to npm with generated declaration files for downstream type safety.

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapter 5
- [npmjs.com](https://www.npmjs.com)
