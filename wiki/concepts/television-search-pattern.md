---
title: "Television Search Pattern"
type: concept
tags: [concept, fuzzy-finder, search, query-syntax]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/television-repo/docs"]
confidence: high
---

## Definition

A **search pattern** is the query syntax Television uses to filter entries. Patterns are evaluated by the [`nucleo-matcher`](https://docs.rs/nucleo-matcher) engine and can be combined with implicit AND logic to form complex queries.

## How It Works

Television supports five matchers, each triggered by a prefix or suffix on the search term:

| Matcher | Pattern | Behavior |
|---------|---------|----------|
| Fuzzy | `foo` | Fuzzy match against the entry. |
| Substring | `'foo` | Exact substring match. Negate with `!foo`. |
| Prefix | `^foo` | Entry must start with the term. Negate with `!^foo`. |
| Suffix | `foo$` | Entry must end with the term. Negate with `!foo$`. |
| Exact | `^foo$` | Entry must equal the term exactly. Negate with `!^foo$`. |

Multiple patterns separated by spaces are combined with AND logic. For example:

```
car 'bike !^car !bike$
```

translates to: fuzzy-match `car`, contain exact substring `bike`, do not start with `car`, and do not end with `bike`.

The `--exact` CLI flag switches the entire query to substring matching instead of fuzzy, which can improve performance on very large datasets.

## Key Parameters

| Flag / Setting | Effect |
|----------------|--------|
| `--exact` | Use substring matching globally instead of fuzzy. |
| `!` prefix on any pattern | Negate (exclude) that pattern. |
| Space between patterns | AND logic. |

## When To Use

Use fuzzy matching for general exploration when you don't know the exact string. Use substring (`'`), prefix (`^`), suffix (`$`), or exact (`^...$`) when you need precise control, and combine them to narrow large result sets. Use `--exact` for performance-critical scripted queries on huge datasets.

## Risks & Pitfalls

- Negation patterns (`!...`) can be confusing with shell history expansion in some shells; quoting the tv command may be necessary.
- Fuzzy matching on extremely large entry lists (hundreds of thousands) may lag; limit source output or use `--exact` in those cases.
- The matcher behavior is delegated to `nucleo-matcher`; edge-case behavior (e.g., Unicode handling) follows that crate's rules.

## Related Concepts

- [[concepts/television-channel]]
- [[concepts/television-frecency-sorting]]
- [[entities/nucleo-matcher]]

## Sources

- Television docs: Search patterns reference, tips and tricks.
