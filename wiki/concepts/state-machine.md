---
title: "State Machine"
type: concept
tags: [concept, software-design, functional-programming, state-management]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/programming-with-types-book/"]
confidence: high
---

## Definition

A state machine (or finite-state machine) is a computational model consisting of a finite set of states, transitions between those states triggered by events or inputs, and actions executed during transitions or while in a state. Encoding a state machine in a type-safe way can eliminate invalid transitions at compile time.

## How It Works

- **Table-driven**: A transition table maps (currentState, event) -> nextState. This is flexible but offers no compile-time guarantees.
- **Function-based**: Each state is represented by a function that accepts valid inputs and returns the next state function. Invalid inputs are rejected by the type system because they do not appear in the function’s signature.
- **Type-state pattern**: The type of an object encodes its current state in the type system, so operations that are only valid in certain states are exposed only on the corresponding type.
- In the function-based approach, the state machine is a recursive composition of functions, eliminating the need for switch statements or large conditional blocks.

## Key Parameters

- **Determinism**: A deterministic state machine has exactly one next state for any (state, input) pair.
- **Completeness**: All possible inputs should be handled for every state; missing cases are gaps in the specification.
- **Side effects**: Actions executed on transitions may perform I/O or mutate shared state, complicating testing and reasoning.

## When To Use

Use a state machine when:
- The behavior of a component depends on its history (e.g., network connections, parsing, UI flows).
- Invalid transitions represent real bugs (e.g., sending data on a closed connection).
- You want the compiler to reject state-protocol violations.

## Risks & Pitfalls

- **State explosion**: As the number of states and inputs grows, the transition matrix or function graph can become unwieldy.
- **Distributed state**: If state is partially encoded in the type system and partially in mutable fields, the two can drift out of sync.
- **Overhead**: Function-based or type-state machines can introduce boilerplate or allocation overhead compared to a simple integer state variable.

## Related Concepts

- [[concepts/first-class-functions]] — function-based state machines treat states as functions
- [[concepts/encapsulation]] — state machines encapsulate valid behavior per state
- [[concepts/type-safety]] — type-state machines push state validity into the type checker

## Sources

- *Programming with Types*, Chapter 5 — Function types (section 5.2)
