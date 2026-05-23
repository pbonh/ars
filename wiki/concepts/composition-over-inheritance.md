---
title: "Composition Over Inheritance"
type: concept
tags: [concept, object-oriented-programming, software-design, python]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/"]
confidence: high
---

## Definition

Composition over inheritance is the design principle that objects should achieve polymorphic behavior and code reuse by containing instances of other classes ("has-a" relationships) rather than inheriting from a parent class ("is-a" relationships). It frees a design from the rigid constraints of class hierarchies while still providing relatedness between concepts.

## How It Works

In composition, a class is built from smaller, focused objects. For example, a `Dog` can speak and roll over not because it inherits from a `TrickAnimal`, but because it composes `SpeakMixin` and `RollOverMixin` behaviors:

```python
class SpeakMixin:
    def speak(self):
        name = self.__class__.__name__.lower()
        print(f'The {name} says, "Hello!"')

class RollOverMixin:
    def roll_over(self):
        print('Did a barrel roll!')

class Dog(SpeakMixin, RollOverMixin):
    pass
```

Even when multiple inheritance is used to achieve composition (as with mixins), the mental model is "has these capabilities" rather than "is a specialized version of."

Python's duck typing means strict interfaces are not required for composition to work. Any object can be substituted for another as long as it has the expected methods and attributes.

## Key Parameters

- **"Has-a" vs. "is-a"**: Composition models capability ownership; inheritance models taxonomic specialization.
- **Mixins**: A common Python pattern where a mixin class provides a narrow, reusable behavior to be composed into other classes.
- **Flexibility**: Composed objects can be swapped at runtime, whereas inherited behavior is fixed at class definition time.

## When To Use

Prefer composition when:
- You need to reuse behavior without forcing it into a rigid hierarchy.
- The relationship between concepts is "has a capability" rather than "is a kind of."
- You anticipate needing to combine behaviors in ways that a single inheritance tree cannot accommodate.
- You want to avoid the fragility of deep class hierarchies.

## Risks & Pitfalls

- **Indirection**: Heavily composed systems can make it harder to trace which object provides a given method. Good naming and documentation mitigate this.
- **Not a ban on inheritance**: Inheritance is still appropriate for true specialization with shallow, narrow hierarchies.

## Related Concepts

- [[concepts/inheritance]] — the alternative mechanism, appropriate for specialization
- [[concepts/inversion-of-control]] — enables swapping composed dependencies

## Sources

- *Practices of the Python Pro*, Chapter 3 — Abstraction and encapsulation
- *Practices of the Python Pro*, Chapter 8 — The rules (and exceptions) of inheritance
