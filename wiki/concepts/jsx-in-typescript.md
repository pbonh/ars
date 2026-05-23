---
title: "JSX in TypeScript"
type: concept
tags: [concept, typescript, jsx, react, web-development]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/essential-typescript-5-book/"]
confidence: high
---

## Definition

JSX in TypeScript (TSX) is the syntax extension that allows HTML-like markup to be written directly inside TypeScript code. TypeScript compiles TSX files to JavaScript function calls, typically targeting React's `createElement` or the newer JSX transform.

## How It Works

TypeScript supports JSX via the `jsx` compiler option. Files using JSX must have the `.tsx` extension. The compiler option `jsx` controls the output mode:
- `preserve`: Keeps JSX syntax for another tool (e.g., Babel) to transform.
- `react`: Transforms JSX into `React.createElement` calls.
- `react-jsx` / `react-jsxdev`: Uses the newer automatic JSX runtime (React 17+) without requiring React to be in scope.

The `jsxFactory` and `jsxFragmentFactory` options allow custom frameworks to replace React as the JSX backend.

Example:
```tsx
function Greeting({ name }: { name: string }) {
    return <h1>Hello, {name}</h1>;
}
```

## Key Parameters

- `jsx`: Controls JSX transformation strategy.
- `jsxFactory`: The function used to create elements (default `React.createElement`).
- `jsxFragmentFactory`: The function used for fragments (default `React.Fragment`).
- Type definitions for JSX elements come from a global `JSX` namespace, usually provided by the framework's type package (e.g., `@types/react`).

## When To Use

- Use `.tsx` for any file containing JSX syntax.
- Use `react-jsx` for modern React projects to avoid importing React solely for JSX.
- Use `preserve` when a bundler (Vite, esbuild, Webpack) handles JSX transformation and TypeScript should only type-check.

## Risks & Pitfalls

- **Missing type definitions**: Without `@types/react` (or equivalent), JSX element names produce `any` and provide no IntelliSense.
- **Fragment syntax**: The `<>...</>` shorthand requires the `jsxFragmentFactory` to be configured correctly.
- **Component prop types**: Failing to type component props leads to implicit `any` on JSX attributes.

## Related Concepts

- [[concepts/tsconfig-configuration]]
- [[concepts/static-typing-in-typescript]]
- [[concepts/shape-types]]

## Sources

- *Essential TypeScript 5, Third Edition* (Adam Freeman), Chapters 16, 20, 21
