---
title: "Inheritance"
type: concept
tags: [concept, object-oriented-programming, software-design, python]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/"]
confidence: high
---

## Definition

Inheritance is an object-oriented programming mechanism in which a class (subclass) acquires the data and behavior of another class (superclass). In Python, inheritance is used for *specialization of behavior*: a subclass should be a special case of its superclass, overriding or extending methods to provide differentiated functionality. It is not primarily a tool for code reuse.

## How It Works

In Python, a subclass is declared by placing the superclass in parentheses:

```python
class CarbonFiberFrame(Frame):
    pass
```

The subclass inherits all attributes and methods from the superclass. It can:
- **Override** methods to change their behavior.
- **Extend** methods by calling `super()` to invoke the superclass version before or after its own logic.

Python supports **multiple inheritance**, where a subclass may have two or more direct superclasses. Python resolves method lookups via the **method resolution order (MRO)**, a depth-first, left-to-right ordering with duplicates removed and subclasses moved before their parents.

### Ideal use cases
Sandi Metz's ground rules for when inheritance is appropriate:
- The problem has a **shallow, narrow** hierarchy.
- Subclasses are at the **leaves** of the object graph and don't introduce unique dependencies.
- Subclasses **use or specialize all** the behavior of their superclass.

## Key Parameters

- **"Is-a" relationship**: Inheritance models specialization. A `CarbonFiberFrame` *is a* `Frame`.
- **Substitutability**: The [[concepts/liskov-substitution-principle]] states that instances of a subclass must be replaceable for instances of the superclass without breaking correctness.
- **Composition vs. inheritance**: Composition ("has-a") is preferred for reusing behavior without confining it to a hierarchy.

## When To Use

Use inheritance when:
- You are modeling a true taxonomic specialization (e.g., `Rectangle` is a `Quadrilateral`).
- The hierarchy will remain shallow and narrow.
- Subclasses will use or override all superclass behavior, not ignore large portions of it.
- You need to enforce a common interface across related types and want to share some default behavior.

## Risks & Pitfalls

- **Deep hierarchies**: Deeply nested class trees make it hard to trace behavior and create "spooky action at a distance"—changes to a superclass can inadvertently break distant subclasses.
- **Inheritance for reuse**: Using inheritance only to share code leads to rigid hierarchies and tight coupling. Prefer composition for reuse.
- **Breaking substitutability**: Changing method signatures or raising unexpected exceptions in subclasses breaks the "is-a" contract and causes bugs.

## Related Concepts

- [[concepts/liskov-substitution-principle]] — defines correct substitutability
- [[concepts/abstract-base-class]] — enforces interfaces in Python
- [[concepts/composition-over-inheritance]] — preferred alternative for code reuse

## Sources

- *Practices of the Python Pro*, Chapter 8 — The rules (and exceptions) of inheritance
