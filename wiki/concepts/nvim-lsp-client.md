---
title: "Neovim LSP Client"
type: concept
tags: [concept, neovim, lsp, language-server, ide]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nvim-docs/lsp.txt", "raw/nvim-docs/help.txt"]
confidence: high
---

## Definition

The Neovim LSP Client is a built-in Language Server Protocol client framework (`vim.lsp`) that enables IDE-like features — go-to-definition, hover, completion, rename, format, diagnostics — by communicating with external LSP servers. It uses a config-driven activation model with sensible defaults and an event-based attach mechanism.

## How It Works

1. **Config Definition**: Define an LSP config with `vim.lsp.config(name, { cmd, filetypes, root_markers, settings })` or place it in `lsp/<name>.lua` on `runtimepath`.
2. **Enable**: Call `vim.lsp.enable(name)` to auto-activate the config for matching filetypes.
3. **Attach**: When a buffer with a matching `filetype` opens, Nvim starts the server and fires `LspAttach`.
4. **Defaults**: Nvim sets default keymaps (`gra`, `gri`, `grn`, `grr`, `grt`, `grx`, `gO`, `CTRL-S`), sets `'omnifunc'` and `'tagfunc'`, enables diagnostics, and maps `K` to hover.
5. **Dynamic Configuration**: Use `LspAttach` / `Client:on_attach()` to add buffer-local keymaps, auto-format on save, or enable completion.
6. **Config Merging**: Configs merge via `vim.tbl_deep_extend('force')` in priority order: `'*'` global < `lsp/<name>.lua` < `after/lsp/<name>.lua` < inline `vim.lsp.config()` calls.

## Key Parameters

- `cmd`: command and arguments to start the server
- `filetypes`: list of filetypes to auto-attach
- `root_markers`: files/directories that define the workspace root (nested lists = equal priority)
- `settings`: server-specific JSON settings
- `capabilities`: LSP client capabilities (merged from `vim.lsp.protocol.make_client_capabilities()`)
- `autocmd`: `LspAttach`, `LspDetach`, `LspNotify`, `LspProgress`, `LspRequest`

## When To Use

- Use for any language where an LSP server exists (see Microsoft LSP implementors list).
- Prefer `lsp/<name>.lua` files for reusable configs; use `after/lsp/` to override plugins like nvim-lspconfig.
- Use `LspAttach` to gate custom features behind `client:supports_method()`.

## Risks & Pitfalls

- **Server not running**: The config defines how to start the server, but the server binary must be installed separately.
- **Root marker missing**: Some servers fail to attach if no `root_markers` file is found; ensure projects have `.git`, `package.json`, or equivalent markers.
- **Default keymap collisions**: Global defaults like `gra` may conflict with existing mappings; delete with `vim.keymap.del()` if needed.
- **Performance**: `workspace/didChangeWatchedFiles` is enabled by default (except Linux); large workspaces may see file-watching overhead — disable in capabilities if needed.
- **Dynamic registration**: Capabilities may be registered after `LspAttach`; handle `client/registerCapability` if you gate features strictly on attach-time capabilities.

## Related Concepts

- [[concepts/nvim-diagnostic-framework]]
- [[concepts/nvim-treesitter-integration]]
- [[entities/nvim-lspconfig]]

## Sources

- [Neovim LSP Reference](raw/nvim-docs/lsp.txt)
- [Neovim Help Index](raw/nvim-docs/help.txt)
