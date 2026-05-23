---
title: "Angular"
type: entity
tags: [entity, framework, google, typescript, frontend]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Overview

Angular is a platform and framework for building single-page client applications using HTML, CSS, and TypeScript. Developed and maintained by Google, Angular provides a comprehensive solution with dependency injection, reactive programming (RxJS), a component system, routing, forms, and HTTP services. TypeScript is the primary language for Angular development.

## Characteristics

- **Opinionated framework**: Provides a complete toolchain (CLI, router, forms, HTTP, animations) out of the box.
- **Dependency injection**: Built-in DI system for services and components.
- **RxJS integration**: Heavy use of observables for asynchronous operations and reactive state management.
- **Decorators**: Historically relied on TypeScript's experimental decorators for `@Component`, `@Injectable`, and other metadata.
- **Ahead-of-Time (AOT) compilation**: Compiles templates and TypeScript to efficient JavaScript before deployment.

## Common Strategies

- Using the Angular CLI (`ng`) to scaffold projects, generate components, and manage builds.
- Structuring applications around modules, services, and components with clear separation of concerns.
- Using TypeScript interfaces and classes to define domain models, API contracts, and component APIs.

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapters 18–19
- [angular.io](https://angular.io)
