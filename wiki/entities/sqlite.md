---
title: "SQLite"
type: entity
tags: [entity, tool, database, sql, python]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/practices-of-the-python-pro-book/"]
confidence: high
---

## Overview

SQLite is a self-contained, serverless, zero-configuration SQL database engine. It stores data in a single ordinary disk file (usually with a `.db` extension), making it convenient for local applications, prototyping, and embedded systems.

## Characteristics

- Included in Python's standard library via the `sqlite3` module.
- Supports standard SQL operations: `CREATE TABLE`, `INSERT`, `SELECT`, `UPDATE`, `DELETE`.
- Transactions protect data integrity; if a statement fails, the database rolls back to its last known working state.
- Placeholders (`?`) should be used in queries to prevent SQL injection.
- Portable across operating systems; deleting the `.db` file resets the database.

## Common Strategies

- Use SQLite for local-first or single-user applications (e.g., desktop tools, mobile apps, command-line utilities).
- Wrap database interactions in a manager class that handles connection lifecycle, transaction context managers, and parameterized queries.
- Migrate to a client-server database (PostgreSQL, MySQL) only when concurrency, scale, or network access requirements outgrow SQLite's capabilities.

## Sources

- *Practices of the Python Pro*, Chapter 6 — Separation of concerns in practice
- https://sqlite.org
