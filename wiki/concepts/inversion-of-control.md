---
title: "Inversion of Control"
type: concept
tags: [concept, software-design, dependency-management, python]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/"]
confidence: high
---

## Definition

Inversion of control (IoC) is the principle of shifting the responsibility for creating or managing dependencies from a class itself to the code that calls or constructs it. Instead of a class instantiating the objects it needs internally, those objects are passed in from the outside. This makes dependencies pluggable and reduces rigidity.

## How It Works

Consider a `Bicycle` class that needs tires and a frame. Without IoC, the bicycle creates its own parts:

```python
class Bicycle:
    def __init__(self):
        self.front_tire = Tire()
        self.back_tire = Tire()
        self.frame = Frame()
```

With IoC, the bicycle receives its parts:

```python
class Bicycle:
    def __init__(self, front_tire, back_tire, frame):
        self.front_tire = front_tire
        self.back_tire = back_tire
        self.frame = frame
```

The caller now controls which concrete implementations are used:

```python
bike = Bicycle(Tire(), Tire(), CarbonFiberFrame())
```

This allows swapping `CarbonFiberFrame` for `Frame`, or passing a `MockTire` during testing, without editing the `Bicycle` class.

## Key Parameters

- **Dependency injection**: A specific form of IoC where dependencies are supplied via constructor arguments, setters, or interfaces.
- **Flexibility**: The consumer class no longer needs to know all possible types of dependencies it might ever need.
- **Testability**: IoC makes it easier to isolate a class under test by substituting real dependencies with test doubles.

## When To Use

Use inversion of control when:
- A class has dependencies that might vary (different databases, API clients, hardware interfaces).
- You want to test a class in isolation without mocking classes it hardcodes internally.
- You are building a framework that should allow users to customize behavior.
- You see a class doing too much object construction inside its initializer.

## Risks & Pitfalls

- **Boilerplate**: IoC can shift complexity to the composition root, where all objects are wired together. Dependency injection frameworks can help but may introduce their own complexity.
- **Over-application**: Not every object needs to be injected. Primitive configuration values or stable, internal helpers may still be constructed internally.

## Related Concepts

- [[concepts/extensibility]] — IoC is a key enabler of extensible code
- [[concepts/loose-coupling]] — reduces coupling by removing hardcoded dependencies

## Sources

- *Practices of the Python Pro*, Chapter 7 — Extensibility and flexibility
