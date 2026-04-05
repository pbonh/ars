# pi-traycer.nvim Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone Neovim plugin that provides Traycer-like spec-driven development using pi's RPC mode, with structured chat, epic/plan management, and task tracking.

**Architecture:** Event-driven hub — `rpc.lua` spawns pi and dispatches JSONL events to subscriber modules (chat, plan, extension_ui). Snacks.nvim handles all UI (windows, pickers, notifications). Edgy.nvim docks the plan panel. A pi extension (`create_plan` tool) provides structured plan output instead of parsing markdown.

**Tech Stack:** Lua (Neovim 0.10+), snacks.nvim, edgy.nvim, plenary.nvim, pi coding agent (RPC mode), TypeScript (pi extension)

**Spec:** `docs/superpowers/specs/2026-04-05-pi-traycer-nvim-design.md`

**Repo:** `pbonh/pi-traycer.nvim` (standalone — create new repo at `~/Code/github.com/pbonh/pi-traycer.nvim/`)

---

## File Structure

```
pi-traycer.nvim/
├── lua/pi-traycer/
│   ├── init.lua              -- setup(opts), health check, API exports
│   ├── config.lua            -- default options, deep merge with user opts
│   ├── rpc.lua               -- pi process spawn, JSONL stdin/stdout, event hub
│   ├── state.lua             -- shared state (session info, active epic, token stats)
│   ├── context.lua           -- gather FileContext (buffers, cursor, selection, git)
│   ├── chat.lua              -- chat panel (snacks split: history + input buffers)
│   ├── plan.lua              -- plan panel (edgy dock), epic CRUD, task tree, persistence
│   ├── extension_ui.lua      -- extension_ui_request → snacks picker/input/confirm
│   ├── commands.lua          -- :Pi* command registration
│   └── keymaps.lua           -- global + buffer-local keymap setup
├── plugin/
│   └── pi-traycer.lua        -- auto-load guard, pi executable check
├── extensions/
│   └── create-plan.ts        -- pi extension: create_plan tool (TypeScript)
├── tests/
│   ├── minimal_init.lua      -- plenary test bootstrap
│   ├── config_spec.lua       -- config defaults and merging
│   ├── rpc_spec.lua          -- JSONL parsing, event dispatch, command serialization
│   ├── state_spec.lua        -- state get/set/reset
│   ├── context_spec.lua      -- FileContext gathering
│   ├── chat_spec.lua         -- message formatting, buffer operations
│   ├── plan_spec.lua         -- epic CRUD, task tree, JSON persistence
│   └── extension_ui_spec.lua -- request routing, response formatting
└── README.md
```

---

### Task 1: Project Scaffolding & Test Harness

**Files:**
- Create: `lua/pi-traycer/config.lua`
- Create: `lua/pi-traycer/init.lua`
- Create: `tests/minimal_init.lua`
- Create: `tests/config_spec.lua`
- Create: `.gitignore`

- [ ] **Step 1: Create repo and directory structure**

```bash
cd ~/Code/github.com/pbonh
mkdir -p pi-traycer.nvim/{lua/pi-traycer,plugin,extensions,tests}
cd pi-traycer.nvim
git init
```

- [ ] **Step 2: Create .gitignore**

Create `.gitignore`:

```gitignore
.pi/
*.swp
*.swo
*~
.superpowers/
```

- [ ] **Step 3: Create test harness**

Create `tests/minimal_init.lua`:

```lua
local lazypath = vim.fn.stdpath("data") .. "/lazy"
vim.opt.rtp:prepend(lazypath .. "/plenary.nvim")
vim.opt.rtp:prepend(lazypath .. "/snacks.nvim")
vim.opt.rtp:prepend(lazypath .. "/edgy.nvim")
vim.opt.rtp:prepend(".")
vim.cmd("runtime plugin/plenary.vim")
```

- [ ] **Step 4: Write config test**

Create `tests/config_spec.lua`:

```lua
describe("config", function()
  local config = require("pi-traycer.config")

  before_each(function()
    package.loaded["pi-traycer.config"] = nil
    config = require("pi-traycer.config")
  end)

  it("has default values", function()
    config.setup({})
    local opts = config.get()
    assert.are.equal("right", opts.chat.position)
    assert.are.equal(0.4, opts.chat.size)
    assert.are.equal("bottom", opts.plan.position)
    assert.are.equal(0.3, opts.plan.size)
    assert.are.equal("<leader>pc", opts.keymaps.chat)
    assert.is_true(opts.notifications.cost_on_completion)
    assert.are.equal(80, opts.notifications.context_warning_pct)
  end)

  it("merges user opts over defaults", function()
    config.setup({ chat = { size = 0.5 }, pi = { model = "test-model" } })
    local opts = config.get()
    assert.are.equal(0.5, opts.chat.size)
    assert.are.equal("right", opts.chat.position)
    assert.are.equal("test-model", opts.pi.model)
  end)

  it("allows disabling keymaps with false", function()
    config.setup({ keymaps = { chat = false } })
    local opts = config.get()
    assert.is_false(opts.keymaps.chat)
    assert.are.equal("<leader>pe", opts.keymaps.epic)
  end)
end)
```

- [ ] **Step 5: Run test to verify it fails**

```bash
nvim --headless -c "PlenaryBustedFile tests/config_spec.lua" 2>&1
```

Expected: FAIL — module `pi-traycer.config` not found.

- [ ] **Step 6: Implement config.lua**

Create `lua/pi-traycer/config.lua`:

```lua
local M = {}

M.defaults = {
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
}

M._options = {}

function M.setup(opts)
  M._options = vim.tbl_deep_extend("force", {}, M.defaults, opts or {})
end

function M.get()
  return M._options
end

return M
```

- [ ] **Step 7: Create init.lua skeleton**

Create `lua/pi-traycer/init.lua`:

```lua
local M = {}

function M.setup(opts)
  require("pi-traycer.config").setup(opts)
end

return M
```

- [ ] **Step 8: Run test to verify it passes**

```bash
nvim --headless -c "PlenaryBustedFile tests/config_spec.lua" 2>&1
```

