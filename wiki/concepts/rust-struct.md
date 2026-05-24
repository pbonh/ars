---
title: "Rust Struct"
type: concept
tags: [concept, rust, data-structures, type-system]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Definition

A struct is a custom data type that groups together related named fields of potentially different types. Unlike tuples, field names make the meaning of each value explicit and remove ordering constraints.

## How It Works

Rust provides three struct flavors:

1. **Named-field structs**: `struct User { active: bool, username: String, sign_in_count: u64 }`
2. **Tuple structs**: `struct Color(i32, i32, i32);` — named wrapper around a tuple, useful for type distinctions without field names.
3. **Unit-like structs**: `struct AlwaysEqual;` — no fields, useful for trait implementations or markers.

Structs can have *methods* and *associated functions* defined in `impl` blocks. Methods take `self` (or `&self`, `&mut self`) as their first parameter. Associated functions (like constructors) do not take `self`; `String::from` and `Vec::new` are common examples.

Field init shorthand allows `User { email, username, active: true, sign_in_count: 1 }` when local variables match field names. Struct update syntax (`..user1`) copies remaining fields from another instance.

## Key Parameters

- `#[derive(Debug, Clone, PartialEq, ...)]`: auto-implements common traits.
- `self`, `&self`, `&mut self`: method receivers controlling ownership and mutability.
- Associated functions: constructors and utilities scoped to the type.

## When To Use

Use structs when:
- You need to bundle multiple related values into a single type.
- You want named fields for clarity rather than positional tuple access.
- You need to attach behavior (methods) to a data type.

## Risks & Pitfalls

- **Partial moves**: Moving individual fields out of a non-`Copy` struct can make the rest unusable.
- **Recursive types**: A struct containing itself directly has infinite size; use `Box<T>` or another indirection.
- **Field order does not matter for construction**, but ergonomics favor update syntax when copying many fields.

## Related Concepts

- [[concepts/rust-enum]] — when a value should be one of several alternatives
- [[concepts/rust-traits]] — shared behavior across structs
- [[concepts/rust-generics]] — generic structs (e.g., `Point<T>`)

## Sources

- *The Rust Programming Language*, Chapter 5 — Using Structs to Structure Related Data
