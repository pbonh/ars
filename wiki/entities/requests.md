---
title: "requests"
type: entity
tags: [entity, library, python, http]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/"]
confidence: high
---

## Overview

requests is a popular, user-friendly HTTP library for Python. Its tagline is "HTTP for Humans." It abstracts away much of the complexity of making network requests and handling responses, providing a simple API for `GET`, `POST`, `PUT`, `DELETE`, and other HTTP methods.

## Characteristics

- Simpler API than Python's built-in `urllib`.
- Returns `Response` objects with convenient attributes like `.json()`, `.text`, `.status_code`, and `.headers`.
- Supports sessions, cookies, authentication, and custom headers out of the box.
- Pagination metadata (e.g., GitHub's `Link` headers) is accessible via `response.links`.

## Common Strategies

- Use `requests.get(url, headers=...)` for REST API interactions.
- When testing code that uses `requests`, mock the specific calls (using `unittest.mock`) to avoid slow or destructive real network requests.
- For production services, consider handling timeouts, retries, and connection pooling explicitly rather than using default settings.

## Sources

- *Practices of the Python Pro*, Chapter 7 — Extensibility and flexibility
- https://requests.readthedocs.io
