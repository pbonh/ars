---
name: wiki
description: Use when the user mentions a wiki, knowledge base, knowledge graph, or any wiki-* skill — provides architecture overview, detects existing wikis, and routes to sibling skills
---

# Wiki

## Architecture

A wiki is a three-layer system:
```
raw/           ← Immutable source documents (never modified)
  ↓ (ingest)
wiki/          ← Structured knowledge pages (concepts, entities, summaries, syntheses)
  ↓ (customize)
AGENTS.md      ← Domain-specific schema, tagging taxonomy, purpose
```

The `raw/` directory holds source documents. The `wiki/` tree holds structured pages with Obsidian-style `[[links]]`, YAML frontmatter, and confidence levels (high/medium/low). `AGENTS.md` (or `CLAUDE.md`) provides domain customization.

## Detection

Check for 3 of 4 signals:
1. `wiki/index.md` exists
2. `wiki/log.md` exists
3. `AGENTS.md` or `CLAUDE.md` exists with wiki-related frontmatter or directory layout
4. `wiki/summaries/`, `wiki/concepts/`, `wiki/entities/` directories exist

Run detection at session start. If wiki detected, load this skill.

## Conventions

- **Naming**: all-lowercase-hyphenated filenames (`concept-name.md`)
- **Linking**: Obsidian-style `[[concepts/concept-name]]`, relative from wiki root
- **Confidence**: high (multi-source corroborated), medium (single-source), low (speculative)
- **Immutability**: never modify `raw/` files
- **Date format**: ISO 8601 (YYYY-MM-DD)

## Coordination

When wiki work begins, check for existing wiki via detection. Then route:
- No wiki → use `wiki-bootstrap`
- Collect sources → use `wiki-collect`
- Ingest sources → use `wiki-ingest`
- Answer questions → use `wiki-query`
- Audit health → use `wiki-lint`
- Log sessions → use `wiki-journal`
- Generate artifacts → use `wiki-generate`

**REQUIRED SUB-SKILLS:** wiki-bootstrap, wiki-collect, wiki-ingest, wiki-query, wiki-lint, wiki-journal, wiki-generate