---
title: "Obsidian CLI Developer Commands"
type: concept
tags: [concept, obsidian, cli, developer-tools, plugin-development, automation]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/obsidian-cli.md"]
confidence: high
---

## Definition

Obsidian CLI Developer Commands are a dedicated subset of the Obsidian CLI surface area exposed for plugin and theme developers. They provide programmatic access to Electron developer tools, the Chrome DevTools Protocol (CDP), DOM and CSS inspection, mobile emulation, screenshots, and live JavaScript evaluation inside the Obsidian renderer process.

## How It Works

- **`devtools`** toggles the Electron developer tools window.
- **`dev:debug`** attaches or detaches a Chrome DevTools Protocol debugger.
- **`dev:cdp`** runs arbitrary CDP methods by name with JSON-encoded parameters.
- **`dev:screenshot`** captures the current Obsidian window as a base64-encoded PNG; an optional `path` parameter writes it to disk.
- **`dev:css`** inspects CSS properties and source locations for a given selector.
- **`dev:dom`** queries DOM elements by CSS selector, returning outerHTML, innerHTML, text content, attributes, or counts.
- **`dev:mobile`** toggles mobile viewport emulation for testing responsive themes and plugins.
- **`dev:errors`** and **`dev:console`** expose captured JavaScript errors and console messages with optional filtering by log level.
- **`eval`** executes arbitrary JavaScript in the Obsidian app context and returns the result, enabling direct inspection of `app.vault`, `app.workspace`, and other internal APIs.

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| `method=<CDP.method>` | CDP method name for `dev:cdp`. |
| `params=<json>` | JSON object of parameters for the CDP method. |
| `selector=<css>` | CSS selector for `dev:css` and `dev:dom`. |
| `prop=<name>` | Filter `dev:css` results to a specific CSS property. |
| `attr=<name>` | Retrieve a specific attribute value in `dev:dom`. |
| `code=<javascript>` | JavaScript expression or statement for `eval`. |
| `path=<filename>` | Output file path for `dev:screenshot`. |

## When To Use

- Automating plugin and theme testing workflows (reload, screenshot diff, DOM assertions).
- Building agentic coding tools that need to inspect or interact with Obsidian’s live UI and data model.
- Debugging CSS regressions by inspecting computed styles and source locations.
- Prototyping JavaScript snippets against the live app without writing a full plugin.
- Capturing visual regression screenshots across theme or plugin changes.

## Risks & Pitfalls

- **`eval` privilege**: Scripts run with full access to the Obsidian `app` object; buggy or malicious code can corrupt vault data or leak sensitive notes.
- **CDP fragility**: CDP method names and behavior depend on the bundled Electron/Chromium version and may break across Obsidian upgrades.
- **Screenshot privacy**: Screenshots capture the entire window, which may include sensitive note content or API keys visible in the UI.
- **Production risk**: Developer commands are intended for local development vaults. Using them on production or shared vaults risks unintended data mutation.

## Related Concepts

- [[concepts/obsidian-cli]] — the overall command-line interface.
- [[entities/obsidian]] — the Obsidian application.

## Sources

- raw/obsidian-cli.md
