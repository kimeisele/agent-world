"""Minimal world heartbeat for founding registry/policy aggregation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import load_yaml, repo_root
from .registry import load_world_registry


def build_world_state(*, base_path: Path | None = None, now: datetime | None = None) -> dict[str, Any]:
    root = repo_root(base_path)
    registry = load_world_registry(base_path=root)
    world_config = load_yaml("config/world.yaml", base_path=root)
    policies = load_yaml("config/world_policies.yaml", base_path=root).get("policies") or []
    now_utc = (now or datetime.now(timezone.utc)).isoformat()
    warnings = [f"missing_last_heartbeat:{city.city_id}" for city in registry.cities if not city.last_heartbeat]
    return {
        "kind": "world_state",
        "version": 1,
        "world_id": registry.world_id,
        "generated_at_utc": now_utc,
        "world": world_config.get("world") or {},
        "summary": {
            "registered_cities": len(registry.cities),
            "founding_cities": len([city for city in registry.cities if city.trust_level == "founding"]),
            "active_policies": len(policies),
        },
        "cities": [city.to_payload() for city in registry.cities],
        "warnings": warnings,
    }


def run_world_heartbeat(*, base_path: Path | None = None, output_path: Path | None = None) -> tuple[Path, dict[str, Any]]:
    root = repo_root(base_path)
    state = build_world_state(base_path=root)
    destination = Path(output_path).resolve() if output_path is not None else root / "data/world_state.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(state, indent=2) + "\n")
    return destination, state
