# Marp Presentation Format Reference

Slide decks generated from wiki content using [Marp](https://marp.app/) markdown.

## File Location

Presentations live in `wiki/presentations/<topic-slug>.md`.

## Marp Frontmatter

Every presentation starts with:

```yaml
---
marp: true
theme: default
paginate: true
size: 16:9
title: "Presentation Title"
---
```

## Slide Structure

Slides are separated by `---` on its own line:

```markdown
---
marp: true
---

# Title Slide

## Subtitle

Author | Date

---

# Slide Title

Content goes here.

- Bullet points
- With `code` and **bold**

---

# Another Slide

More content.
```

## Content Patterns

| Wiki Content | Marp Slide |
|-------------|------------|
| Concept definition | Title + definition paragraph + key points as bullets |
| Process/steps | Title + numbered steps, one sub-bullet each |
| Comparison table | Title + markdown table |
| Key parameters | Title + definition list or table |
| Source summary | Title + 3-5 key takeaways as bullets |

## Generation Strategy

When generating a presentation from wiki content:

1. Determine the audience and scope (ask the user if unclear)
2. Select 5-15 relevant wiki pages
3. Structure slides:
   - Slide 1: Title
   - Slide 2: Agenda/overview
   - Slides 3-N: One slide per major concept or section
   - Final slide: Summary + links back to wiki
4. Keep slides focused — one idea per slide
5. Use the page's confidence level to decide inclusion: high-confidence content should dominate

## Example

```markdown
---
marp: true
theme: default
paginate: true
size: 16:9
title: "Understanding Transformer Architectures"
---

# Understanding Transformer Architectures

## A Knowledge Base Overview

Generated from the wiki | 2026-05-01

---

# Agenda

1. What is a Transformer?
2. The Attention Mechanism
3. Encoder-Decoder Structure
4. Key Innovations
5. Summary

---

# What is a Transformer?

A neural network architecture introduced in "Attention Is All You Need" (Vaswani et al., 2017).

**Key innovation**: Replaces recurrence with self-attention, enabling:
- Parallel computation across sequence positions
- Better handling of long-range dependencies
- Scalability to very large models

---

# The Attention Mechanism

Self-attention computes weighted representations by comparing each token to every other token.

Steps:
1. Project input into Query (Q), Key (K), Value (V)
2. Compute attention scores: Q·K^T / √d_k
3. Apply softmax to get weights
4. Weighted sum of Values

---

# Summary

- Transformers revolutionized NLP through parallelizable attention
- Self-attention captures relationships between all token pairs
- Multi-head attention provides multiple representation subspaces
- The architecture scales to billions of parameters

**Wiki**: [[concepts/transformers]], [[concepts/attention-mechanism]]
```