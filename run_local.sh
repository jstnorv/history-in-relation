#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-5050}"

cleanup_stale_project_processes() {
  if ! command -v lsof >/dev/null 2>&1; then
    echo "lsof is not installed; skipping stale-process cleanup."
    return
  fi

  while read -r pid; do
    [ -n "${pid}" ] || continue
    cmd="$(ps -p "${pid}" -o command= 2>/dev/null || true)"
    [[ -n "${cmd}" ]] || continue

    if printf '%s' "${cmd}" | grep -Eiq 'python .*app\.py|python.*app\.py|flask .*--app app|python -m flask .*app'; then
      echo "Stopping stale project process on port ${PORT}: PID ${pid} (${cmd})"
      kill "${pid}" 2>/dev/null || true
      sleep 0.5
      if kill -0 "${pid}" 2>/dev/null; then
        kill -9 "${pid}" 2>/dev/null || true
      fi
    fi
  done < <(lsof -t -nP -iTCP:"${PORT}" -sTCP:LISTEN 2>/dev/null || true)
}

cleanup_stale_project_processes

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PROJECT_DIR}/.venv/bin/python"
if [[ ! -x "${PYTHON_BIN}" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
  else
    PYTHON_BIN="$(command -v python || true)"
  fi
fi

if [[ -z "${PYTHON_BIN}" || ! -x "${PYTHON_BIN}" ]]; then
  echo "Could not find a Python interpreter for this project." >&2
  exit 1
fi

echo "Starting app on http://127.0.0.1:${PORT}"
export FLASK_DEBUG=0
exec "${PYTHON_BIN}" app.py
