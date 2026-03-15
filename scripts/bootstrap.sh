#!/usr/bin/env bash
# bootstrap.sh — Universal setup for agent-world.
# Works inside DevContainers, Codespaces, GitPod, Cloud Code Web,
# and standalone on any Linux/macOS with Python 3.11+.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== agent-world bootstrap ==="

# Detect Python
PYTHON=""
for candidate in python3.11 python3 python; do
  if command -v "$candidate" &>/dev/null; then
    PYTHON="$candidate"
    break
  fi
done

if [ -z "$PYTHON" ]; then
  echo "ERROR: No Python 3.11+ found. Install Python first." >&2
  exit 1
fi

PY_VERSION=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Using $PYTHON ($PY_VERSION)"

# Create venv if missing
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  "$PYTHON" -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install package with dev dependencies
echo "Installing agent-world[dev]..."
pip install -e '.[dev]' --quiet

# Verify installation
echo "Verifying..."
python -c "import agent_world; print('agent_world package OK')"
pytest -q --tb=short 2>/dev/null && echo "Tests passed." || echo "WARNING: Some tests failed."

echo "=== bootstrap complete ==="
