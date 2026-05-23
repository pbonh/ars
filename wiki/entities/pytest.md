---
title: "pytest"
type: entity
tags: [entity, tool, testing-framework, python]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/"]
confidence: high
---

## Overview

pytest is a mature, full-featured testing framework for Python. It is widely used as an alternative or successor to Python's built-in `unittest` framework because it requires less boilerplate and produces more readable output.

## Characteristics

- Uses plain `assert` statements rather than custom assertion methods, with rich introspection of failures.
- Discovers tests automatically in files named `test_*.py` or `*_test.py`.
- Test classes are named `Test*` and do not need to inherit from a base class.
- Compatible with existing `unittest` tests, allowing incremental migration.
- Provides fixtures and plugins for setting up test environments and dependencies.

## Common Strategies

- Organize tests into classes for grouping, even though pytest does not strictly require it.
- Convert `unittest` tests incrementally by removing inheritance from `unittest.TestCase` and replacing `self.assertEqual(expected, actual)` with `assert actual == expected`.
- Use pytest as the default runner for new Python projects, falling back to `unittest` only when integration with the standard library is required without external dependencies.

## Sources

- *Practices of the Python Pro*, Chapter 5 — Testing with pytest
- https://docs.pytest.org
