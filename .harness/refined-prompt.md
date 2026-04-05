A Neovim plugin that provides a Traycer-like AI-assisted development interface using the pi coding agent's RPC mode. The plugin creates a multi-panel UI (chat, plan viewer, status) using snacks.nvim for popups/notifications and edgy.nvim for panel layouts. Users interact with pi through structured chat, can create "Epic" specifications that generate implementation plans with trackable tasks, and manage the full development workflow without leaving Neovim.

## Tech Choices

| Category | Choice | Notes |
|----------|--------|-------|
| **Language** | Lua (pure runtime) | No build step required |
| **Neovim version** | 0.10+ | Required for snacks.nvim compatibility |
| **Plugin manager** | lazy.nvim | Distribution method |
| **Core UI** | snacks.nvim | Popups, notifications, pickers, input |
| **Layout management** | edgy.nvim | Sidebar/bottom panel layouts |
| **Utilities** | plenary.nvim | Lua stdlib, test framework |
| **Additional UI** | nui.nvim | Additional UI primitives if needed |
| **pi integration** | RPC mode (`pi --mode rpc`) | JSONL protocol over stdin/stdout |
| **LLM provider** | Fireworks (via pi) | FIREWORKS_API_KEY pre-defined in environment |
| **Excluded** | telescope.nvim | Use snacks picker instead |

## Data and Interfaces

### Core Data Structures