Expected: All 3 tests PASS.

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "feat: project scaffolding with config module and test harness"
```

---

### Task 2: RPC JSONL Parser

**Files:**
- Create: `lua/pi-traycer/rpc.lua`
- Create: `tests/rpc_spec.lua`

- [ ] **Step 1: Write JSONL parsing tests**

Create `tests/rpc_spec.lua`:

```lua
describe("rpc", function()
  local rpc

  before_each(function()
    package.loaded["pi-traycer.rpc"] = nil
    rpc = require("pi-traycer.rpc")
  end)

  describe("parse_line", function()
    it("parses valid JSON", function()
      local result = rpc._parse_line('{"type":"agent_start"}')
      assert.are.same({ type = "agent_start" }, result)
    end)

    it("returns nil for empty string", function()
      assert.is_nil(rpc._parse_line(""))
    end)

    it("strips trailing carriage return", function()
      local result = rpc._parse_line('{"type":"agent_end"}\r')
      assert.are.same({ type = "agent_end" }, result)
    end)

    it("returns nil for invalid JSON", function()
      local result = rpc._parse_line("not json")
      assert.is_nil(result)
    end)

    it("parses nested objects", function()
      local line = '{"type":"message_update","assistantMessageEvent":{"type":"text_delta","delta":"hi"}}'
      local result = rpc._parse_line(line)
      assert.are.equal("message_update", result.type)
      assert.are.equal("text_delta", result.assistantMessageEvent.type)
      assert.are.equal("hi", result.assistantMessageEvent.delta)
    end)
  end)

  describe("process_stdout", function()
    it("handles complete single line", function()
      local events = {}
      rpc.on("agent_start", function(e) table.insert(events, e) end)
      rpc._process_stdout('{"type":"agent_start"}\n')
      assert.are.equal(1, #events)
      assert.are.equal("agent_start", events[1].type)
    end)

    it("handles multiple lines in one chunk", function()
      local events = {}
      rpc.on("*", function(e) table.insert(events, e) end)
      rpc._process_stdout('{"type":"agent_start"}\n{"type":"agent_end"}\n')
      assert.are.equal(2, #events)
    end)

    it("buffers partial lines across chunks", function()
      local events = {}
      rpc.on("agent_start", function(e) table.insert(events, e) end)
      rpc._process_stdout('{"type":')
      assert.are.equal(0, #events)
      rpc._process_stdout('"agent_start"}\n')
      assert.are.equal(1, #events)
    end)

    it("does not split on Unicode line separators", function()
      local events = {}
      rpc.on("*", function(e) table.insert(events, e) end)
      -- U+2028 is \xe2\x80\xa8 in UTF-8
      rpc._process_stdout('{"type":"msg","text":"line\xe2\x80\xa8sep"}\n')
      assert.are.equal(1, #events)
      assert.are.equal("line\xe2\x80\xa8sep", events[1].text)
    end)

    it("handles empty lines gracefully", function()
      local events = {}
      rpc.on("*", function(e) table.insert(events, e) end)
      rpc._process_stdout('\n\n{"type":"agent_start"}\n\n')
      assert.are.equal(1, #events)
    end)
  end)
end)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
nvim --headless -c "PlenaryBustedFile tests/rpc_spec.lua" 2>&1
```

Expected: FAIL — module `pi-traycer.rpc` not found.

- [ ] **Step 3: Implement JSONL parser and event hub skeleton**

Create `lua/pi-traycer/rpc.lua`:

```lua
local M = {}

M._handlers = {}
M._state = {
  proc = nil,
  stdout_buf = "",
  session_file = nil,
  is_streaming = false,
  restart_count = 0,
}

function M.on(event_type, handler)
  if not M._handlers[event_type] then
    M._handlers[event_type] = {}
  end
  table.insert(M._handlers[event_type], handler)
end

function M.off(event_type, handler)
  local handlers = M._handlers[event_type]
  if not handlers then return end
  for i, h in ipairs(handlers) do
    if h == handler then
      table.remove(handlers, i)
      return
    end
  end
end

function M._dispatch(event)
  local handlers = M._handlers[event.type] or {}
  for _, handler in ipairs(handlers) do
    handler(event)
  end
  local wildcard = M._handlers["*"] or {}
  for _, handler in ipairs(wildcard) do
    handler(event)
  end
end

function M._parse_line(line)
  if line == "" then return nil end
  if line:sub(-1) == "\r" then
    line = line:sub(1, -2)
  end
  if line == "" then return nil end
  local ok, data = pcall(vim.json.decode, line)
  if not ok then
    vim.notify("[pi-traycer] JSON parse error: " .. tostring(data), vim.log.levels.WARN)
    return nil
  end
  return data
end

function M._process_stdout(data)
  M._state.stdout_buf = M._state.stdout_buf .. data
  while true do
    local newline_pos = M._state.stdout_buf:find("\n")
    if not newline_pos then break end
    local line = M._state.stdout_buf:sub(1, newline_pos - 1)
    M._state.stdout_buf = M._state.stdout_buf:sub(newline_pos + 1)
    local event = M._parse_line(line)
    if event then
      M._dispatch(event)
    end
  end
end

function M._reset()
  M._handlers = {}
  M._state = {
    proc = nil,
    stdout_buf = "",
    session_file = nil,
    is_streaming = false,
    restart_count = 0,
  }
end

return M
```

- [ ] **Step 4: Run test to verify it passes**

```bash
nvim --headless -c "PlenaryBustedFile tests/rpc_spec.lua" 2>&1
```

Expected: All 10 tests PASS.

Note: The `process_stdout` tests call `_dispatch` synchronously (no `vim.schedule`) because in the test harness we're already on the main thread. In production, the stdout callback from `vim.system()` will use `vim.schedule()` to marshal back to the main thread — see Task 4.

- [ ] **Step 5: Commit**

```bash
git add lua/pi-traycer/rpc.lua tests/rpc_spec.lua
git commit -m "feat: RPC JSONL parser with strict LF framing and event dispatch"
```

---

### Task 3: RPC Event Hub & Command Serialization

**Files:**
- Modify: `tests/rpc_spec.lua`
- Modify: `lua/pi-traycer/rpc.lua`

- [ ] **Step 1: Write event hub and command tests**

Append to `tests/rpc_spec.lua`:

```lua
  describe("event hub", function()
    it("dispatches to specific handler", function()
      local received = nil
      rpc.on("agent_start", function(e) received = e end)
      rpc._dispatch({ type = "agent_start" })
      assert.are.equal("agent_start", received.type)
    end)

    it("dispatches to wildcard handler", function()
      local received = {}
      rpc.on("*", function(e) table.insert(received, e) end)
      rpc._dispatch({ type = "agent_start" })
      rpc._dispatch({ type = "agent_end" })
      assert.are.equal(2, #received)
    end)

    it("supports multiple handlers per event", function()
      local count = 0
      rpc.on("agent_start", function() count = count + 1 end)
      rpc.on("agent_start", function() count = count + 1 end)
      rpc._dispatch({ type = "agent_start" })
      assert.are.equal(2, count)
    end)

    it("removes handler with off()", function()
      local count = 0
      local handler = function() count = count + 1 end
      rpc.on("agent_start", handler)
      rpc._dispatch({ type = "agent_start" })
      assert.are.equal(1, count)
      rpc.off("agent_start", handler)
      rpc._dispatch({ type = "agent_start" })
      assert.are.equal(1, count)
    end)
  end)

  describe("send_command", function()
    it("serializes prompt command", function()
      local written = nil
      rpc._state.proc = {
        write = function(_, data) written = data end,
      }
      rpc.send_command({ type = "prompt", message = "hello" })
      local decoded = vim.json.decode(written:sub(1, -2))
      assert.are.equal("prompt", decoded.type)
      assert.are.equal("hello", decoded.message)
      assert.are.equal("\n", written:sub(-1))
    end)

    it("serializes abort command", function()
      local written = nil
      rpc._state.proc = {
        write = function(_, data) written = data end,
      }
      rpc.send_command({ type = "abort" })
      local decoded = vim.json.decode(written:sub(1, -2))
      assert.are.equal("abort", decoded.type)
    end)

    it("returns false when no process", function()
      rpc._state.proc = nil
      local ok = rpc.send_command({ type = "prompt", message = "hi" })
      assert.is_false(ok)
    end)
  end)
```

- [ ] **Step 2: Run test to verify new tests fail or pass**

```bash
nvim --headless -c "PlenaryBustedFile tests/rpc_spec.lua" 2>&1
```

Expected: Event hub tests PASS (already implemented). send_command tests may FAIL if `send_command` isn't implemented yet.

- [ ] **Step 3: Implement send_command**

Add to `lua/pi-traycer/rpc.lua` before the `_reset` function:

```lua
function M.send_command(cmd)
  if not M._state.proc then
    vim.notify("[pi-traycer] No active pi process", vim.log.levels.ERROR)
    return false
  end
  local json = vim.json.encode(cmd) .. "\n"
  M._state.proc:write(json)
  return true
end

function M.is_connected()
  return M._state.proc ~= nil
end

function M.is_streaming()
  return M._state.is_streaming
end
```

- [ ] **Step 4: Run tests to verify all pass**

```bash
nvim --headless -c "PlenaryBustedFile tests/rpc_spec.lua" 2>&1
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add lua/pi-traycer/rpc.lua tests/rpc_spec.lua
git commit -m "feat: RPC event hub with on/off/dispatch and command serialization"
```

---

### Task 4: RPC Process Management

**Files:**
- Modify: `lua/pi-traycer/rpc.lua`

- [ ] **Step 1: Implement start_session and stop**

Add to `lua/pi-traycer/rpc.lua` before `send_command`:

```lua
local MAX_RESTARTS = 3

function M.start_session(session_name, opts)
  opts = opts or {}
  local config = require("pi-traycer.config").get()

  local session_dir = config.pi.session_dir or ".pi/sessions"
  vim.fn.mkdir(session_dir, "p")
  local session_file = session_dir .. "/" .. session_name .. ".jsonl"

  local cmd = { "pi", "--mode", "rpc", "--session", session_file }
  if config.pi.model then
    table.insert(cmd, "--model")
    table.insert(cmd, config.pi.model)
  end
  if config.pi.thinking then
    table.insert(cmd, "--thinking")
    table.insert(cmd, config.pi.thinking)
  end

  M._state.stdout_buf = ""
  M._state.session_file = session_file

  M._state.proc = vim.system(cmd, {
    stdin = true,
    stdout = function(_, data)
      if data then
        vim.schedule(function()
          M._process_stdout(data)
        end)
      end
    end,
    stderr = function(_, data)
      if data and data ~= "" then
        vim.schedule(function()
          vim.notify("[pi-traycer] stderr: " .. vim.trim(data), vim.log.levels.DEBUG)
        end)
      end
    end,
  }, function(result)
    vim.schedule(function()
      M._state.proc = nil
      M._state.is_streaming = false
      M._dispatch({ type = "process_exit", code = result.code })

      if result.code ~= 0 and M._state.restart_count < MAX_RESTARTS then
        M._state.restart_count = M._state.restart_count + 1
        vim.notify(
          "[pi-traycer] pi crashed (exit " .. result.code .. "), restarting ("
            .. M._state.restart_count .. "/" .. MAX_RESTARTS .. ")",
          vim.log.levels.WARN
        )
        M.start_session(session_name, opts)
      elseif result.code ~= 0 then
        vim.notify("[pi-traycer] pi crashed and max restarts reached", vim.log.levels.ERROR)
      end
    end)
  end)

  return M._state.proc, session_file
end

function M.stop()
  if M._state.proc then
    M._state.proc:kill(15)
    M._state.proc = nil
    M._state.is_streaming = false
  end
end
```

- [ ] **Step 2: Wire up streaming state tracking**

Add event handlers in rpc.lua — add an `_init_internal_handlers` function after `_reset`:

```lua
function M._init_internal_handlers()
  M.on("agent_start", function()
    M._state.is_streaming = true
  end)
  M.on("agent_end", function()
    M._state.is_streaming = false
    M._state.restart_count = 0
  end)
end
```

- [ ] **Step 3: Manual verification**

Open Neovim in a test project with pi installed:

```vim
:lua require("pi-traycer").setup({})
:lua local rpc = require("pi-traycer.rpc"); rpc._init_internal_handlers(); rpc.on("*", function(e) print(vim.inspect(e)) end); rpc.start_session("test")
:lua require("pi-traycer.rpc").send_command({ type = "get_state" })
:lua require("pi-traycer.rpc").stop()
```

Expected: Events printed to `:messages`. Process starts and stops cleanly.

- [ ] **Step 4: Commit**

```bash
git add lua/pi-traycer/rpc.lua
git commit -m "feat: RPC process management with auto-restart on crash"
```

---

### Task 5: State Module

**Files:**
- Create: `lua/pi-traycer/state.lua`
- Create: `tests/state_spec.lua`

- [ ] **Step 1: Write state tests**

Create `tests/state_spec.lua`:

```lua
describe("state", function()
  local state

  before_each(function()
    package.loaded["pi-traycer.state"] = nil
    state = require("pi-traycer.state")
  end)

  it("starts with empty state", function()
    assert.is_nil(state.get("session_file"))
    assert.is_nil(state.get("active_epic_id"))
    assert.are.same({}, state.get("token_stats"))
  end)

  it("sets and gets values", function()
    state.set("session_file", ".pi/sessions/test.jsonl")
    assert.are.equal(".pi/sessions/test.jsonl", state.get("session_file"))
  end)

  it("updates token stats", function()
    state.update_token_stats({ input = 100, output = 50, cost = 0.01 })
    local stats = state.get("token_stats")
    assert.are.equal(100, stats.input)
    assert.are.equal(50, stats.output)
    assert.are.equal(0.01, stats.cost)
  end)

  it("resets to initial state", function()
    state.set("session_file", "test")
    state.reset()
    assert.is_nil(state.get("session_file"))
  end)
end)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
nvim --headless -c "PlenaryBustedFile tests/state_spec.lua" 2>&1
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement state.lua**

Create `lua/pi-traycer/state.lua`:

```lua
local M = {}

local _state = {}

local function initial_state()
  return {
    session_file = nil,
    active_epic_id = nil,
    token_stats = {},
    context_pct = 0,
  }
end

_state = initial_state()

function M.get(key)
  return _state[key]
end

function M.set(key, value)
  _state[key] = value
end

function M.update_token_stats(stats)
  _state.token_stats = vim.tbl_deep_extend("force", _state.token_stats, stats)
end

function M.reset()
  _state = initial_state()
end

return M
```

- [ ] **Step 4: Run test to verify it passes**

```bash
nvim --headless -c "PlenaryBustedFile tests/state_spec.lua" 2>&1
```

Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add lua/pi-traycer/state.lua tests/state_spec.lua
git commit -m "feat: shared state module for session, epic, and token tracking"
```

---

### Task 6: Context Gathering

**Files:**
- Create: `lua/pi-traycer/context.lua`
- Create: `tests/context_spec.lua`

- [ ] **Step 1: Write context tests**

Create `tests/context_spec.lua`:

```lua
describe("context", function()
  local context

  before_each(function()
    package.loaded["pi-traycer.context"] = nil
    context = require("pi-traycer.context")
  end)

  it("gathers cwd", function()
    local ctx = context.get_context()
    assert.are.equal(vim.fn.getcwd(), ctx.cwd)
  end)

  it("includes cursor file", function()
    local ctx = context.get_context()
    assert.is_string(ctx.cursor_file)
  end)

  it("includes cursor position", function()
    local ctx = context.get_context()
    assert.is_number(ctx.cursor_line)
    assert.is_number(ctx.cursor_col)
  end)

  it("lists open buffers", function()
    local ctx = context.get_context()
    assert.is_table(ctx.open_buffers)
  end)

  it("formats context for prompt", function()
    local ctx = context.get_context()
    local formatted = context.format_for_prompt(ctx)
    assert.is_string(formatted)
    assert.truthy(formatted:find("Working in"))
  end)
end)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
nvim --headless -c "PlenaryBustedFile tests/context_spec.lua" 2>&1
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement context.lua**

Create `lua/pi-traycer/context.lua`:

```lua
local M = {}

function M.get_context(opts)
  opts = opts or {}
  local buffers = {}
  for _, buf in ipairs(vim.api.nvim_list_bufs()) do
    if vim.api.nvim_buf_is_loaded(buf) and vim.bo[buf].buflisted then
      local name = vim.api.nvim_buf_get_name(buf)
      if name ~= "" then
        table.insert(buffers, name)
      end
    end
  end

  local cursor = vim.api.nvim_win_get_cursor(0)
  local selected_text = nil
  if opts.include_selection then
    local mode = vim.fn.mode()
    if mode == "v" or mode == "V" or mode == "\22" then
      vim.cmd('noautocmd normal! "vy')
      selected_text = vim.fn.getreg("v")
    end
  end

  local git_status = nil
  if opts.include_git then
    local result = vim.fn.systemlist("git status --porcelain 2>/dev/null")
    if vim.v.shell_error == 0 then
      local branch = vim.fn.systemlist("git branch --show-current 2>/dev/null")
      git_status = {
        branch = branch[1] or "HEAD",
        changed_files = result,
      }
    end
  end

  return {
    cwd = vim.fn.getcwd(),
    open_buffers = buffers,
    cursor_file = vim.api.nvim_buf_get_name(0),
    cursor_line = cursor[1],
    cursor_col = cursor[2],
    selected_text = selected_text,
    git_status = git_status,
  }
end

function M.format_for_prompt(ctx)
  local parts = { "Working in " .. ctx.cwd }

  if #ctx.open_buffers > 0 then
    local names = {}
    for _, buf in ipairs(ctx.open_buffers) do
      table.insert(names, vim.fn.fnamemodify(buf, ":."))
    end
    table.insert(parts, "Open files: " .. table.concat(names, ", "))
  end

  if ctx.cursor_file and ctx.cursor_file ~= "" then
    table.insert(parts, "Cursor at " .. vim.fn.fnamemodify(ctx.cursor_file, ":.") .. ":" .. ctx.cursor_line)
  end

  if ctx.selected_text then
    table.insert(parts, "Selection:\n```\n" .. ctx.selected_text .. "\n```")
  end

  if ctx.git_status then
    table.insert(parts, "Git branch: " .. ctx.git_status.branch)
    if #ctx.git_status.changed_files > 0 then
      table.insert(parts, "Changed files: " .. table.concat(ctx.git_status.changed_files, ", "))
    end
  end

  return table.concat(parts, "\n")
end

return M
```

- [ ] **Step 4: Run test to verify it passes**

```bash
nvim --headless -c "PlenaryBustedFile tests/context_spec.lua" 2>&1
```

Expected: All 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add lua/pi-traycer/context.lua tests/context_spec.lua
git commit -m "feat: context gathering for buffers, cursor, selection, and git state"
```

---

### Task 7: Chat Message Formatting

**Files:**
- Create: `lua/pi-traycer/chat.lua` (formatting functions only)
- Create: `tests/chat_spec.lua`

- [ ] **Step 1: Write message formatting tests**

Create `tests/chat_spec.lua`:

```lua
describe("chat", function()
  local chat

  before_each(function()
    package.loaded["pi-traycer.chat"] = nil
    chat = require("pi-traycer.chat")
  end)

  describe("format_user_message", function()
    it("formats user message with separator", function()
      local lines = chat.format_user_message("Hello pi")
      assert.truthy(vim.tbl_contains(lines, ">>> You"))
      local found = false
      for _, line in ipairs(lines) do
        if line == "Hello pi" then found = true end
      end
      assert.is_true(found)
    end)
  end)

  describe("format_assistant_header", function()
    it("returns assistant header lines", function()
      local lines = chat.format_assistant_header()
      assert.truthy(vim.tbl_contains(lines, "<<< Pi"))
    end)
  end)

  describe("format_tool_start", function()
    it("formats bash tool", function()
      local lines = chat.format_tool_start("bash", { command = "ls -la" })
      local joined = table.concat(lines, "\n")
      assert.truthy(joined:find("bash"))
      assert.truthy(joined:find("ls %-la"))
    end)

    it("formats read tool", function()
      local lines = chat.format_tool_start("read", { path = "src/main.lua" })
      local joined = table.concat(lines, "\n")
      assert.truthy(joined:find("read"))
      assert.truthy(joined:find("src/main.lua"))
    end)

    it("formats edit tool", function()
      local lines = chat.format_tool_start("edit", { path = "src/main.lua" })
      local joined = table.concat(lines, "\n")
      assert.truthy(joined:find("edit"))
    end)
  end)

  describe("format_tool_result", function()
    it("formats tool output", function()
      local lines = chat.format_tool_result("file1.lua\nfile2.lua")
      assert.is_true(#lines > 0)
    end)

    it("truncates long output", function()
      local long_output = string.rep("x", 2000)
      local lines = chat.format_tool_result(long_output)
      local total_len = 0
      for _, line in ipairs(lines) do
        total_len = total_len + #line
      end
      assert.is_true(total_len < 2000)
    end)
  end)
end)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
nvim --headless -c "PlenaryBustedFile tests/chat_spec.lua" 2>&1
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement chat formatting functions**

Create `lua/pi-traycer/chat.lua`:

```lua
local M = {}

local MAX_TOOL_OUTPUT_LINES = 20

M._history_buf = nil
M._input_buf = nil
M._history_win = nil
M._input_win = nil
M._split_win = nil
M._streaming_text = ""

function M.format_user_message(text)
  return { "", ">>> You", text, "" }
end

function M.format_assistant_header()
  return { "<<< Pi" }
end

function M.format_tool_start(tool_name, args)
  local detail = ""
  if tool_name == "bash" and args.command then
    detail = ": " .. args.command
  elseif tool_name == "read" and args.path then
    detail = ": " .. args.path
  elseif tool_name == "edit" and args.path then
    detail = ": " .. args.path
  elseif tool_name == "write" and args.path then
    detail = ": " .. args.path
  end
  return { "", "[" .. tool_name .. detail .. "]" }
end

function M.format_tool_result(output)
  if not output or output == "" then
    return { "[done]" }
  end
  local lines = vim.split(output, "\n")
  if #lines > MAX_TOOL_OUTPUT_LINES then
    local truncated = {}
    for i = 1, MAX_TOOL_OUTPUT_LINES do
      table.insert(truncated, "  " .. lines[i])
    end
    table.insert(truncated, "  ... (" .. (#lines - MAX_TOOL_OUTPUT_LINES) .. " more lines)")
    return truncated
  end
  local result = {}
  for _, line in ipairs(lines) do
    table.insert(result, "  " .. line)
  end
  return result
end

return M
```

- [ ] **Step 4: Run test to verify it passes**

```bash
nvim --headless -c "PlenaryBustedFile tests/chat_spec.lua" 2>&1
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add lua/pi-traycer/chat.lua tests/chat_spec.lua
git commit -m "feat: chat message formatting for user, assistant, and tool output"
```

---

### Task 8: Chat Panel UI

**Files:**
- Modify: `lua/pi-traycer/chat.lua`

- [ ] **Step 1: Implement chat panel toggle with snacks split**

Add to `lua/pi-traycer/chat.lua` after the formatting functions:

```lua
local function create_history_buf()
  local buf = vim.api.nvim_create_buf(false, true)
  vim.bo[buf].buftype = "nofile"
  vim.bo[buf].bufhidden = "hide"
  vim.bo[buf].swapfile = false
  vim.bo[buf].filetype = "pi-traycer-chat"
  vim.api.nvim_buf_set_name(buf, "pi-traycer://chat")
  vim.bo[buf].modifiable = false
  return buf
end

local function create_input_buf()
  local buf = vim.api.nvim_create_buf(false, true)
  vim.bo[buf].buftype = "nofile"
  vim.bo[buf].bufhidden = "hide"
  vim.bo[buf].swapfile = false
  vim.bo[buf].filetype = "pi-traycer-input"
  vim.api.nvim_buf_set_name(buf, "pi-traycer://input")
  return buf
end

local function append_to_history(lines)
  if not M._history_buf or not vim.api.nvim_buf_is_valid(M._history_buf) then return end
  vim.bo[M._history_buf].modifiable = true
  vim.api.nvim_buf_set_lines(M._history_buf, -1, -1, false, lines)
  vim.bo[M._history_buf].modifiable = false
  if M._history_win and vim.api.nvim_win_is_valid(M._history_win) then
    local line_count = vim.api.nvim_buf_line_count(M._history_buf)
    vim.api.nvim_win_set_cursor(M._history_win, { line_count, 0 })
  end
end

function M.is_open()
  return M._split_win ~= nil
    and vim.api.nvim_win_is_valid(M._split_win)
end

function M.toggle()
  if M.is_open() then
    M.close()
    return
  end
  M.open()
end

function M.open()
  if M.is_open() then
    vim.api.nvim_set_current_win(M._input_win)
    return
  end

  local config = require("pi-traycer.config").get()
  local position = config.chat.position
  local size = config.chat.size

  if not M._history_buf or not vim.api.nvim_buf_is_valid(M._history_buf) then
    M._history_buf = create_history_buf()
  end
  if not M._input_buf or not vim.api.nvim_buf_is_valid(M._input_buf) then
    M._input_buf = create_input_buf()
  end

  local split_cmd = position == "right" and "botright vsplit" or "botright split"
  vim.cmd(split_cmd)
  M._split_win = vim.api.nvim_get_current_win()

  if position == "right" then
    local width = math.floor(vim.o.columns * size)
    vim.api.nvim_win_set_width(M._split_win, width)
  else
    local height = math.floor(vim.o.lines * size)
    vim.api.nvim_win_set_height(M._split_win, height)
  end

  vim.api.nvim_win_set_buf(M._split_win, M._history_buf)
  M._history_win = M._split_win

  vim.cmd("belowright split")
  M._input_win = vim.api.nvim_get_current_win()
  vim.api.nvim_win_set_height(M._input_win, 3)
  vim.api.nvim_win_set_buf(M._input_win, M._input_buf)

  vim.keymap.set("n", "<CR>", function() M._send_from_input() end, { buffer = M._input_buf })
  vim.keymap.set("i", "<CR>", function()
    vim.cmd("stopinsert")
    M._send_from_input()
  end, { buffer = M._input_buf })
  vim.keymap.set("n", "q", function() M.close() end, { buffer = M._input_buf })
  vim.keymap.set("n", "q", function() M.close() end, { buffer = M._history_buf })

  vim.api.nvim_set_current_win(M._input_win)
  vim.cmd("startinsert")
end

function M.close()
  if M._split_win and vim.api.nvim_win_is_valid(M._split_win) then
    vim.api.nvim_win_close(M._split_win, true)
  end
  if M._input_win and vim.api.nvim_win_is_valid(M._input_win) then
    vim.api.nvim_win_close(M._input_win, true)
  end
  M._split_win = nil
  M._history_win = nil
  M._input_win = nil
end

function M._send_from_input()
  if not M._input_buf or not vim.api.nvim_buf_is_valid(M._input_buf) then return end
  local lines = vim.api.nvim_buf_get_lines(M._input_buf, 0, -1, false)
  local text = vim.trim(table.concat(lines, "\n"))
  if text == "" then return end
  vim.api.nvim_buf_set_lines(M._input_buf, 0, -1, false, { "" })
  M.send(text)
end

function M.send(text, opts)
  opts = opts or {}
  local rpc = require("pi-traycer.rpc")
  if not rpc.is_connected() then
    vim.notify("[pi-traycer] Not connected to pi. Start a session first.", vim.log.levels.WARN)
    return
  end
  append_to_history(M.format_user_message(text))
  local context = require("pi-traycer.context")
  local ctx = context.get_context({ include_selection = opts.include_selection })
  local message = text .. "\n\n---\n" .. context.format_for_prompt(ctx)
  rpc.send_command({ type = "prompt", message = message })
end

function M.clear()
  if M._history_buf and vim.api.nvim_buf_is_valid(M._history_buf) then
    vim.bo[M._history_buf].modifiable = true
    vim.api.nvim_buf_set_lines(M._history_buf, 0, -1, false, { "" })
    vim.bo[M._history_buf].modifiable = false
  end
  M._streaming_text = ""
end

M._append_to_history = append_to_history
```

- [ ] **Step 2: Manual verification**

```vim
:lua require("pi-traycer").setup({})
:lua require("pi-traycer.chat").toggle()
```

Expected: Right-side split appears with history buffer (top) and input buffer (bottom, 3 lines high). Cursor is in input buffer in insert mode. Pressing `q` in normal mode closes both.

- [ ] **Step 3: Commit**

```bash
git add lua/pi-traycer/chat.lua
git commit -m "feat: chat panel UI with history and input buffers"
```

---

### Task 9: Chat Streaming & Event Integration

**Files:**
- Modify: `lua/pi-traycer/chat.lua`

- [ ] **Step 1: Add event subscription setup function**

Add to `lua/pi-traycer/chat.lua`:

```lua
function M.subscribe(rpc)
  rpc.on("agent_start", function()
    M._streaming_text = ""
    M._append_to_history(M.format_assistant_header())
  end)

  rpc.on("message_update", function(event)
    local msg_event = event.assistantMessageEvent
    if not msg_event then return end

    if msg_event.type == "text_delta" then
      M._streaming_text = M._streaming_text .. msg_event.delta
      local lines = vim.split(M._streaming_text, "\n")
      if not M._history_buf or not vim.api.nvim_buf_is_valid(M._history_buf) then return end
      vim.bo[M._history_buf].modifiable = true
      local buf_lines = vim.api.nvim_buf_line_count(M._history_buf)
      local header_line = buf_lines
      for i = buf_lines, 1, -1 do
        local line = vim.api.nvim_buf_get_lines(M._history_buf, i - 1, i, false)[1]
        if line == "<<< Pi" then
          header_line = i
          break
        end
      end
      vim.api.nvim_buf_set_lines(M._history_buf, header_line, -1, false, lines)
      vim.bo[M._history_buf].modifiable = false
      if M._history_win and vim.api.nvim_win_is_valid(M._history_win) then
        local new_count = vim.api.nvim_buf_line_count(M._history_buf)
        vim.api.nvim_win_set_cursor(M._history_win, { new_count, 0 })
      end
    end
  end)

  rpc.on("tool_execution_start", function(event)
    M._append_to_history(M.format_tool_start(event.toolName or "tool", event.args or {}))
  end)

  rpc.on("tool_execution_update", function(event)
    if event.partialResult then
      local text = ""
      if type(event.partialResult) == "string" then
        text = event.partialResult
      elseif event.partialResult.content then
        for _, block in ipairs(event.partialResult.content) do
          if block.text then text = text .. block.text end
        end
      end
      if text ~= "" then
        local lines = M.format_tool_result(text)
        if not M._history_buf or not vim.api.nvim_buf_is_valid(M._history_buf) then return end
        vim.bo[M._history_buf].modifiable = true
        local buf_lines = vim.api.nvim_buf_line_count(M._history_buf)
        local tool_start = buf_lines
        for i = buf_lines, math.max(1, buf_lines - 30), -1 do
          local line = vim.api.nvim_buf_get_lines(M._history_buf, i - 1, i, false)[1]
          if line and line:match("^%[") then
            tool_start = i
            break
          end
        end
        vim.api.nvim_buf_set_lines(M._history_buf, tool_start, -1, false, lines)
        vim.bo[M._history_buf].modifiable = false
      end
    end
  end)

  rpc.on("tool_execution_end", function()
    M._append_to_history({ "" })
  end)

  rpc.on("agent_end", function(event)
    M._streaming_text = ""
    M._append_to_history({ "", "---", "" })
    local state = require("pi-traycer.state")
    if event.messages then
      for _, msg in ipairs(event.messages) do
        if msg.usage then
          state.update_token_stats({
            input = (state.get("token_stats").input or 0) + (msg.usage.inputTokens or 0),
            output = (state.get("token_stats").output or 0) + (msg.usage.outputTokens or 0),
            cache_read = (state.get("token_stats").cache_read or 0) + (msg.usage.cacheReadTokens or 0),
            cache_write = (state.get("token_stats").cache_write or 0) + (msg.usage.cacheWriteTokens or 0),
          })
        end
      end
    end
    local config = require("pi-traycer.config").get()
    if config.notifications.cost_on_completion then
      local stats = state.get("token_stats")
      if stats.input then
        vim.notify(
          string.format("[pi-traycer] Tokens: %d in / %d out", stats.input or 0, stats.output or 0),
          vim.log.levels.INFO
        )
      end
    end
  end)
end
```

- [ ] **Step 2: Manual verification — full chat flow**

```vim
:lua require("pi-traycer").setup({})
:lua local rpc = require("pi-traycer.rpc"); local chat = require("pi-traycer.chat"); rpc._init_internal_handlers(); chat.subscribe(rpc); rpc.start_session("test-chat")
:lua require("pi-traycer.chat").open()
```

Type a message in the input buffer. Press Enter. Expected: user message appears in history, then streaming pi response appears with text deltas.

- [ ] **Step 3: Commit**

```bash
git add lua/pi-traycer/chat.lua
git commit -m "feat: chat streaming with text delta accumulation and tool display"
```

---

### Task 10: Pi Extension — create_plan

**Files:**
- Create: `extensions/create-plan.ts`

- [ ] **Step 1: Write the pi extension**

Create `extensions/create-plan.ts`:

```typescript
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import { Type } from "@sinclair/typebox";

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "create_plan",
    label: "Create Plan",
    description:
      "Create or update an implementation plan with structured tasks and dependencies. " +
      "Use this tool when the user asks you to plan, break down, or create an epic for a piece of work. " +
      "Each task should have a unique id, clear title, optional description, and list of dependency task ids.",
    parameters: Type.Object({
      epic_title: Type.String({ description: "Title for the epic/plan" }),
      tasks: Type.Array(
        Type.Object({
          id: Type.String({ description: 'Unique task identifier, e.g. "task-1"' }),
          title: Type.String({ description: "Short task title" }),
          description: Type.Optional(Type.String({ description: "Detailed task description" })),
          dependencies: Type.Optional(
            Type.Array(Type.String(), { description: "IDs of tasks that must complete before this one" })
          ),
        })
      ),
    }),

    async execute(toolCallId, params, signal, onUpdate) {
      return {
        content: [
          {
            type: "text",
            text: `Plan created: "${params.epic_title}" with ${params.tasks.length} tasks.`,
          },
        ],
        details: params,
      };
    },
  });
}
```

- [ ] **Step 2: Verify extension loads with pi**

```bash
# Copy extension to pi's extensions directory
mkdir -p ~/.pi/agent/extensions
cp extensions/create-plan.ts ~/.pi/agent/extensions/

# Verify pi loads it (check for errors)
pi --mode json "List your available tools" 2>&1 | head -20
```

Expected: pi starts without extension errors. `create_plan` appears in tool list.

- [ ] **Step 3: Commit**

```bash
git add extensions/create-plan.ts
git commit -m "feat: pi extension providing create_plan tool for structured plan output"
```

---

### Task 11: Plan Data Model & Persistence

**Files:**
- Create: `lua/pi-traycer/plan.lua`
- Create: `tests/plan_spec.lua`

- [ ] **Step 1: Write plan persistence tests**

Create `tests/plan_spec.lua`:

```lua
describe("plan", function()
  local plan
  local test_dir

  before_each(function()
    package.loaded["pi-traycer.plan"] = nil
    plan = require("pi-traycer.plan")
    test_dir = vim.fn.tempname()
    vim.fn.mkdir(test_dir, "p")
  end)

  after_each(function()
    vim.fn.delete(test_dir, "rf")
  end)

  describe("create_epic", function()
    it("creates epic with id and title", function()
      local epic = plan.create_epic("Test Feature", test_dir)
      assert.is_string(epic.id)
      assert.are.equal("Test Feature", epic.title)
      assert.are.equal("draft", epic.status)
      assert.are.same({}, epic.tasks)
    end)

    it("persists epic to JSON file", function()
      local epic = plan.create_epic("Test Feature", test_dir)
      local path = test_dir .. "/" .. epic.id .. ".json"
      assert.are.equal(1, vim.fn.filereadable(path))
    end)
  end)

  describe("load_epic", function()
    it("loads persisted epic", function()
      local epic = plan.create_epic("Test Feature", test_dir)
      package.loaded["pi-traycer.plan"] = nil
      plan = require("pi-traycer.plan")
      local loaded = plan.load_epic(epic.id, test_dir)
      assert.are.equal("Test Feature", loaded.title)
      assert.are.equal(epic.id, loaded.id)
    end)

    it("returns nil for missing epic", function()
      local loaded = plan.load_epic("nonexistent", test_dir)
      assert.is_nil(loaded)
    end)
  end)

  describe("set_tasks", function()
    it("sets tasks from create_plan tool output", function()
      local epic = plan.create_epic("Auth System", test_dir)
      local tasks = {
        { id = "task-1", title = "DB schema", description = "Create tables" },
        { id = "task-2", title = "Login endpoint", dependencies = { "task-1" } },
      }
      plan.set_tasks(epic.id, tasks, test_dir)
      local loaded = plan.load_epic(epic.id, test_dir)
      assert.are.equal(2, #loaded.tasks)
      assert.are.equal("task-1", loaded.tasks[1].id)
      assert.are.equal("pending", loaded.tasks[1].status)
      assert.are.same({ "task-1" }, loaded.tasks[2].dependencies)
    end)
  end)

  describe("update_task_status", function()
    it("updates task status", function()
      local epic = plan.create_epic("Test", test_dir)
      plan.set_tasks(epic.id, {
        { id = "task-1", title = "First task" },
      }, test_dir)
      plan.update_task_status(epic.id, "task-1", "active", test_dir)
      local loaded = plan.load_epic(epic.id, test_dir)
      assert.are.equal("active", loaded.tasks[1].status)
    end)

    it("cycles status pending -> active -> done -> pending", function()
      local epic = plan.create_epic("Test", test_dir)
      plan.set_tasks(epic.id, {
        { id = "task-1", title = "First task" },
      }, test_dir)
      assert.are.equal("pending", plan.load_epic(epic.id, test_dir).tasks[1].status)
      plan.toggle_task_status(epic.id, "task-1", test_dir)
      assert.are.equal("active", plan.load_epic(epic.id, test_dir).tasks[1].status)
      plan.toggle_task_status(epic.id, "task-1", test_dir)
      assert.are.equal("done", plan.load_epic(epic.id, test_dir).tasks[1].status)
      plan.toggle_task_status(epic.id, "task-1", test_dir)
      assert.are.equal("pending", plan.load_epic(epic.id, test_dir).tasks[1].status)
    end)
  end)

  describe("list_epics", function()
    it("lists all epics in directory", function()
      plan.create_epic("Epic A", test_dir)
      plan.create_epic("Epic B", test_dir)
      local epics = plan.list_epics(test_dir)
      assert.are.equal(2, #epics)
    end)
  end)
end)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
nvim --headless -c "PlenaryBustedFile tests/plan_spec.lua" 2>&1
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement plan data model and persistence**

Create `lua/pi-traycer/plan.lua`:

```lua
local M = {}

M._plan_buf = nil
M._plan_win = nil
M._active_epic_id = nil

local STATUS_CYCLE = { pending = "active", active = "done", done = "pending" }

local function generate_id()
  local template = "xxxxxxxx"
  return string.gsub(template, "x", function()
    return string.format("%x", math.random(0, 15))
  end)
end

local function plans_dir(override)
  if override then return override end
  return ".pi/plans"
end

local function epic_path(epic_id, dir)
  return plans_dir(dir) .. "/" .. epic_id .. ".json"
end

function M.create_epic(title, dir)
  local d = plans_dir(dir)
  vim.fn.mkdir(d, "p")
  local epic = {
    id = generate_id(),
    title = title,
    description = "",
    status = "draft",
    created_at = os.time(),
    updated_at = os.time(),
    session_id = nil,
    tasks = {},
  }
  local path = epic_path(epic.id, dir)
  local json = vim.json.encode(epic)
  local f = io.open(path, "w")
  if f then
    f:write(json)
    f:close()
  end
  return epic
end

function M.load_epic(epic_id, dir)
  local path = epic_path(epic_id, dir)
  local f = io.open(path, "r")
  if not f then return nil end
  local content = f:read("*a")
  f:close()
  local ok, epic = pcall(vim.json.decode, content)
  if not ok then return nil end
  return epic
end

function M.save_epic(epic, dir)
  local path = epic_path(epic.id, dir)
  epic.updated_at = os.time()
  local json = vim.json.encode(epic)
  local f = io.open(path, "w")
  if f then
    f:write(json)
    f:close()
  end
end

function M.set_tasks(epic_id, tasks, dir)
  local epic = M.load_epic(epic_id, dir)
  if not epic then return end
  epic.tasks = {}
  for _, task in ipairs(tasks) do
    table.insert(epic.tasks, {
      id = task.id,
      title = task.title,
      description = task.description or "",
      status = "pending",
      dependencies = task.dependencies or {},
      files_changed = {},
    })
  end
  epic.status = "active"
  M.save_epic(epic, dir)
end

function M.update_task_status(epic_id, task_id, new_status, dir)
  local epic = M.load_epic(epic_id, dir)
  if not epic then return end
  for _, task in ipairs(epic.tasks) do
    if task.id == task_id then
      task.status = new_status
      break
    end
  end
  M.save_epic(epic, dir)
end

function M.toggle_task_status(epic_id, task_id, dir)
  local epic = M.load_epic(epic_id, dir)
  if not epic then return end
  for _, task in ipairs(epic.tasks) do
    if task.id == task_id then
      task.status = STATUS_CYCLE[task.status] or "pending"
      break
    end
  end
  M.save_epic(epic, dir)
end

function M.list_epics(dir)
  local d = plans_dir(dir)
  local files = vim.fn.glob(d .. "/*.json", false, true)
  local epics = {}
  for _, file in ipairs(files) do
    local f = io.open(file, "r")
    if f then
      local content = f:read("*a")
      f:close()
      local ok, epic = pcall(vim.json.decode, content)
      if ok then
        table.insert(epics, { id = epic.id, title = epic.title, status = epic.status })
      end
    end
  end
  return epics
end

return M
```

- [ ] **Step 4: Run test to verify it passes**

```bash
nvim --headless -c "PlenaryBustedFile tests/plan_spec.lua" 2>&1
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add lua/pi-traycer/plan.lua tests/plan_spec.lua
git commit -m "feat: plan data model with epic CRUD, task management, and JSON persistence"
```

---

### Task 12: Plan Panel UI & Event Wiring

**Files:**
- Modify: `lua/pi-traycer/plan.lua`

- [ ] **Step 1: Implement plan panel rendering**

Add to `lua/pi-traycer/plan.lua`:

```lua
local STATUS_ICONS = {
  pending = "○",
  active = "▶",
  done = "✓",
}

local function render_task_tree(buf, epic)
  if not buf or not vim.api.nvim_buf_is_valid(buf) then return end
  vim.bo[buf].modifiable = true
  local lines = {}
  table.insert(lines, "Epic: " .. epic.title)
  table.insert(lines, "Status: " .. epic.status)
  table.insert(lines, string.rep("─", 40))
  table.insert(lines, "")
  for _, task in ipairs(epic.tasks) do
    local icon = STATUS_ICONS[task.status] or "?"
    local deps = ""
    if task.dependencies and #task.dependencies > 0 then
      deps = " [after: " .. table.concat(task.dependencies, ", ") .. "]"
    end
    table.insert(lines, icon .. " " .. task.id .. ": " .. task.title .. deps)
  end
  if #epic.tasks == 0 then
    table.insert(lines, "(no tasks yet)")
  end
  vim.api.nvim_buf_set_lines(buf, 0, -1, false, lines)
  vim.bo[buf].modifiable = false
end

local function get_task_id_at_cursor()
  local line = vim.api.nvim_get_current_line()
  local id = line:match("^[○▶✓?] (task%-[%w%-]+):")
  return id
end

function M.is_open()
  return M._plan_win ~= nil and vim.api.nvim_win_is_valid(M._plan_win)
end

function M.toggle()
  if M.is_open() then
    M.close()
    return
  end
  M.open()
end

function M.open()
  if M.is_open() then
    vim.api.nvim_set_current_win(M._plan_win)
    return
  end

  local config = require("pi-traycer.config").get()

  if not M._plan_buf or not vim.api.nvim_buf_is_valid(M._plan_buf) then
    M._plan_buf = vim.api.nvim_create_buf(false, true)
    vim.bo[M._plan_buf].buftype = "nofile"
    vim.bo[M._plan_buf].bufhidden = "hide"
    vim.bo[M._plan_buf].swapfile = false
    vim.bo[M._plan_buf].filetype = "pi-traycer-plan"
    vim.api.nvim_buf_set_name(M._plan_buf, "pi-traycer://plan")
    vim.bo[M._plan_buf].modifiable = false
  end

  local split_cmd = config.plan.position == "bottom" and "botright split" or "botright vsplit"
  vim.cmd(split_cmd)
  M._plan_win = vim.api.nvim_get_current_win()

  if config.plan.position == "bottom" then
    local height = math.floor(vim.o.lines * config.plan.size)
    vim.api.nvim_win_set_height(M._plan_win, height)
  else
    local width = math.floor(vim.o.columns * config.plan.size)
    vim.api.nvim_win_set_width(M._plan_win, width)
  end

  vim.api.nvim_win_set_buf(M._plan_win, M._plan_buf)

  vim.keymap.set("n", "t", function()
    local task_id = get_task_id_at_cursor()
    if task_id and M._active_epic_id then
      M.toggle_task_status(M._active_epic_id, task_id)
      M.refresh()
    end
  end, { buffer = M._plan_buf })

  vim.keymap.set("n", "<CR>", function()
    local task_id = get_task_id_at_cursor()
    if task_id and M._active_epic_id then
      local epic = M.load_epic(M._active_epic_id)
      if epic then
        for _, task in ipairs(epic.tasks) do
          if task.id == task_id then
            vim.notify("[pi-traycer] Task: " .. task.title .. "\n" .. (task.description or ""), vim.log.levels.INFO)
            break
          end
        end
      end
    end
  end, { buffer = M._plan_buf })

  vim.keymap.set("n", "d", function()
    local task_id = get_task_id_at_cursor()
    if task_id and M._active_epic_id then
      local epic = M.load_epic(M._active_epic_id)
      if epic then
        for _, task in ipairs(epic.tasks) do
          if task.id == task_id then
            local detail = task.id .. ": " .. task.title .. "\n"
              .. "Status: " .. task.status .. "\n"
              .. "Description: " .. (task.description or "(none)") .. "\n"
              .. "Dependencies: " .. (#task.dependencies > 0 and table.concat(task.dependencies, ", ") or "(none)")
            vim.notify(detail, vim.log.levels.INFO)
            break
          end
        end
      end
    end
  end, { buffer = M._plan_buf })

  vim.keymap.set("n", "q", function() M.close() end, { buffer = M._plan_buf })

  M.refresh()
end

function M.close()
  if M._plan_win and vim.api.nvim_win_is_valid(M._plan_win) then
    vim.api.nvim_win_close(M._plan_win, true)
  end
  M._plan_win = nil
end

function M.refresh()
  if not M._active_epic_id then
    if M._plan_buf and vim.api.nvim_buf_is_valid(M._plan_buf) then
      vim.bo[M._plan_buf].modifiable = true
      vim.api.nvim_buf_set_lines(M._plan_buf, 0, -1, false, { "No active epic.", "", "Use :PiEpic <title> to create one." })
      vim.bo[M._plan_buf].modifiable = false
    end
    return
  end
  local epic = M.load_epic(M._active_epic_id)
  if epic then
    render_task_tree(M._plan_buf, epic)
  end
end

function M.set_active_epic(epic_id)
  M._active_epic_id = epic_id
  require("pi-traycer.state").set("active_epic_id", epic_id)
  M.refresh()
end

function M.get_active_epic_id()
  return M._active_epic_id
end
```

- [ ] **Step 2: Wire up event subscription for create_plan tool interception**

Add to `lua/pi-traycer/plan.lua`:

```lua
function M.subscribe(rpc)
  rpc.on("tool_execution_start", function(event)
    if event.toolName == "create_plan" and event.args then
      local args = event.args
      if not M._active_epic_id then
        local epic = M.create_epic(args.epic_title or "Untitled Epic")
        M.set_active_epic(epic.id)
      end
      if args.tasks then
        M.set_tasks(M._active_epic_id, args.tasks)
        M.refresh()
        vim.notify(
          "[pi-traycer] Plan created: " .. (args.epic_title or "") .. " (" .. #args.tasks .. " tasks)",
          vim.log.levels.INFO
        )
      end
    end
  end)
end
```

- [ ] **Step 3: Manual verification**

```vim
:lua require("pi-traycer").setup({})
:lua require("pi-traycer.plan").toggle()
```

Expected: Bottom panel opens showing "No active epic." message. Pressing `q` closes it.

- [ ] **Step 4: Commit**

```bash
git add lua/pi-traycer/plan.lua
git commit -m "feat: plan panel UI with task tree, status toggle, and create_plan event wiring"
```

---

### Task 13: Extension UI Handler

**Files:**
- Create: `lua/pi-traycer/extension_ui.lua`
- Create: `tests/extension_ui_spec.lua`

- [ ] **Step 1: Write extension UI tests**

Create `tests/extension_ui_spec.lua`:

```lua
describe("extension_ui", function()
  local ext_ui

  before_each(function()
    package.loaded["pi-traycer.extension_ui"] = nil
    ext_ui = require("pi-traycer.extension_ui")
  end)

  describe("format_response", function()
    it("formats select response", function()
      local resp = ext_ui.format_response("req-1", "option_a")
      assert.are.equal("extension_ui_response", resp.type)
      assert.are.equal("req-1", resp.id)
      assert.are.equal("option_a", resp.value)
      assert.is_nil(resp.cancelled)
    end)

    it("formats cancellation response", function()
      local resp = ext_ui.format_cancellation("req-1")
      assert.are.equal("extension_ui_response", resp.type)
      assert.are.equal("req-1", resp.id)
      assert.is_true(resp.cancelled)
    end)
  end)
end)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
nvim --headless -c "PlenaryBustedFile tests/extension_ui_spec.lua" 2>&1
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement extension UI handler**

Create `lua/pi-traycer/extension_ui.lua`:

```lua
local M = {}

local TIMEOUT_MS = 30000

function M.format_response(request_id, value)
  return {
    type = "extension_ui_response",
    id = request_id,
    value = value,
  }
end

function M.format_cancellation(request_id)
  return {
    type = "extension_ui_response",
    id = request_id,
    cancelled = true,
  }
end

local function handle_select(event, rpc)
  local Snacks = require("snacks")
  local items = {}
  for i, option in ipairs(event.options or {}) do
    table.insert(items, {
      idx = i,
      text = option.label or option.value or tostring(option),
      value = option.value or option,
    })
  end

  local responded = false
  local timer = vim.defer_fn(function()
    if not responded then
      responded = true
      rpc.send_command(M.format_cancellation(event.id))
    end
  end, TIMEOUT_MS)

  Snacks.picker({
    title = event.title or "Select",
    items = items,
    format = function(item) return { { item.text } } end,
    confirm = function(picker, item)
      picker:close()
      if not responded then
        responded = true
        if timer then timer:stop() end
        rpc.send_command(M.format_response(event.id, item.value))
      end
    end,
    on_close = function()
      if not responded then
        responded = true
        if timer then timer:stop() end
        rpc.send_command(M.format_cancellation(event.id))
      end
    end,
  })
end

local function handle_confirm(event, rpc)
  local Snacks = require("snacks")
  local responded = false

  Snacks.input({
    prompt = (event.message or "Confirm?") .. " (y/n): ",
  }, function(value)
    if not responded then
      responded = true
      local confirmed = value and (value:lower() == "y" or value:lower() == "yes")
      rpc.send_command(M.format_response(event.id, confirmed))
    end
  end)
end

local function handle_input(event, rpc)
  local Snacks = require("snacks")
  local responded = false

  local timer = vim.defer_fn(function()
    if not responded then
      responded = true
      rpc.send_command(M.format_cancellation(event.id))
    end
  end, TIMEOUT_MS)

  Snacks.input({
    prompt = event.prompt or "Input: ",
    default = event.default or "",
  }, function(value)
    if not responded then
      responded = true
      if timer then timer:stop() end
      if value then
        rpc.send_command(M.format_response(event.id, value))
      else
        rpc.send_command(M.format_cancellation(event.id))
      end
    end
  end)
end

local function handle_editor(event, rpc)
  local buf = vim.api.nvim_create_buf(false, true)
  vim.bo[buf].buftype = "nofile"
  vim.bo[buf].filetype = event.language or "markdown"

  if event.content then
    local lines = vim.split(event.content, "\n")
    vim.api.nvim_buf_set_lines(buf, 0, -1, false, lines)
  end

  vim.cmd("botright split")
  local win = vim.api.nvim_get_current_win()
  vim.api.nvim_win_set_height(win, 15)
  vim.api.nvim_win_set_buf(win, buf)

  local responded = false
  vim.keymap.set("n", "<leader>s", function()
    if not responded then
      responded = true
      local lines = vim.api.nvim_buf_get_lines(buf, 0, -1, false)
      local content = table.concat(lines, "\n")
      rpc.send_command(M.format_response(event.id, content))
      vim.api.nvim_win_close(win, true)
    end
  end, { buffer = buf })

  vim.keymap.set("n", "q", function()
    if not responded then
      responded = true
      rpc.send_command(M.format_cancellation(event.id))
      vim.api.nvim_win_close(win, true)
    end
  end, { buffer = buf })
end

function M.subscribe(rpc)
  rpc.on("extension_ui_request", function(event)
    if event.method == "select" then
      handle_select(event, rpc)
    elseif event.method == "confirm" then
      handle_confirm(event, rpc)
    elseif event.method == "input" then
      handle_input(event, rpc)
    elseif event.method == "editor" then
      handle_editor(event, rpc)
    else
      rpc.send_command(M.format_cancellation(event.id))
    end
  end)
end

return M
```

- [ ] **Step 4: Run test to verify it passes**

```bash
nvim --headless -c "PlenaryBustedFile tests/extension_ui_spec.lua" 2>&1
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add lua/pi-traycer/extension_ui.lua tests/extension_ui_spec.lua
git commit -m "feat: extension UI handler with select, confirm, input, and editor support"
```

---

### Task 14: Commands

**Files:**
- Create: `lua/pi-traycer/commands.lua`

- [ ] **Step 1: Implement all :Pi* commands**

Create `lua/pi-traycer/commands.lua`:

```lua
local M = {}

function M.register()
  vim.api.nvim_create_user_command("PiChat", function(opts)
    local chat = require("pi-traycer.chat")
    local rpc = require("pi-traycer.rpc")

    if not rpc.is_connected() then
      rpc._init_internal_handlers()
      chat.subscribe(rpc)
      require("pi-traycer.plan").subscribe(rpc)
      require("pi-traycer.extension_ui").subscribe(rpc)
      rpc.start_session("chat")
      require("pi-traycer.state").set("session_file", ".pi/sessions/chat.jsonl")
    end

    if opts.args and opts.args ~= "" then
      if not chat.is_open() then chat.open() end
      chat.send(opts.args)
    else
      chat.toggle()
    end
  end, { nargs = "?", desc = "Toggle pi chat panel or send message" })

  vim.api.nvim_create_user_command("PiEpic", function(opts)
    local plan = require("pi-traycer.plan")
    local rpc = require("pi-traycer.rpc")
    local title = opts.args and opts.args ~= "" and opts.args or nil

    if not title then
      vim.ui.input({ prompt = "Epic title: " }, function(input)
        if input and input ~= "" then
          local epic = plan.create_epic(input)
          plan.set_active_epic(epic.id)
          if not rpc.is_connected() then
            rpc._init_internal_handlers()
            require("pi-traycer.chat").subscribe(rpc)
            plan.subscribe(rpc)
            require("pi-traycer.extension_ui").subscribe(rpc)
            rpc.start_session("epic-" .. epic.id)
            require("pi-traycer.state").set("session_file", ".pi/sessions/epic-" .. epic.id .. ".jsonl")
          end
          if not plan.is_open() then plan.open() end
          vim.notify("[pi-traycer] Epic created: " .. input, vim.log.levels.INFO)
        end
      end)
      return
    end

    local epic = plan.create_epic(title)
    plan.set_active_epic(epic.id)
    if not rpc.is_connected() then
      rpc._init_internal_handlers()
      require("pi-traycer.chat").subscribe(rpc)
      plan.subscribe(rpc)
      require("pi-traycer.extension_ui").subscribe(rpc)
      rpc.start_session("epic-" .. epic.id)
      require("pi-traycer.state").set("session_file", ".pi/sessions/epic-" .. epic.id .. ".jsonl")
    end
    if not plan.is_open() then plan.open() end
    vim.notify("[pi-traycer] Epic created: " .. title, vim.log.levels.INFO)
  end, { nargs = "?", desc = "Create a new epic" })

  vim.api.nvim_create_user_command("PiPlan", function(opts)
    local plan = require("pi-traycer.plan")
    if opts.args and opts.args ~= "" then
      plan.set_active_epic(opts.args)
    end
    plan.toggle()
  end, { nargs = "?", desc = "Toggle plan panel or load specific epic" })

  vim.api.nvim_create_user_command("PiFileAdd", function(opts)
    local path = opts.args and opts.args ~= "" and opts.args or vim.api.nvim_buf_get_name(0)
    if path == "" then
      vim.notify("[pi-traycer] No file to add", vim.log.levels.WARN)
      return
    end
    vim.notify("[pi-traycer] Added to context: " .. vim.fn.fnamemodify(path, ":."), vim.log.levels.INFO)
  end, { nargs = "?", complete = "file", desc = "Add file to context" })

  vim.api.nvim_create_user_command("PiBash", function(opts)
    local rpc = require("pi-traycer.rpc")
    if not rpc.is_connected() then
      vim.notify("[pi-traycer] Not connected to pi", vim.log.levels.WARN)
      return
    end
    rpc.send_command({ type = "bash", command = opts.args })
  end, { nargs = "+", desc = "Run bash command through pi" })

  vim.api.nvim_create_user_command("PiAbort", function()
    local rpc = require("pi-traycer.rpc")
    if rpc.is_streaming() then
      rpc.send_command({ type = "abort" })
      vim.notify("[pi-traycer] Aborting...", vim.log.levels.INFO)
    else
      vim.notify("[pi-traycer] Nothing to abort", vim.log.levels.INFO)
    end
  end, { desc = "Abort current pi operation" })

  vim.api.nvim_create_user_command("PiStatus", function()
    local state = require("pi-traycer.state")
    local rpc = require("pi-traycer.rpc")
    local stats = state.get("token_stats") or {}
    local connected = rpc.is_connected() and "Connected" or "Disconnected"
    local epic_id = state.get("active_epic_id") or "none"
    local msg = string.format(
      "[pi-traycer] %s | Epic: %s\nTokens: %d in / %d out\nCache: %d read / %d write",
      connected,
      epic_id,
      stats.input or 0,
      stats.output or 0,
      stats.cache_read or 0,
      stats.cache_write or 0
    )
    vim.notify(msg, vim.log.levels.INFO)
  end, { desc = "Show pi session status" })
end

return M
```

- [ ] **Step 2: Manual verification**

```vim
:lua require("pi-traycer").setup({})
:lua require("pi-traycer.commands").register()
:PiChat
:PiStatus
:PiPlan
```

Expected: Chat panel opens, status shows "Disconnected", plan panel opens.

- [ ] **Step 3: Commit**

```bash
git add lua/pi-traycer/commands.lua
git commit -m "feat: all :Pi* user commands"
```

---

### Task 15: Keymaps & Plugin Entry

**Files:**
- Create: `lua/pi-traycer/keymaps.lua`
- Create: `plugin/pi-traycer.lua`
- Modify: `lua/pi-traycer/init.lua`

- [ ] **Step 1: Implement keymaps.lua**

Create `lua/pi-traycer/keymaps.lua`:

```lua
local M = {}

function M.setup()
  local config = require("pi-traycer.config").get()
  local maps = config.keymaps

  if maps.chat then
    vim.keymap.set("n", maps.chat, "<cmd>PiChat<cr>", { desc = "Toggle pi chat" })
  end
  if maps.epic then
    vim.keymap.set("n", maps.epic, "<cmd>PiEpic<cr>", { desc = "Create/focus pi epic" })
  end
  if maps.plan then
    vim.keymap.set("n", maps.plan, "<cmd>PiPlan<cr>", { desc = "Toggle pi plan panel" })
  end
  if maps.send_selection then
    vim.keymap.set("v", maps.send_selection, function()
      vim.cmd('noautocmd normal! "vy')
      local text = vim.fn.getreg("v")
      if text and text ~= "" then
        local chat = require("pi-traycer.chat")
        if not chat.is_open() then chat.open() end
        chat.send(text, { include_selection = true })
      end
    end, { desc = "Send selection to pi chat" })
  end
  if maps.abort then
    vim.keymap.set("n", maps.abort, "<cmd>PiAbort<cr>", { desc = "Abort pi operation" })
  end
end

return M
```

- [ ] **Step 2: Implement plugin entry point**

Create `plugin/pi-traycer.lua`:

```lua
if vim.g.loaded_pi_traycer then
  return
end
vim.g.loaded_pi_traycer = true

if vim.fn.executable("pi") ~= 1 then
  vim.notify("[pi-traycer] 'pi' executable not found in PATH. Plugin disabled.", vim.log.levels.WARN)
  return
end
```

- [ ] **Step 3: Update init.lua with full setup**

Replace `lua/pi-traycer/init.lua`:

```lua
local M = {}

function M.setup(opts)
  local config = require("pi-traycer.config")
  config.setup(opts)

  require("pi-traycer.commands").register()
  require("pi-traycer.keymaps").setup()
end

function M.health()
  vim.health.start("pi-traycer")

  if vim.fn.executable("pi") == 1 then
    vim.health.ok("pi executable found")
  else
    vim.health.error("pi executable not found", { "Install pi: npm install -g @mariozechner/pi-coding-agent" })
  end

  local has_snacks, _ = pcall(require, "snacks")
  if has_snacks then
    vim.health.ok("snacks.nvim found")
  else
    vim.health.error("snacks.nvim not found", { "Install: https://github.com/folke/snacks.nvim" })
  end

  local has_edgy, _ = pcall(require, "edgy")
  if has_edgy then
    vim.health.ok("edgy.nvim found")
  else
    vim.health.warn("edgy.nvim not found (optional for panel docking)", { "Install: https://github.com/folke/edgy.nvim" })
  end

  local has_plenary, _ = pcall(require, "plenary")
  if has_plenary then
    vim.health.ok("plenary.nvim found")
  else
    vim.health.warn("plenary.nvim not found (needed for tests)", { "Install: https://github.com/nvim-lua/plenary.nvim" })
  end
end

return M
```

- [ ] **Step 4: Manual verification — full plugin load**

```vim
:lua require("pi-traycer").setup({})
:checkhealth pi-traycer
:PiChat
:PiStatus
```

Expected: Health check passes. Commands work. Keymaps bound.

- [ ] **Step 5: Commit**

```bash
git add lua/pi-traycer/keymaps.lua lua/pi-traycer/init.lua plugin/pi-traycer.lua
git commit -m "feat: keymaps, plugin entry point, health check, and full setup wiring"
```

---

### Task 16: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README**

Create `README.md`:

````markdown
# pi-traycer.nvim

Traycer-like spec-driven development in Neovim using the [pi coding agent](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent).

Create epics, generate structured implementation plans, track tasks — all without leaving your terminal.

## Requirements

- Neovim 0.10+
- [pi coding agent](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent) installed and in PATH
- [snacks.nvim](https://github.com/folke/snacks.nvim)
- [edgy.nvim](https://github.com/folke/edgy.nvim)
- [plenary.nvim](https://github.com/nvim-lua/plenary.nvim) (for tests)

## Installation

Using [lazy.nvim](https://github.com/folke/lazy.nvim):

```lua
{
  "pbonh/pi-traycer.nvim",
  dependencies = {
    "folke/snacks.nvim",
    "folke/edgy.nvim",
    "nvim-lua/plenary.nvim",
  },
  opts = {},
}
```

### Pi Extension

Copy the `create_plan` extension to pi's extensions directory:

```bash
cp extensions/create-plan.ts ~/.pi/agent/extensions/
```

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

Set any keymap to `false` to disable it.

## Commands

| Command | Description |
|---------|-------------|
| `:PiChat [message?]` | Toggle chat panel, optionally send message |
| `:PiEpic [title?]` | Create a new epic |
| `:PiPlan [epic-id?]` | Toggle plan panel |
| `:PiFileAdd [path?]` | Add file to context |
| `:PiBash <command>` | Run bash through pi |
| `:PiAbort` | Cancel current operation |
| `:PiStatus` | Show session stats |

## Keymaps

| Mapping | Action |
|---------|--------|
| `<leader>pc` | Toggle chat |
| `<leader>pe` | Create/focus epic |
| `<leader>pp` | Toggle plan panel |
| `<leader>ps` | Send selection to chat (visual mode) |
| `<leader>pa` | Abort |

**Plan panel buffer keymaps:**

| Key | Action |
|-----|--------|
| `t` | Toggle task status |
| `Enter` | Show task info |
| `d` | Show task details |
| `q` | Close panel |

## Running Tests

```bash
nvim --headless -c "PlenaryBustedDirectory tests/ { minimal_init = 'tests/minimal_init.lua' }"
```

## Health Check

```vim
:checkhealth pi-traycer
```
````

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: README with installation, configuration, and usage guide"
```

---

### Task 17: End-to-End Integration Test

**Files:** None — manual verification only.

- [ ] **Step 1: Run all unit tests**

```bash
cd ~/Code/github.com/pbonh/pi-traycer.nvim
nvim --headless -c "PlenaryBustedDirectory tests/ { minimal_init = 'tests/minimal_init.lua' }" 2>&1
```

Expected: All tests PASS.

- [ ] **Step 2: Full E2E manual test**

Open Neovim in a test project:

```vim
:lua require("pi-traycer").setup({})
:checkhealth pi-traycer
:PiEpic "Test auth system"
:PiChat Create a plan for implementing user authentication with login and session management
```

Expected sequence:
1. Health check passes
2. Epic created, plan panel opens at bottom
3. Chat panel opens on right
4. Pi receives the message, streams response
5. Pi calls `create_plan` tool with structured tasks
6. Plan panel updates with task tree
7. `:PiStatus` shows token counts

- [ ] **Step 3: Test task management**

In the plan panel:
- Navigate to a task line, press `t` → status cycles (○ → ▶ → ✓ → ○)
- Press `d` → task details shown in notification
- Press `q` → panel closes
- `:PiPlan` → panel reopens with persisted state

- [ ] **Step 4: Test abort**

```vim
:PiChat Tell me a very long story about every programming language ever created
:PiAbort
```

Expected: Streaming stops. Chat shows partial response.

- [ ] **Step 5: Verify persistence**

Close and reopen Neovim:

```vim
:lua require("pi-traycer").setup({})
:PiPlan <epic-id from step 2>
```

Expected: Plan panel shows the same epic with task statuses preserved.

- [ ] **Step 6: Commit any fixes**

```bash
git add -A
git commit -m "fix: integration test fixes"
```

Only commit if fixes were needed. Skip if everything passed.
