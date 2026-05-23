---
title: "Short-Circuit Evaluation"
type: concept
tags: [concept, boolean-logic, control-flow, optimization]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

Short-circuit evaluation is the behavior of Boolean logical operators (`&&` and `||`) in which the second operand is evaluated only if the first operand does not already determine the result. If the first operand of `&&` is false, the overall expression must be false, so the second operand is skipped. If the first operand of `||` is true, the overall expression must be true, so the second operand is skipped.

## How It Works

- In `A && B`, evaluate `A`. If `A` is false, return false immediately without evaluating `B`. If `A` is true, evaluate `B` and return its Boolean value.
- In `A || B`, evaluate `A`. If `A` is true, return true immediately without evaluating `B`. If `A` is false, evaluate `B` and return its Boolean value.
- The skipped subexpression may contain side effects (function calls, assignments) that never execute, which programmers sometimes exploit for conditional behavior.

## Key Parameters

- **Operator associativity**: Chained expressions like `A && B && C` short-circuit left-to-right.
- **Truthiness**: In weakly typed languages, non-Boolean values are coerced to Booleans, so short-circuiting also returns the last evaluated value, not strictly `true` or `false`.
- **Side-effect dependency**: Relying on short-circuiting to guard expensive or unsafe operations (e.g., `obj && obj.value`) is idiomatic but fragile if the guard condition changes.

## When To Use

Use short-circuit evaluation when:
- You want to avoid unnecessary computation (e.g., checking a cheap condition before an expensive one).
- You need a guard to prevent invalid operations (e.g., checking for null before accessing a property).
- You are chaining Boolean conditions where early failure is expected and cheap.

## Risks & Pitfalls

- **Hidden side effects**: Skipping an expression with side effects can lead to subtle bugs if later code assumes the side effect occurred.
- **Readability**: Using `&&` and `||` for control flow rather than pure Boolean logic can confuse readers expecting simple predicates.
- **Type coercion**: In JavaScript, `0 && anything` returns `0`, not `false`, which can surprise developers using the result in a strict Boolean context.

## Related Concepts

- [[concepts/lazy-evaluation]] — short-circuiting is a form of lazy evaluation at the expression level
- [[concepts/type-safety]] — weakly typed short-circuiting can bypass type checks through truthiness coercion

## Sources

- *Programming with Types*, Chapter 2 — Basic types (section 2.2)
