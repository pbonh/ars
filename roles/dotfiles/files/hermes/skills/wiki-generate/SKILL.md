---
name: wiki-generate
description: Use when the user asks for flashcards, a slide deck, a presentation, or a diagram from wiki content
---

# Wiki Generate

Produce artifacts on demand from wiki content: flashcards, Marp slide decks, and Mermaid diagrams.

**REQUIRED REFERENCES:**
- `references/flashcard-format.md` — Spaced repetition flashcard spec
- `references/marp-format.md` — Marp presentation spec
- `references/mermaid-format.md` — Mermaid diagram type catalog

## Generation Workflow

### 1. Determine what to generate

Ask or detect from user request:
- "make flashcards" → flashcards
- "create slides" / "presentation" → Marp
- "draw a diagram" / "visualize" → Mermaid

### 2. Select source pages

Identify which wiki pages to use as source material. If the user specifies pages, use those. Otherwise:
- **Flashcards**: recent concept and entity pages
- **Slides**: synthesis pages, or a set of related concept pages
- **Diagrams**: pages with rich cross-link data

### 3. Generate artifact

Use the format reference for the selected artifact type. The reference file contains the exact format specs, card types, slide patterns, and diagram syntax.

### 4. Write to file

- **Flashcards**: Append to `wiki/flashcards.md` (or create if missing) under a heading naming the source page
- **Marp slides**: Write to `wiki/presentations/<topic-slug>.md`
- **Mermaid diagrams**: Embed inline in the relevant page, or write standalone to `wiki/presentations/<slug>-diagram.md`

### 5. Report

```
Generated [artifact type] from [source pages].
Saved to: [file path].
Open in Obsidian with [plugin name] to view interactively.
```

## Tool Requirements

Requires `file` toolset. Wiki must have content pages to generate from.