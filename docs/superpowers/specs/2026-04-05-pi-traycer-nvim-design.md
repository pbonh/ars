# pi-traycer.nvim Design Specification

## Overview

pi-traycer.nvim is a standalone Neovim plugin that provides a Traycer-like AI-assisted development workflow using the pi coding agent's RPC mode. It delivers spec-driven development — epics, plans, trackable tasks — through a multi-panel UI built on snacks.nvim and edgy.nvim, all without leaving the terminal.

**Core value:** Transform high-level specifications into actionable, trackable implementation plans through structured AI interaction in Neovim.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Distribution | Standalone repo (`pbonh/pi-traycer.nvim`) | Clean separation from ars, installable by anyone via lazy.nvim |
| UI approach | Snacks-first, edgy for docking only | Smaller dependency surface, leverages snacks' integrated API |
| Pi integration | RPC-only (`pi --mode rpc`) | Clean separation from interactive terminal mode |
| Plan extraction | Pi extension (`create_plan` tool) | Structured JSON contract, no fragile markdown parsing |
| Architecture | Event-driven hub | Loose coupling, mirrors pi's event-based protocol, testable modules |
| Default layout | Right chat + bottom plan | Mirrors Traycer's VS Code layout for chat-heavy workflows |

## Architecture

Three layers with an event-driven hub at the core.

### UI Layer

Three independent modules, each subscribing to RPC events:

- **chat.lua** — snacks split window (right side, 40% width). Two buffers in a vertical split: a read-only message history buffer (top, scrollable) showing conversation and tool output, and an editable input buffer (bottom, small fixed height) where the user types. `Enter` in the input buffer sends the message and clears the input. Subscribes to: `message_update`, `tool_execution_*`, `agent_start`, `agent_end`.
- **plan.lua** — edgy-docked panel (bottom, 30% height). Epic list, task tree with status checkboxes, dependency visualization. Subscribes to: `tool_execution_*` (intercepts `create_plan` tool calls).
- **extension_ui.lua** — transient snacks popups. Renders pickers, inputs, confirms on demand when pi extensions request input. Subscribes to: `extension_ui_request`.

### Core Layer

- **rpc.lua** — the event hub. Spawns `pi --mode rpc`, manages JSONL stdin/stdout protocol, dispatches events via `rpc.on(event_type, handler)`, sends commands via `rpc.send_command(cmd)`.
- **state.lua** — shared read-only state store. Current session info, active epic, token/cost stats. Updated on `agent_end` and plan changes.
- **context.lua** — gathers `FileContext` per prompt: cwd, open buffers, cursor position, visual selection, optional git status.

### Infrastructure

- **commands.lua** — `:Pi*` command registration
- **keymaps.lua** — global and buffer-local keymap setup
- **config.lua** — defaults, user opts merging, validation
- **init.lua** — `setup()`, health check, API exports

### Event Flow

```
User types in chat → chat.lua
  → context.lua gathers FileContext
  → rpc.send_command({ type = "prompt", message = "...", context = {...} })
  → pi stdin receives JSON + \n

Pi emits events on stdout:
  agent_start → message_update (text_delta) → tool_execution_* → agent_end

rpc.lua splits on \n, parses JSON, dispatches to subscribers:
  → chat.lua: text_delta → append to buffer, auto-scroll
  → chat.lua: tool_execution_* → render collapsible tool output
  → plan.lua: tool_execution_* → intercept create_plan tool, persist epic
  → state.lua: agent_end → update token/cost stats
```

### Critical RPC Implementation Details