**ChatMessage** (aligned with pi's AgentMessage):
```lua
{
  role = "user" | "assistant" | "toolResult",
  content = string | table,  -- text blocks, tool calls, thinking blocks
  timestamp = number,
  -- assistant only: toolCalls[], usage{}, stopReason, model
}
```

**Epic/Plan** (plugin-managed, stored as JSON):
```lua
{
  id = "uuid",
  title = "Implement user authentication",
  description = "# Full markdown spec...",
  status = "draft" | "in_progress" | "completed",
  created_at = number,
  pi_session_file = ".pi/sessions/<epic-id>.jsonl",
  tasks = {
    {
      id = "task-1",
      title = "Add login form component",
      description = "...",
      status = "pending" | "in_progress" | "done",
      dependencies = {"task-0"},
      files_changed = {}
    }
  }
}
```

**FileContext** (sent with every prompt):
```lua
{
  cwd = "/project/path",
  open_buffers = {"/path/file1.lua", "/path/file2.lua"},
  cursor_file = "/path/file1.lua",
  cursor_line = 42,
  cursor_column = 10,
  selected_text = "..." | nil  -- visual selection if active
}
```

**RPC State** (internal):
```lua
{
  proc = vim.SystemObj,  -- active pi process handle
  session_file = ".pi/sessions/<name>.jsonl",
  is_streaming = boolean,
  pending_steering = {},
  pending_followup = {}
}
```

### Interfaces

**pi RPC Protocol (JSONL over stdin/stdout):**

Commands sent to pi:
```json
{"type": "prompt", "message": "Hello", "id": "req-1"}
{"type": "steer", "message": "Stop and refactor"}
{"type": "abort"}
{"type": "get_state"}
{"type": "bash", "command": "npm test"}
```

Key events received from pi:
```json
{"type": "agent_start"}
{"type": "message_update", "message": {...}, "assistantMessageEvent": {"type": "text_delta", "delta": "Hello"}}
{"type": "tool_execution_start", "toolCallId": "call_123", "toolName": "bash", "args": {"command": "ls"}}
{"type": "tool_execution_update", "toolCallId": "call_123", "partialResult": {"content": [...]}}
{"type": "agent_end", "messages": [...]}
```

**Neovim Commands:**
- `:PiChat [message?]` — Open/focus chat panel, optionally send initial message
- `:PiEpic [title?]` — Create new epic from current buffer or prompt for title
- `:PiPlan [epic-id?]` — Open plan viewer panel (current epic or specific)
- `:PiFileAdd [path?]` — Add file to context (current buffer or specified path)
- `:PiBash [command]` — Execute bash via pi context
- `:PiAbort` — Abort current streaming operation
- `:PiStatus` — Show session stats (tokens, cost, context usage)

**Lua API (for advanced users):**
```lua
require("pi-traycer").setup({
  -- Panel layouts
  chat = { position = "right", width = 0.4 },
  plan = { position = "bottom", height = 0.3 },
  
  -- Keymaps (set to false to disable)
  keymaps = {
    chat = "<leader>pc",
    epic = "<leader>pe",
    plan = "<leader>pp",
    send_selection = "<leader>ps",
    abort = "<leader>pa",
  },
  
  -- pi options
  pi = {
    model = "fireworks/llama-v3p1-405b-instruct",
    thinking = "medium",
  }
})

-- Programmatic access
local traycer = require("pi-traycer")
traycer.chat.send("Hello pi")           -- Send message
traycer.plan.create_epic("My Feature")  -- Create epic
traycer.rpc.get_state()                 -- Get pi state
```

**Default Keymaps (configurable):**
- `<leader>pc` — Toggle chat panel
- `<leader>pe` — Create/focus epic panel
- `<leader>pp` — Toggle plan panel
- `<leader>ps` — Send visual selection to chat
- `<leader>pa` — Abort current operation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Neovim UI                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │
│  │   Chat Panel    │  │   Plan Panel    │  │ Status Line  │  │
│  │  (snacks.nvim)  │  │  (edgy.nvim)    │  │  (snacks)    │  │
│  │                 │  │                 │  │              │  │
│  │  User input     │  │  Epic list      │  │ Token count  │  │
│  │  AI responses   │  │  Task tree       │  │ Cost         │  │
│  │  Tool results   │  │  Checkboxes      │  │ Status       │  │
│  └────────┬────────┘  └────────┬────────┘  └──────────────┘  │
│           │                    │                              │
│           └────────────────────┘                              │
│                     │                                         │
│                     ▼                                         │
│           ┌─────────────────┐                                 │
│           │  lua/pi-traycer/│                                 │
│           │                 │                                 │
│           │  chat.lua ──────┼──► UI updates                   │
│           │  plan.lua ──────┼──► Epic/task state             │
│           │  context.lua ───┼──► File/buffer gathering        │
│           │  rpc.lua ───────┼──► Process management          │
│           └────────┬────────┘                                 │
│                    │                                          │
│                    ▼                                          │
│           ┌─────────────────┐                                 │
│           │  pi --mode rpc  │  ◄── stdin/stdout JSONL        │
│           │                 │  ◄── FIREWORKS_API_KEY env       │
│           │  Session:       │                                 │
│           │  .pi/sessions/  │                                 │
│           │  <project>.jsonl│                                 │
│           └─────────────────┘                                 │
└─────────────────────────────────────────────────────────────┘
```

**Data Flow:**

1. **User Input**: Typed in chat buffer or via `:PiChat` → captured by `chat.lua`
2. **Context Gathering**: `context.lua` collects cwd, open buffers, cursor position, visual selection
3. **RPC Command**: `rpc.lua` formats JSON and writes to pi stdin: `{"type":"prompt","message":"..."}`
4. **Streaming Response**: pi writes events to stdout → `rpc.lua` parses JSONL, dispatches to handlers
5. **UI Updates**: `chat.lua` receives `message_update` events, appends text deltas to buffer
6. **Tool Execution**: `tool_execution_*` events show progress in status/snacks notifications
7. **Plan Detection**: On `agent_end`, `plan.lua` parses response for plan markers ("## Plan", numbered tasks)
8. **Epic Persistence**: Plans saved to `.pi/plans/<epic-id>.json`

**Extension UI Protocol:** When pi extensions request user input (select, confirm, input, editor), the plugin intercepts `extension_ui_request` events and renders snacks.nvim pickers/input dialogs, then sends `extension_ui_response` back to pi.

## Project Structure

```
pi-traycer.nvim/
├── lua/pi-traycer/
│   ├── init.lua              -- Main entry, setup(opts), health check
│   ├── config.lua            -- Default configuration, user opts merging
│   ├── rpc.lua               -- pi process spawn, JSONL protocol, event dispatch
│   ├── chat.lua              -- Chat panel UI (snacks), message history, input handling
│   ├── plan.lua              -- Epic/Plan panel (edgy), task tree, status updates
│   ├── context.lua           -- Gather FileContext (buffers, cwd, cursor, selection)
│   ├── commands.lua          -- :PiChat, :PiEpic, :PiPlan, :PiBash implementations
│   ├── keymaps.lua           -- Default keymap setup (configurable)
│   └── utils.lua             -- JSON helpers, message formatting, plan parsing
├── plugin/
│   └── pi-traycer.lua        -- Auto-load: check pi executable, warn if missing
├── tests/
│   ├── minimal_init.lua      -- Test bootstrap (plenary.nvim harness)
│   ├── rpc_spec.lua          -- RPC protocol tests (JSONL parsing, event handling)
│   ├── chat_spec.lua         -- Chat panel tests (message formatting, history)
│   └── plan_spec.lua         -- Plan parsing tests (marker detection, task extraction)
├── README.md                 -- Installation, configuration, keymaps, examples
└── .gitignore                -- Ignore .pi/ directories in development
```

## Testing Strategy

**Prerequisites:** `FIREWORKS_API_KEY` environment variable is set, `pi` CLI is installed and in `$PATH`.

**Unit Tests (plenary.nvim):**
```bash
# Run all tests
nvim --headless -c "PlenaryBustedDirectory tests/ { minimal_init = 'tests/minimal_init.lua' }"
```

**Test Files:**
- `tests/rpc_spec.lua` — JSONL framing, event parsing, command formatting
- `tests/chat_spec.lua` — Message history management, buffer updates
- `tests/plan_spec.lua` — Plan marker detection, task tree building

**Manual E2E Acceptance Test:**

```bash
# 1. Verify pi standalone works
cd /tmp/pi-test
pi --mode json "List files" 2>/dev/null | head -5

# 2. Open test project in Neovim with plugin loaded
nvim .

# 3. Execute test sequence:
:PiChat                    -- Chat panel appears (snacks floating window)
:PiChat Hello pi           -- Message sent, streaming response within 10s
<leader>pe                 -- Epic panel appears (edgy sidebar)
:PiPlan                    -- Plan panel shows (empty or current epic)
<leader>ps                 -- With visual selection: sends to chat
:PiAbort                   -- Cancels any streaming operation
:PiStatus                  -- Shows tokens, cost, context usage in notification
```

**Assertions for "Done":**
- Chat panel opens/closes without errors
- Streaming responses display incrementally (text_delta events)
- Tool execution shows progress (bash commands visible)
- Epic panel renders task list with checkboxes
- Plan JSON persists to `.pi/plans/` and reloads correctly
- Abort command stops streaming immediately
- Status shows accurate token/cost info from pi

## Important Notes

**Environment Variables:**
- `FIREWORKS_API_KEY` — Required, already defined in environment
- `PI_TRAYCER_DEBUG` — Optional, enables verbose RPC logging to `:messages`
- `PI_TRAYCER_SESSION_DIR` — Optional override for session storage path

**Critical File Paths:**
- `.pi/sessions/<project-name>.jsonl` — pi session persistence (tree structure for branching)
- `.pi/plans/<epic-id>.json` — Epic plans with tasks, dependencies, status
- `~/.pi/agent/` — Global pi config directory (extensions, skills, themes)

**Known Gotchas:**

1. **RPC Framing (Critical)**: pi uses strict LF (`\n`) delimited JSONL. Do NOT use generic line readers that split on Unicode line separators (`U+2028`, `U+2029`). Split on `\n` only, strip optional trailing `\r`.

2. **Streaming State**: Must handle the full lifecycle: `agent_start` → multiple `message_update` (text_delta, thinking_delta, toolcall_delta) → `message_end` → `agent_end`. Missing events cause UI desync.

3. **Tool Execution Updates**: `tool_execution_update` events contain `partialResult` (accumulated output so far), not deltas. Replace display, don't append.

4. **Extension UI Protocol**: When pi extensions request user input via `extension_ui_request`, the plugin must render appropriate snacks.nvim UI (picker for `select`, input for `input`, confirm dialog for `confirm`) and send `extension_ui_response` with matching `id`.

5. **Session Isolation**: Each Neovim instance spawns its own pi RPC process with unique session file. No shared state between instances.

6. **pi Availability Check**: Plugin must verify `vim.fn.executable("pi") == 1` on setup. If missing, show error notification and disable commands.

7. **Fireworks Model**: Default to `fireworks/llama-v3p1-405b-instruct` or similar. Model must support tool use for bash/read/edit operations.

**Performance Considerations:**
- Use `vim.system()` (Neovim 0.10+) for async process management
- Buffer text updates, flush on `message_end` or throttle for high-frequency deltas
- Large file context: truncate or use `@file` references instead of full content
