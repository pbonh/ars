---
title: "Rust Macros"
type: concept
tags: [concept, rust, metaprogramming, code-generation]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/rust-book-book/"]
confidence: high
---

## Definition

Macros are a family of metaprogramming features in Rust that write code at compile time. They fall into two broad categories: declarative macros (`macro_rules!`) and procedural macros (custom `derive`, attribute-like, and function-like).

## How It Works

**Declarative macros** (`macro_rules!`) match the structure of source code against patterns, similar to `match` expressions. They are defined with:

```rust
#[macro_export]
macro_rules! vec {
    ( $( $x:expr ),* ) => {
        {
            let mut temp_vec = Vec::new();
            $( temp_vec.push($x); )*
            temp_vec
        }
    };
}
```

Repetition operators (`*`, `+`, `?`) and fragment specifiers (`expr`, `ty`, `pat`, `ident`, etc.) control parsing. Macros are hygienic: identifiers inside a macro do not collide with identifiers at the call site unless explicitly passed.

**Procedural macros** operate on token streams and are compiled as separate crates:

1. **Custom derive**: `#[derive(MyTrait)]` on structs/enums.
2. **Attribute-like macros**: `#[my_attribute]` on any item.
3. **Function-like macros**: `my_macro!(...)` similar to `macro_rules!` but with full token-manipulation power.

Macros differ from functions: they are expanded before type checking, accept variable argument counts, and can implement traits at compile time.

## Key Parameters

- `macro_rules!`: declarative macro definition.
- `#[macro_export]`: makes macro available when the crate is brought into scope.
- Repetition: `$( ... )*`, `$( ... )+`, `$( ... )?`.
- Fragments: `expr`, `ty`, `pat`, `ident`, `literal`, `tt` (token tree).
- `proc_macro` crate: required for procedural macros.

## When To Use

Use macros when:
- You need variable-arity APIs (e.g., `println!`, `vec!`).
- Boilerplate trait implementations should be generated automatically.
- Domain-specific languages or compile-time code generation are required.

## Risks & Pitfalls

- **Complex debugging**: Macro expansion errors can be cryptic because they reference generated code.
- **Compile-time cost**: Heavy macro use increases compile times.
- **Hygiene limitations**: While hygienic, cross-crate macro behavior can still be surprising with name resolution.

## Related Concepts

- [[concepts/rust-traits]] - derive macros generate trait implementations
- [[concepts/rust-struct]] - derive macros commonly target structs and enums
- [[concepts/rust-traits]] — derive macros generate trait implementations

## Sources

- *The Rust Programming Language*, Chapter 19.5 - Macros
