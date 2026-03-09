"""Config loaders for agent-world founding state."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def repo_root(base_path: Path | None = None) -> Path:
    return Path(base_path).resolve() if base_path is not None else Path(__file__).resolve().parents[1]


def load_yaml(relative_path: str, *, base_path: Path | None = None) -> dict[str, Any]:
    path = repo_root(base_path) / relative_path
    payload = yaml.safe_load(path.read_text()) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"invalid_yaml_payload:{relative_path}")
    return payload
