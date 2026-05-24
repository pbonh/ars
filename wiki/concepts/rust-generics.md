---
title: "Rust Generics"
type: concept
tags: [concept, rust, type-system, generic-programming]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Definition

Generics are abstract stand-ins for concrete types or other properties. They allow functions, structs, enums, and methods to operate on many different data types while remaining type-safe.

## How It Works

Type parameters are declared inside angle brackets `<>` after a name:

```rust
fn largest<T>(list: &[T]) -> &T { ... }
struct Point<T> { x: T, y: T }
enum Option<T> { Some(T), None }
```

Trait bounds restrict a generic type to those that implement specific behavior:

```rust
fn largest<T: PartialOrd>(list: &[T]) -> &T { ... }
```

Multiple bounds use `+`: `T: Display + Clone`.

Rust implements generics via *monomorphization*: the compiler generates a separate concrete copy of the generic code for each type it is called with. This means there is zero runtime overhead compared to hand-written duplicates; generics in Rust are *zero-cost abstractions*.

## Key Parameters

- Type parameter names: by convention single uppercase letters (`T`, `U`, `E`).
- Trait bounds: `T: Trait` ensures the generic type supports required methods.
- `where` clauses: alternative syntax for complex bounds, improving readability.
- Associated types: traits can declare type placeholders (e.g., `Iterator::Item`) that implementors define.

## When To Use

Use generics when:
- A function or type should work with multiple concrete types.
- You want to avoid code duplication without sacrificing type safety.
- Defining containers (`Vec<T>`, `HashMap<K, V>`) or algorithms (`sort`, `max`).

## Risks & Pitfalls

- **Monomorphization bloat**: Excessive use of generics with many distinct types can increase binary size.
- **Trait bound complexity**: Deeply nested bounds become hard to read; prefer `where` clauses.
- **Generic recursion limits**: The compiler has a default recursion depth for generic types; deeply nested generics may require increasing it.

## Related Concepts

- [[concepts/rust-traits]] — generics are usually constrained by traits
- [[concepts/rust-struct]] — structs can be generic
- [[concepts/rust-enum]] — enums can be generic (Option, Result)
- [[concepts/rust-lifetimes]] — lifetime parameters are another kind of generic

## Sources

- *The Rust Programming Language*, Chapter 10.1 — Generic Data Types
