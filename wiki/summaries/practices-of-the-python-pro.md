---
title: "Practices of the Python Pro"
type: summary
tags: [summary, python, software-design, object-oriented-programming]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/"]
confidence: high
---

## Overview

*Practices of the Python Pro* by Dane Hillard is a mid-level Python book that teaches software design principles through practical examples. It targets developers who know Python basics and want to move from writing scripts to building maintainable, complex systems. The book uses Python 3.7+ as its vehicle and builds a command-line bookmarking application called **Bark** across several chapters to demonstrate each concept in practice.

The core thesis is that design is a continuous, iterative process—not a one-time upfront activity. The book emphasizes separation of concerns, abstraction, encapsulation, testing, and loose coupling as foundational practices that compound over time to produce software that is easier to understand, extend, and maintain.

## Key Claims

- [[concepts/separation-of-concerns]] is the cornerstone of clear code; it should guide decisions about functions, classes, modules, and packages.
- [[concepts/abstraction]] reduces cognitive load by hiding implementation details behind well-named interfaces, enabling developers to reason about code at the appropriate level of granularity.
- [[concepts/encapsulation]] groups related data and behavior into barriers (classes, modules, packages) that protect internals from external knowledge.
- [[concepts/decomposition]] breaks large problems into small, manageable pieces that can be recomposed; it enables abstraction and testability.
- [[concepts/big-o-notation]] provides a qualitative language for reasoning about how code consumes time and space as inputs grow.
- [[concepts/lazy-evaluation]] (via generators) can dramatically reduce memory footprint by producing one value at a time instead of materializing full collections.
- [[concepts/test-driven-development]] puts testing first, guiding implementation from requirements and building confidence for refactoring.
- The [[concepts/test-pyramid]] recommends investing most testing effort in fast, granular unit tests, fewer integration tests, and only critical end-to-end or load tests.
- The [[concepts/command-pattern]] decouples presentation layer menu options from business logic by encapsulating each action as an object with a uniform `execute` interface.
- [[concepts/extensibility]] means adding new behavior by adding new code, not editing existing code; rigidity manifests as [[concepts/loose-coupling|shotgun surgery]].
- [[concepts/inversion-of-control]] makes dependencies pluggable by accepting them from the caller rather than constructing them internally.
- [[concepts/loose-coupling]] allows pieces of code to interact without relying heavily on each other's details, often achieved through shared abstractions and message-oriented thinking.
- [[concepts/inheritance]] should be used for specialization of behavior, not code reuse; [[concepts/liskov-substitution-principle|substitutability]] and shallow, narrow hierarchies are critical guardrails.
- [[concepts/cyclomatic-complexity]] measures execution paths and identifies code that has grown too branch-heavy to be easily understood or tested.
- [[concepts/abstract-base-class]] in Python (via the `abc` module) can enforce interfaces when duck typing alone is insufficient.

## Source Metadata

- **Type**: Book (mdBook source)
- **Title**: Practices of the Python Pro
- **Author**: [[entities/dane-hillard]]
- **Publisher**: Manning Publications
- **Year**: 2020
- **ISBN**: 9781617296086
- **URL**: https://www.manning.com/books/practices-of-the-python-pro
- **License**: Proprietary (purchased book; source code under MIT-like usage for readers)
- **Ingested on**: 2026-05-23

## Relevant Concepts

- [[concepts/separation-of-concerns]] — introduced
- [[concepts/abstraction]] — introduced
- [[concepts/encapsulation]] — introduced
- [[concepts/decomposition]] — introduced
- [[concepts/big-o-notation]] — introduced
- [[concepts/lazy-evaluation]] — introduced
- [[concepts/test-driven-development]] — introduced
- [[concepts/test-pyramid]] — introduced
- [[concepts/command-pattern]] — introduced
- [[concepts/extensibility]] — introduced
- [[concepts/inversion-of-control]] — introduced
- [[concepts/loose-coupling]] — introduced
- [[concepts/inheritance]] — introduced
- [[concepts/liskov-substitution-principle]] — introduced
- [[concepts/cyclomatic-complexity]] — introduced
- [[concepts/abstract-base-class]] — introduced

## Relevant Entities

- [[entities/dane-hillard]] — author
- [[entities/pytest]] — testing framework discussed extensively
- [[entities/sqlite]] — database used in the Bark application
- [[entities/requests]] — HTTP library used for the GitHub stars importer
