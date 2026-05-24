---
title: "Rust Traits"
type: concept
tags: [concept, rust, type-system, interfaces, polymorphism]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Definition

A trait defines shared behavior in an abstract way. It is similar to an interface in other languages: it groups method signatures that specify a set of behaviors necessary to accomplish some purpose.

## How It Works

Traits are declared with the `trait` keyword and implemented with `impl Trait for Type`:

```rust
pub trait Summary {
    fn summarize(&self) -> String;
}

impl Summary for NewsArticle {
    fn summarize(&self) -> String { ... }
}
```

Traits enable:

- **Default implementations**: Methods in a trait can have bodies, so implementors only override what they need.
- **Trait bounds**: `fn notify<T: Summary>(item: &T)` accepts any type that implements `Summary`.
- **Trait objects**: `&dyn Summary` allows heterogeneous types at runtime via dynamic dispatch.
- **Operator overloading**: Traits like `Add`, `Deref`, `Drop` hook into language features.
- **Extension traits**: Add methods to foreign types (orphan rules apply).

The `#[derive(...)]` attribute auto-implements common traits (`Debug`, `Clone`, `PartialEq`, etc.) based on struct/enum contents.

## Key Parameters

- `trait` definition: method signatures grouped under a trait name.
- `impl Trait for Type`: binds a concrete type to a trait.
- `dyn Trait`: trait object for runtime polymorphism.
- `impl Trait`: opaque return type (syntactic sugar for unnamed concrete types).
- Supertraits: `trait Foo: Bar` means any type implementing `Foo` must also implement `Bar`.

## When To Use

Use traits when:
- Multiple types share a common behavior (e.g., `Display`, `Serialize`).
- You need to write generic code that operates on any type supporting a specific operation.
- You want to add methods to existing types or override operators.

## Risks & Pitfalls

- **Orphan rules**: You can only implement a trait for a type if either the trait or the type is local to your crate.
- **Trait object safety**: Not all traits can be made into `dyn Trait` objects (methods must not use `Self` or generic type parameters by value).
- **Coherence**: Overlapping blanket implementations are forbidden to keep trait resolution unambiguous.

## Related Concepts

- [[concepts/rust-generics]] — traits constrain generic parameters
- [[concepts/rust-struct]] — structs gain behavior via trait implementations
- [[concepts/rust-lifetimes]] — traits can have lifetime requirements

## Sources

- *The Rust Programming Language*, Chapter 10.2 — Traits: Defining Shared Behavior
