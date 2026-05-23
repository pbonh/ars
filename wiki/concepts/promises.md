---
title: "Promises"
type: concept
tags: [concept, asynchronous-programming, concurrency, functional-programming]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

A promise is an object representing the eventual completion or failure of an asynchronous operation and its resulting value. It allows attaching callbacks to handle success (`then`) or failure (`catch`), providing a structured alternative to deeply nested callbacks.

## How It Works

- A promise starts in a **pending** state. It transitions to **fulfilled** with a value when the asynchronous operation succeeds, or to **rejected** with a reason when it fails.
- `then(onFulfilled, onRejected)` registers handlers and returns a new promise, enabling chaining. Each handler’s return value becomes the fulfillment value of the next promise in the chain.
- `catch(onRejected)` is shorthand for `then(undefined, onRejected)` and handles rejection anywhere in the chain.
- Promises flatten nested asynchronous calls into a linear pipeline, making control flow easier to follow than raw callbacks.

## Key Parameters

- **Immutability**: Once a promise is settled (fulfilled or rejected), its state and value cannot change. This makes promises predictable and safe to share.
- **Eager evaluation**: A promise begins executing immediately upon creation; it does not wait for a handler to be attached.
- **Error propagation**: An unhandled rejection in a promise chain skips all `then` handlers until a `catch` is found, similar to exception bubbling.

## When To Use

Use promises when:
- You are sequencing asynchronous operations (network requests, file I/O, timers).
- You want to centralize error handling for a chain of async steps.
- You need to compose multiple concurrent operations with `Promise.all` or `Promise.race`.

## Risks & Pitfalls

- **Unhandled rejections**: A rejected promise without a catch handler can crash the process or emit warnings, depending on the runtime.
- **Sequential confusion**: `Promise.all` runs concurrently, but a chain of `.then` runs sequentially. Mixing the two incorrectly leads to performance or ordering bugs.
- **Callback migration**: Converting callback-based APIs to promises requires care to ensure errors are properly captured.

## Related Concepts

- [[concepts/async-await]] — syntactic sugar that makes promise chains look like synchronous code
- [[concepts/monad]] — promises form a monad (unit = `Promise.resolve`, bind = `then`)
- [[concepts/first-class-functions]] — promise handlers are first-class functions passed to `then`/`catch`

## Sources

- *Programming with Types*, Chapter 6 — Advanced applications of function types (section 6.4)
