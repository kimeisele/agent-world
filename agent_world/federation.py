"""Federation communication for agent-world (World Authority).

Emits:
  - world_state_update: after each heartbeat aggregation
  - policy_update: when governance policies change
  - heartbeat: periodic health announcement

Receives:
  - city_report: from agent-city (population, health, campaigns)
  - heartbeat: from any peer (track liveness)
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

from nadi_kit import NadiNode, NadiMessage

_REPO_ROOT = Path(__file__).resolve().parent.parent

log = logging.getLogger("agent_world.federation")


def create_world_node(federation_dir: Path | None = None) -> NadiNode:
    """Create the NadiNode for agent-world."""
    if federation_dir is None:
        federation_dir = _REPO_ROOT / "data" / "federation"
    peer_json = federation_dir / "peer.json"
    node = NadiNode.from_peer_json(peer_json)

    # Register handlers
    node.on("heartbeat", _handle_heartbeat)
    node.on("city_report", _handle_city_report)

    return node


def emit_world_state(node: NadiNode, world_state: dict[str, Any]) -> int:
    """Emit world_state_update to all peers after aggregation."""
    msgs = node.emit(
        "world_state_update",
        {
            "version": world_state.get("version", 0),
            "timestamp": time.time(),
            "cities": world_state.get("cities", {}),
            "agents": world_state.get("agents", {}),
            "policies_hash": world_state.get("policies_hash", ""),
            "federation_health": world_state.get("federation_health", {}),
        },
        priority=2,
    )
    return len(msgs)


def emit_policy_update(node: NadiNode, policies: dict[str, Any]) -> int:
    """Emit policy_update when governance changes."""
    msgs = node.emit(
        "policy_update",
        {
            "timestamp": time.time(),
            "policies": policies,
        },
        priority=2,
    )
    return len(msgs)


# ── Handlers ─────────────────────────────────────────────────────────────

_city_reports: dict[str, dict[str, Any]] = {}  # latest report per city


def _handle_heartbeat(msg: NadiMessage) -> None:
    log.info("heartbeat from %s (health=%.2f)", msg.source, msg.payload.get("health", 0))


def _handle_city_report(msg: NadiMessage) -> None:
    log.info(
        "city_report from %s: pop=%d alive=%d heartbeat=%d",
        msg.source,
        msg.payload.get("population", 0),
        msg.payload.get("alive", 0),
        msg.payload.get("heartbeat", 0),
    )
    _city_reports[msg.source] = {
        "timestamp": msg.timestamp,
        "population": msg.payload.get("population", 0),
        "alive": msg.payload.get("alive", 0),
        "heartbeat": msg.payload.get("heartbeat", 0),
        "chain_valid": msg.payload.get("chain_valid", False),
    }


def get_city_reports() -> dict[str, dict[str, Any]]:
    """Get latest city reports received via NADI."""
    return dict(_city_reports)
