---
title: "Liskov Substitution Principle"
type: concept
tags: [concept, object-oriented-programming, software-design, python]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/"]
confidence: high
---

## Definition

The Liskov substitution principle (LSP), formulated by Barbara Liskov, states that in a program, any instance of a class must be replaceable by an instance of one of its subclasses without affecting the correctness of the program. "Correctness" means the program remains error-free and achieves the same basic outcomes, though the precise result may differ or be achieved in a different manner.

## How It Works

Substitutability arises from subclasses strictly adhering to their superclass's interface. In Python, this is not enforced by the type system; it is a design discipline. A subclass that:
- Changes the signature of an inherited method (e.g., adds required arguments to `__init__`)
- Raises exceptions the superclass does not raise
- Returns fundamentally incompatible types

...breaks substitutability. Code written against the superclass will fail when a non-substitutable subclass is used.

A practical way to assess substitutability is to examine the **role** a set of classes fills. If each class in a hierarchy can fulfill that role, they are likely substitutable. If a subclass changes method signatures or raises new exceptions as part of its specialization, it may not fulfill the role, suggesting that composition might be more appropriate than inheritance.

## Key Parameters

- **Interface compliance**: Subclasses must honor the contracts (method names, signatures, and expected behavior) established by the superclass.
- **Preconditions and postconditions**: A subclass should not strengthen preconditions or weaken postconditions relative to the superclass.

## When To Use

Apply the Liskov substitution principle as a guardrail whenever you use inheritance:
- Before creating a subclass, ask: "Can this subclass be dropped in anywhere the superclass is expected?"
- If the answer is no, reconsider whether inheritance is the right tool; composition may be preferable.

## Risks & Pitfalls

- **Implicit contracts**: Python's dynamic typing makes it easy to violate LSP accidentally. Documentation and code review are essential.
- **Overriding to do nothing**: A subclass that overrides a method to do nothing (`pass`) or raises `NotImplementedError` often signals that the inheritance relationship is wrong.

## Related Concepts

- [[concepts/inheritance]] — the mechanism that makes LSP relevant
- [[concepts/abstract-base-class]] — can enforce interface compliance in Python

## Sources

- *Practices of the Python Pro*, Chapter 8 — The rules (and exceptions) of inheritance
