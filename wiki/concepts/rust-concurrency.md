---
title: "Rust Concurrency"
type: concept
tags: [concept, rust, concurrency, parallelism, fearless-concurrency]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Definition

Fearless concurrency is Rust’s approach to concurrent and parallel programming: the ownership and type systems prevent data races and other concurrency bugs at compile time, allowing programmers to refactor concurrent code with confidence.

## How It Works

Rust provides several concurrency models, all grounded in ownership:

1. **Threads**: `std::thread::spawn` creates an OS thread. The `join` handle waits for completion.
2. **Message passing**: `mpsc` (multiple producer, single consumer) channels transfer ownership of data between threads. Because ownership moves, there is no shared mutable state.
3. **Shared-state concurrency**: `Mutex<T>` provides interior mutability with locking; `Arc<T>` (atomic reference counting) allows multiple threads to share ownership of immutable data. `Mutex` and `Arc` are often combined as `Arc<Mutex<T>>`.
4. **Send and Sync traits**: `Send` means a type can be transferred across thread boundaries; `Sync` means a type can be safely referenced from multiple threads. The compiler automatically derives these for types composed only of `Send`/`Sync` fields.

Because the borrow checker already prevents mutable aliasing, a mutable reference cannot be shared between threads unless properly synchronized. This eliminates data races by construction.

## Key Parameters

- `thread::spawn(|| ...)`: create a new thread.
- `mpsc::channel()`: create a message channel.
- `Mutex::new(data)`: mutual exclusion wrapper.
- `Arc::new(data)`: thread-safe reference counting.
- `Send` / `Sync`: marker traits for thread safety.

## When To Use

Use Rust concurrency when:
- CPU-bound work should be split across cores.
- I/O-bound work should be multiplexed (though async/await is often preferred for massive I/O concurrency).
- You need a safe, low-level foundation for higher-level async runtimes.

## Risks & Pitfalls

- **Deadlocks**: Rust cannot prevent deadlocks at compile time; locking order discipline remains the programmer’s responsibility.
- **Poisoned mutexes**: If a thread panics while holding a `Mutex`, the mutex becomes poisoned to signal potential inconsistency.
- **Channel backpressure**: Unbounded channels can exhaust memory; bounded channels (`sync_channel`) require senders to wait.

## Related Concepts

- [[concepts/rust-ownership]] — ownership is the foundation of thread safety
- [[concepts/rust-traits]] — `Send` and `Sync` are auto-traits
- [[concepts/rust-unsafe]] — some synchronization primitives use unsafe internals

## Sources

- *The Rust Programming Language*, Chapter 16 — Fearless Concurrency
