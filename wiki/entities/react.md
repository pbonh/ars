---
title: "React"
type: entity
tags: [entity, library, facebook, meta, typescript, frontend, jsx]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Overview

React is a JavaScript library for building user interfaces, developed and maintained by Meta (formerly Facebook). It uses a component-based architecture and a virtual DOM to efficiently update the UI. React can be used with TypeScript via TSX files, providing type safety for component props, state, and hooks.

## Characteristics

- **Component-based**: UI is composed of reusable, self-contained components.
- **Virtual DOM**: Efficient diffing and patching of the actual DOM.
- **Hooks**: Functions like `useState`, `useEffect`, and `useContext` manage state and side effects in functional components.
- **JSX/TSX**: HTML-like syntax embedded in JavaScript/TypeScript.
- **Unopinionated**: React is a view layer; routing, state management, and data fetching are handled by companion libraries.

## Common Strategies

- Using TypeScript interfaces or type aliases to define component `props` and `state` shapes.
- Leveraging generic hooks (e.g., `useState<T>`) to preserve type information through React's state management.
- Combining React with Vite, Next.js, or Create React App (legacy) for bundling and development server workflows.

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapters 20–21
- [react.dev](https://react.dev)
