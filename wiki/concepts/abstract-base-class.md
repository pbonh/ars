---
title: "Abstract Base Class"
type: concept
tags: [concept, object-oriented-programming, python, interfaces]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/"]
confidence: high
---

## Definition

An abstract base class (ABC) in Python is a class that cannot be instantiated directly. It acts as a template that defines which methods and attributes its subclasses must implement. ABCs provide a way to enforce interfaces in Python's dynamically typed environment, supplementing the duck typing philosophy with explicit structural contracts.

## How It Works

Python provides the `abc` module for creating abstract base classes:

- Inherit from `ABC` (or have `ABCMeta` as the metaclass) to mark a class as abstract.
- Use the `@abstractmethod` decorator on methods that subclasses must implement.
- Any subclass that fails to implement an abstract method will raise a `TypeError` at instantiation time.

Example:

```python
from abc import ABC, abstractmethod

class Predator(ABC):
    @abstractmethod
    def eat(self, prey):
        pass

class Bear(Predator):
    def eat(self, prey):
        print(f'Mauling {prey}!')
```

ABCs can also include concrete methods and properties, but adding real behavior to a class that claims to be abstract can confuse readers. The primary purpose is to enforce a minimal interface.

## Key Parameters

- **`@abstractmethod`**: Marks a method that must be overridden.
- **Instantiation prevention**: Direct instantiation of an ABC raises `TypeError`.
- **IDE support**: Type checkers and IDEs can warn when a subclass has the wrong method signature.

## When To Use

Use abstract base classes when:
- Duck typing alone is insufficient and you need stronger guarantees that a family of classes implements the same interface.
- You are building a plugin architecture or framework where third parties must adhere to a contract.
- You want IDE assistance in catching missing or mismatched method signatures early.

## Risks & Pitfalls

- **Over-engineering**: Python's culture favors duck typing. Reaching for ABCs too often can make code feel unnecessarily bureaucratic.
- **Runtime, not compile-time**: Python enforces ABCs at instantiation, not at import or type-check time (unless using static analysis tools).

## Related Concepts

- [[concepts/inheritance]] — ABCs use inheritance to enforce interfaces
- [[concepts/liskov-substitution-principle]] — ABCs help ensure subclasses remain substitutable
- [[concepts/loose-coupling]] — ABCs provide the shared abstractions that reduce coupling

## Sources

- *Practices of the Python Pro*, Chapter 8 — The rules (and exceptions) of inheritance
