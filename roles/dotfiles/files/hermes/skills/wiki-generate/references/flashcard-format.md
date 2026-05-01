# Flashcard Format Reference

Spaced repetition flashcards for the [Spaced Repetition](https://github.com/st3v3nmw/obsidian-spaced-repetition) Obsidian plugin.

## File Location

Flashcards live in `wiki/flashcards.md`. This file can hold a master deck. Page-specific decks can be appended inline on concept pages under a `## Flashcards` section.

## Card Format

Each card uses this exact syntax:

```
Question text goes here
?
Answer text goes here
```

Rules:
- Single `?` on its own line separates question from answer (required by the Spaced Repetition plugin)
- Separate multiple cards with a blank line
- Questions should be answerable in 1-3 sentences
- Answers should be self-contained (don't reference "see above" or "as mentioned earlier")

## Card Types

| Type | Question Pattern | Example |
|------|-----------------|---------|
| **Definition** | "What is X?" | "What is the attention mechanism?" |
| **Comparison** | "How does X differ from Y?" | "How does high confidence differ from medium confidence?" |
| **Process** | "What are the steps for X?" | "What are the steps in the ingest workflow?" |
| **Application** | "When would you use X?" | "When would you use a synthesis page vs a concept page?" |
| **Pitfall** | "What is a common mistake with X?" | "What is a common mistake when setting confidence levels?" |

## Generation Strategy

When generating flashcards from a wiki page:

1. Extract 5-10 key facts from the page
2. Convert each fact into one of the card types above
3. Ensure questions test understanding, not just recall
4. Vary card types — don't make all cards definition-type
5. Append to `wiki/flashcards.md` under a heading like `## Cards from [[concepts/concept-name]]`

## Example Output

```markdown
## Cards from [[concepts/attention-mechanism]]

What is the attention mechanism in transformer models?
?
A method that allows a model to weigh the importance of different input tokens when producing each output token, computing attention scores via query-key-value projections.

How does self-attention differ from cross-attention?
?
Self-attention computes attention within the same sequence (Q, K, V all from same input). Cross-attention computes attention between two different sequences (Q from one, K and V from another).

When should you use multi-head attention over single-head attention?
?
Use multi-head attention when you need the model to attend to information from different representation subspaces simultaneously — each head can focus on different relationships (syntax, semantics, position).
```