- JSONL framing splits on `\n` only — never Unicode line separators (`U+2028`/`U+2029`)
- `tool_execution_update` contains accumulated output (replace display, don't append)
- Steering messages delivered after current tool calls complete
- Follow-up messages queue until `agent_end`
- Process crash triggers up to 3 restart attempts, then notifies user

## Pi Extension: create_plan

A minimal TypeScript extension (~30 lines) that registers a `create_plan` tool. Pi calls this tool to output structured plan data instead of freeform markdown.

```typescript
// extensions/create-plan.ts
export default {
  name: "create-plan",
  tools: [{
    name: "create_plan",
    description: "Create or update an implementation plan with structured tasks and dependencies",
    parameters: {
      type: "object",
      properties: {
        epic_title: { type: "string" },
        tasks: {
          type: "array",
          items: {
            type: "object",
            properties: {
              id: { type: "string" },
              title: { type: "string" },
              description: { type: "string" },
              dependencies: { type: "array", items: { type: "string" } }
            },
            required: ["id", "title"]
          }
        }
      },
      required: ["epic_title", "tasks"]
    }
  }]
}
```

The extension does no LLM calls, no file I/O, no UI. It is purely a structured output channel. The Neovim plugin intercepts the tool call via `tool_execution_start` events, extracts the args, and persists the plan.

The extension ships in the plugin repo (`extensions/create-plan.ts`) and installs into `~/.pi/agent/extensions/`.

## Data Model

### Entities

**Session** (pi-owned, read-only to plugin)
- id, name, epic_id (optional), token_stats
- Stored at `.pi/sessions/<name>.jsonl` (pi's native JSONL format)
- Plugin reads for token stats only, never writes

**Epic** (plugin-owned)
- id, title, description (markdown), status (draft | active | done)
- session_id (links to pi session), plan (embedded)
- Stored at `.pi/plans/<epic-id>.json`

**Task** (embedded in Epic)
- id ("task-1"), title, description, status (pending | active | done)
- dependencies (task ID array), files_changed (populated during work)

### Relationships

```
Session ←1:1→ Epic ←1:*→ Task ←*:*→ Task (dependencies)
```

### Ownership Boundary

Pi owns session files (JSONL). The plugin owns plan files (JSON). The `create_plan` extension is the bridge — pi calls the tool, the plugin intercepts and persists.

### What Persists Across Restarts

- Epic + plan + task statuses → `.pi/plans/<epic-id>.json`
- Chat history → pi's session file (re-read on reconnect)
- Plugin config → user's `setup(opts)` in Neovim config

## UI Layout

Default: right chat (40%) + bottom plan (30%). All positions/sizes configurable.

```
┌─────────────────────────────────┬──────────────────┐
│                                 │                  │
│         Editor Buffers          │    Chat Panel    │
│                                 │   (snacks.nvim)  │
│                                 │                  │
├─────────────────────────────────│  Messages +      │
│         Plan Panel              │  streaming +     │
│        (edgy.nvim)              │  tool output +   │
│  Epic → Tasks → Dependencies   │  input area      │
└─────────────────────────────────┴──────────────────┘
```

## Commands

| Command | Action |
|---------|--------|
| `:PiChat [message?]` | Toggle chat panel. If message provided, send immediately. |
| `:PiEpic [title?]` | Create new epic — opens spec buffer. |
| `:PiPlan [epic-id?]` | Toggle plan panel. Shows current or specific epic. |
| `:PiFileAdd [path?]` | Add file to context. Defaults to current buffer. |
| `:PiBash <command>` | Run bash through pi (output in chat). |
| `:PiAbort` | Cancel current streaming operation. |
| `:PiStatus` | Show token usage, cost, context % via snacks notification. |

## Keymaps

| Mapping | Action | Scope |
|---------|--------|-------|
| `<leader>pc` | Toggle chat | Global |
| `<leader>pe` | Create/focus epic | Global |
| `<leader>pp` | Toggle plan panel | Global |
| `<leader>ps` | Send visual selection to chat | Visual mode |
| `<leader>pa` | Abort | Global |
| `Enter` | Focus task / send message | Plan buffer / Chat input |
| `t` | Toggle task status | Plan buffer |
| `d` | View task details | Plan buffer |
| `q` | Close panel | Chat/Plan buffer |

All keymaps configurable via `setup(opts)`. Set to `false` to disable.

## Configuration

```lua
require("pi-traycer").setup({
  chat = { position = "right", size = 0.4 },
  plan = { position = "bottom", size = 0.3 },
  keymaps = {
    chat = "<leader>pc",
    epic = "<leader>pe",
    plan = "<leader>pp",
    send_selection = "<leader>ps",
    abort = "<leader>pa",
  },
  pi = {
    model = nil,
    thinking = nil,
    session_dir = nil,
  },
  notifications = {
    cost_on_completion = true,
    context_warning_pct = 80,
  },
})
```

## Project Structure

```
pi-traycer.nvim/
├── lua/pi-traycer/
│   ├── init.lua              -- setup(), health(), API exports
│   ├── config.lua            -- defaults, opts merging, validation
│   ├── rpc.lua               -- pi process spawn, JSONL protocol, event hub
│   ├── chat.lua              -- chat panel UI (snacks), streaming, tool display
│   ├── plan.lua              -- plan panel (edgy), task tree, epic CRUD, persistence
│   ├── context.lua           -- FileContext gathering
│   ├── extension_ui.lua      -- extension_ui_request handler (snacks pickers/inputs)
│   ├── state.lua             -- shared state store
│   ├── commands.lua          -- :Pi* command registration
│   └── keymaps.lua           -- keymap setup
├── plugin/
│   └── pi-traycer.lua        -- auto-load: check pi executable, warn if missing
├── extensions/
│   └── create-plan.ts        -- pi extension: create_plan tool
├── tests/
│   ├── minimal_init.lua      -- plenary test bootstrap
│   ├── rpc_spec.lua          -- JSONL framing, event parsing
│   ├── chat_spec.lua         -- message formatting, buffer management
│   ├── plan_spec.lua         -- epic CRUD, task tree, JSON persistence
│   └── extension_ui_spec.lua -- request/response routing
└── README.md
```

## Dependencies

| Required | Purpose |
|----------|---------|
| Neovim 0.10+ | `vim.system()` for async process management |
| snacks.nvim | All UI: windows, pickers, input, notifications |
| edgy.nvim | Panel docking (plan panel) |
| plenary.nvim | Test framework, async utilities |
| pi (in PATH) | AI backend via RPC mode |

nui.nvim removed from dependencies — not needed with snacks-first approach.

## Testing Strategy

**Unit tests (plenary.nvim):**
- `rpc_spec.lua` — JSONL framing (strict `\n` split), event parsing, command formatting
- `chat_spec.lua` — message history buffer management, streaming text accumulation
- `plan_spec.lua` — epic CRUD, task tree building, JSON round-trip persistence
- `extension_ui_spec.lua` — request routing, response formatting, timeout handling

**Manual E2E acceptance:**
1. `:PiChat` opens panel, type message, streaming response appears
2. Tool execution visible in chat (bash commands + output)
3. `:PiEpic "Test"` creates epic, pi calls `create_plan`, plan panel populates
4. Task status toggling persists across Neovim restart
5. `:PiAbort` stops streaming immediately
6. `:PiStatus` shows accurate token/cost info

## Error Handling

| Error | Detection | Response |
|-------|-----------|----------|
| pi not in PATH | `vim.fn.executable("pi")` on setup | Error notification, disable commands |
| RPC process crash | read_loop exit | Up to 3 restart attempts, then notify |
| JSON parse error | `pcall` on decode | Log to `:messages`, skip event, continue |
| Extension UI timeout | Timer in handler | Auto-send cancellation response |
| Context limit approaching | Token stats from `get_state` | Warning notification at configured threshold |
