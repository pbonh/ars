---
title: "Rust Smart Pointers"
type: concept
tags: [concept, rust, memory-management, data-structures]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Definition

Smart pointers are data structures that act like pointers but include additional metadata and capabilities. In Rust, smart pointers usually *own* the data they point to (unlike references, which only borrow).

## How It Works

Smart pointers are typically implemented as structs that implement `Deref` and `Drop`:

- `Deref`: allows the smart pointer to be treated like a reference (enables deref coercion).
- `Drop`: customizes cleanup when the smart pointer goes out of scope.

Common standard-library smart pointers:

1. **`Box<T>`**: allocates data on the heap. Used for recursive types, large values, or transferring ownership without copying.
2. **`Rc<T>`**: reference counting for multiple immutable owners on a single thread. `Rc::clone` increments the count; when the last `Rc` is dropped, the data is freed.
3. **`RefCell<T>`**: provides interior mutability at runtime via borrow checking. Allows mutation through an immutable reference, but panics if borrowing rules are violated at runtime. Used inside `Rc` when shared mutable access is needed: `Rc<RefCell<T>>`.
4. **`Arc<T>`**: thread-safe version of `Rc` (atomic reference counting).
5. **`Mutex<T>` / `RwLock<T>`**: thread-safe interior mutability; `Mutex` is often combined with `Arc`.

## Key Parameters

- `Box::new(value)`: heap allocation.
- `Rc::clone(&rc)` / `Arc::clone(&arc)`: increment reference count (not deep copy).
- `RefCell::borrow()` / `borrow_mut()`: runtime borrow checking.
- `Deref coercion`: `&Box<T>` automatically coerces to `&T`.

## When To Use

Use smart pointers when:
- Data size is unknown at compile time or must live on the heap.
- Multiple parts of the program need shared ownership.
- Interior mutability is required (e.g., cyclic data structures, shared state in GUIs).

## Risks & Pitfalls

- **Reference cycles**: `Rc` (and `Arc`) can leak memory if strong reference cycles exist; use `Weak<T>` to break cycles.
- **Runtime panics**: `RefCell` panics on violated borrow rules at runtime; these are logic errors, not compile-time safety.
- **Overhead**: `Rc`/`RefCell` add reference-counting or locking overhead compared to plain references.

## Related Concepts

- [[concepts/rust-ownership]] — smart pointers extend ownership to shared or heap scenarios
- [[concepts/rust-borrowing]] — `Deref` enables smart pointers to behave like references
- [[concepts/rust-concurrency]] — `Arc` and `Mutex` are concurrency-aware smart pointers

## Sources

- *The Rust Programming Language*, Chapter 15 — Smart Pointers
