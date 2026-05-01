# Page Format Reference

Detailed format specifications for each wiki page type. Referenced by the wiki-ingest skill.

## Common Frontmatter

Every page begins with YAML frontmatter:

```yaml
---
title: "Page Title"
type: concept | entity | summary | synthesis
tags: [tag1, tag2, tag3]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: ["raw/filename.txt"]
confidence: high | medium | low
---
```

**Fields:**
- `title` — Display title in quotes. Should match the filename slug.
- `type` — One of: `concept`, `entity`, `summary`, `synthesis`
- `tags` — Array of lowercase-hyphenated tags from the AGENTS.md taxonomy
- `created` — ISO 8601 date when the page was first created
- `updated` — ISO 8601 date when the page was last modified
- `sources` — Array of `raw/` source file paths that inform this page
- `confidence` — `high`, `medium`, or `low` (see confidence definitions)

## Summary Pages (`wiki/summaries/`)

One per raw source document. Filename: `<source-slug>.md`

**Required sections:**

```markdown
## Key Points

- Bulleted list of the main claims and ideas from the source
- Each point should be self-contained and understandable without reading the source
- Include concrete examples and specific details

## Relevant Concepts

- [[concepts/concept-name]] — brief note on why this concept appears in the source
- [[concepts/another-concept]] — ...

## Source Metadata

- **Type**: article | video-transcript | podcast-transcript | paper | book-excerpt | notes
- **Author/Speaker**: name
- **Date**: YYYY-MM-DD (publication or recording date, if known)
- **URL**: full URL or identifier
- **Retrieved**: YYYY-MM-DD
```

## Concept Pages (`wiki/concepts/`)

Abstract ideas, strategies, frameworks, methods. One concept per page. Filename: `<concept-slug>.md`

**Required sections:**

```markdown
## Definition

One paragraph in plain English. Define any domain-specific jargon on first use.
A reader unfamiliar with the domain should understand this definition.

## How It Works

The mechanics, process, or structure of the concept.
Use numbered steps for processes, sub-bullets for components.

## Key Parameters

- **Parameter Name**: description, typical values or ranges, impact

## When To Use

Situations and contexts where this concept applies. Contrast with alternatives
when available (link to synthesis pages for detailed comparisons).

## Risks & Pitfalls

Known failure modes, common mistakes, limitations, and when NOT to apply this concept.

## Related Concepts

- [[concepts/related-concept]] — how they connect
- [[concepts/another-concept]] — ...

## Sources

- [[summaries/source-slug]] — specific section or claim
```

## Entity Pages (`wiki/entities/`)

Concrete things: people, tools, organizations, products, species, locations. Filename: `<entity-slug>.md`

**Required sections:**

```markdown
## Overview

What this entity is in 1-2 sentences. Name it, categorize it, give the essential facts.

## Characteristics

- **Property**: value or description
- Use a table for structured data:

| Property | Value |
|----------|-------|
| property1 | value1 |
| property2 | value2 |

## Common Strategies

How this entity is typically used, approached, or interacted with — link to concept pages:

- [[concepts/strategy-name]] — how it applies to this entity

## Related Entities

- [[entities/related-entity]] — relationship description
```

## Synthesis Pages (`wiki/syntheses/`)

Cross-cutting analyses comparing multiple pages or drawing novel conclusions. Filename: `<synthesis-slug>.md`

**Required sections:**

```markdown
## Comparison

Structured comparison table:

| Dimension | Approach A | Approach B |
|-----------|------------|------------|
| dimension1 | value | value |
| dimension2 | value | value |

## Analysis

Cross-cutting insights that emerge from comparing these pages.
What patterns do you see? What contradictions exist?

## Recommendations

When to prefer which approach. Decision criteria:
- Use X when... because...
- Use Y when... because...

## Pages Compared

- [[concepts/page-a]]
- [[concepts/page-b]]
```

## Confidence Levels

- **high** — Corroborated by 2+ independent sources, demonstrated with concrete examples, no contradictory evidence
- **medium** — Supported by sources but limited to single source or light on examples
- **low** — Single mention, anecdotal, speculative, or contradicted by other sources

When confidence is `low`, add a note in the relevant section explaining why:
```markdown
> ⚠️ Low confidence: single mention in [[summaries/source-slug]], not corroborated.
```