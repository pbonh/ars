update-brew:
  #!/usr/bin/env bash
  set -euo pipefail
  if ! command -v brew >/dev/null 2>&1; then
    echo "update-brew: brew not found on PATH, skipping" >&2
    exit 0
  fi
  {{ task_prelude }} brew upgrade
  {{ task_prelude }} brew cleanup

update-node:
  #!/usr/bin/env bash
  set -euo pipefail
  if ! command -v npm >/dev/null 2>&1; then
    echo "update-node: npm not found on PATH, skipping" >&2
    exit 0
  fi
  {{ task_prelude }} npm update -g

update-pnpm:
  #!/usr/bin/env bash
  set -euo pipefail
  if ! command -v pnpm >/dev/null 2>&1; then
    echo "update-pnpm: pnpm not found on PATH, skipping" >&2
    exit 0
  fi
  {{ task_prelude }} pnpm update -g

update-uv:
  #!/usr/bin/env bash
  set -euo pipefail
  if ! command -v uv >/dev/null 2>&1; then
    echo "update-uv: uv not found on PATH, skipping" >&2
    exit 0
  fi
  {{ task_prelude }} uv tool upgrade --all

update-mise:
  #!/usr/bin/env bash
  set -euo pipefail
  if ! command -v mise >/dev/null 2>&1; then
    echo "update-mise: mise not found on PATH, skipping" >&2
    exit 0
  fi
  {{ task_prelude }} mise upgrade

update-devbox:
  #!/usr/bin/env bash
  set -euo pipefail
  if ! command -v devbox >/dev/null 2>&1; then
    echo "update-devbox: devbox not found on PATH, skipping" >&2
    exit 0
  fi
  {{ task_prelude }} devbox global update

update: update-brew update-node update-pnpm update-uv update-mise update-devbox
