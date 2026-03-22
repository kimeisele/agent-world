"""Minimal world heartbeat for founding registry/policy aggregation."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import load_yaml, repo_root
from .governance import evaluate_federation_governance
from .registry import load_world_registry
from .schema import validate_policies_or_raise

log = logging.getLogger("agent_world.heartbeat")


def _collect_capability_index(
    cities: tuple, agents: tuple,
) -> dict[str, list[str]]:
    """Map each capability to the node IDs that provide it (deduplicated)."""
    index: dict[str, set[str]] = {}
    for city in cities:
        for cap in city.capabilities:
            index.setdefault(cap, set()).add(city.city_id)
    for agent in agents:
        for cap in agent.capabilities:
            index.setdefault(cap, set()).add(agent.agent_id)
    return {k: sorted(v) for k, v in sorted(index.items())}


def _build_federation_health(
    cities: tuple, agents: tuple,
) -> dict[str, Any]:
    """Per-node health + descriptor status summary."""
    nodes: list[dict[str, Any]] = []

    for city in cities:
        nodes.append({
            "node_id": city.city_id,
            "node_type": "city",
            "status": city.status,
            "trust_level": city.trust_level,
            "has_heartbeat": city.last_heartbeat is not None,
            "descriptor_complete": "descriptor_incomplete" not in city.capabilities,
            "capability_count": len(city.capabilities),
        })

    for agent in agents:
        nodes.append({
            "node_id": agent.agent_id,
            "node_type": "agent",
            "status": agent.status,
            "trust_level": agent.trust_level,
            "has_heartbeat": True,  # agents don't have heartbeat field — always considered present
            "descriptor_complete": "descriptor_incomplete" not in agent.capabilities,
            "capability_count": len(agent.capabilities),
        })

    total = len(nodes)
    descriptor_complete = sum(1 for n in nodes if n["descriptor_complete"])
    active = sum(1 for n in nodes if n["status"] in ("alive", "active"))

    return {
        "total_nodes": total,
        "active_nodes": active,
        "descriptor_complete": descriptor_complete,
        "descriptor_incomplete": total - descriptor_complete,
        "health_ratio": round(active / total, 2) if total else 0.0,
        "nodes": nodes,
    }


def build_world_state(*, base_path: Path | None = None, now: datetime | None = None) -> dict[str, Any]:
    root = repo_root(base_path)
    registry = load_world_registry(base_path=root)
    world_config = load_yaml("config/world.yaml", base_path=root)
    policies_payload = load_yaml("config/world_policies.yaml", base_path=root)
    validate_policies_or_raise(policies_payload)
    policies = policies_payload.get("policies") or []
    now_utc = (now or datetime.now(timezone.utc)).isoformat()

    warnings = [f"missing_last_heartbeat:{city.city_id}" for city in registry.cities if not city.last_heartbeat]
    for agent in registry.agents:
        if "descriptor_incomplete" in agent.capabilities:
            warnings.append(f"descriptor_incomplete:{agent.agent_id}")

    federation_health = _build_federation_health(registry.cities, registry.agents)
    capability_index = _collect_capability_index(registry.cities, registry.agents)
    governance = evaluate_federation_governance(registry, policies)

    # Surface non-compliant nodes as warnings
    for node in governance["nodes"]:
        if not node["compliant"]:
            for v in node["violations"]:
                warnings.append(f"policy_violation:{node['node_id']}:{v['policy_id']}")

    return {
        "kind": "world_state",
        "version": 4,
        "world_id": registry.world_id,
        "generated_at_utc": now_utc,
        "world": world_config.get("world") or {},
        "summary": {
            "registered_cities": len(registry.cities),
            "registered_agents": len(registry.agents),
            "total_nodes": len(registry.cities) + len(registry.agents),
            "founding_cities": len([city for city in registry.cities if city.trust_level == "founding"]),
            "active_policies": len(policies),
        },
        "federation_health": federation_health,
        "governance": governance,
        "capability_index": capability_index,
        "cities": [city.to_payload() for city in registry.cities],
        "agents": [agent.to_payload() for agent in registry.agents],
        "warnings": warnings,
    }


def run_world_heartbeat(*, base_path: Path | None = None, output_path: Path | None = None) -> tuple[Path, dict[str, Any]]:
    root = repo_root(base_path)
    state = build_world_state(base_path=root)
    destination = Path(output_path).resolve() if output_path is not None else root / "data/world_state.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(state, indent=2) + "\n")

    # Legislator: Head Agent cognitive cycle (replaces simple emit)
    try:
        from agent_world.legislator import run_legislator
        leg_result = run_legislator(base_path=root)
        log.info("Legislator: %s", leg_result)
    except Exception as exc:
        log.warning("Legislator failed (non-fatal): %s", exc)
        # Fallback to simple NADI emit
        try:
            from agent_world.federation import create_world_node, emit_world_state
            fed_dir = root / "data" / "federation"
            node = create_world_node(fed_dir)
            emit_world_state(node, state)
            node.heartbeat(health=1.0, version=str(state.get("version", 0)))
            node.sync()
        except Exception as exc2:
            log.warning("NADI fallback also failed: %s", exc2)

    return destination, state
