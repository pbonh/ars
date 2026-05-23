---
title: "Async/Await"
type: concept
tags: [concept, asynchronous-programming, concurrency, syntax]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

Async/await is syntactic sugar built on top of promises (or similar asynchronous primitives) that allows asynchronous code to be written with the same linear structure as synchronous code. An `async` function implicitly returns a promise, and the `await` keyword pauses execution until a promise settles, without blocking the event loop or thread.

## How It Works

- Marking a function `async` makes it return a promise wrapping the function’s return value (or rejection if an exception is thrown).
- The `await` keyword can only appear inside an `async` function. It yields control back to the runtime until the awaited promise resolves, then resumes execution with the resolved value.
- Because the code reads top-to-bottom, error handling can use ordinary `try/catch` blocks instead of `.catch()` chains.
- The compiler or transpiler rewrites `async/await` into state-machine-based promise chains, preserving non-blocking semantics.

## Key Parameters

- **Execution model**: In single-threaded event-loop environments (e.g., JavaScript), `await` yields to the event loop; in multi-threaded environments, it may free the thread.
- **Error semantics**: Throwing inside an `async` function rejects the returned promise. Awaiting a rejected promise propagates the error as a thrown exception.
- **Sequential by default**: Multiple `await` statements run one after another. To run concurrently, compose promises with `Promise.all` before awaiting.

## When To Use

Use async/await when:
- You want the readability of synchronous code for asynchronous workflows.
- You are composing multiple dependent asynchronous operations.
- You want to use standard exception handling (`try/catch`) for async errors.

## Risks & Pitfalls

- **Sequential bottlenecks**: Awaiting unrelated operations one by one wastes time. Gather independent promises and await them together.
- **Top-level await**: Not all environments support `await` outside functions, requiring an async wrapper or module-level support.
- **Mixing styles**: Combining raw promises, callbacks, and async/await in the same codebase can create confusion about when errors are caught.

## Related Concepts

- [[concepts/promises]] — async/await is a thin layer over promises
- [[concepts/monad]] — async/await is the syntactic face of the continuation monad
- [[concepts/state-machine]] — the compiler transforms async functions into state machines

## Sources

- *Programming with Types*, Chapter 6 — Advanced applications of function types (section 6.4)
