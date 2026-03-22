"""Legislator — Head Agent for agent-world (Governance Layer).

Perceives: city reports, compliance state, trust scores
Judges: policy violations, trust penalties, governance health
Acts: policy_update broadcasts, trust adjustments via NADI
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

log = logging.getLogger("agent_world.legislator")

_REPO_ROOT = Path(__file__).resolve().parent.parent

# Thresholds
VIOLATION_TOLERANCE_CYCLES = 3  # Allow N cycles before penalty
TRUST_PENALTY_PER_VIOLATION = 0.1
COMPLIANCE_HEALTHY_RATIO = 0.8


class Legislator:
    """Head Agent for agent-world. Enforces federation governance."""

    agent_type = "legislator"

    def __init__(self, base_path: Path | None = None) -> None:
        self.base_path = base_path or _REPO_ROOT
        self.federation_dir = self.base_path / "data" / "federation"
        self.cycle_count = 0
        self._nadi_node = None

    def _get_nadi_node(self):
        if self._nadi_node is None:
            import sys
            sys.path.insert(0, str(_REPO_ROOT))
            from nadi_kit import NadiNode
            self._nadi_node = NadiNode.from_peer_json(self.federation_dir / "peer.json")
        return self._nadi_node

    def heartbeat(self) -> dict[str, Any]:
        """Full Legislator cycle."""
        self.cycle_count += 1
        observations = self.perceive()
        decisions = self.judge(observations)
        actions = self.act(decisions)
        self.emit_status(observations, actions)

        log.info(
            "Legislator #%d: %d nodes evaluated, %d decisions, %d actions",
            self.cycle_count, observations.get("total_nodes", 0),
            len(decisions), len(actions),
        )
        return {"cycle": self.cycle_count, "observations": observations,
                "decisions": decisions, "actions": actions}

    def perceive(self) -> dict[str, Any]:
        """Run governance evaluation on current world state."""
        from agent_world.config import load_yaml, repo_root
        from agent_world.governance import evaluate_federation_governance
        from agent_world.registry import load_world_registry
        from agent_world.schema import validate_policies_or_raise

        root = repo_root(self.base_path)
        registry = load_world_registry(root / "config" / "world_registry.yaml")
        raw_policies = load_yaml(root / "config" / "world_policies.yaml")
        policies = validate_policies_or_raise(raw_policies.get("policies", []))
        governance = evaluate_federation_governance(registry, policies)

        non_compliant = [n for n in governance.get("nodes", []) if not n.get("compliant")]

        # Read inbox for city reports
        city_reports = {}
        inbox_path = self.federation_dir / "nadi_inbox.json"
        if inbox_path.exists():
            try:
                msgs = json.loads(inbox_path.read_text())
                for m in msgs:
                    if m.get("operation") == "city_report":
                        city_reports[m.get("source", "?")] = m.get("payload", {})
            except Exception:
                pass

        return {
            "compliance_ratio": governance.get("compliance_ratio", 0),
            "total_nodes": governance.get("total_nodes", 0),
            "non_compliant": non_compliant,
            "city_reports": city_reports,
            "timestamp": time.time(),
        }

    def judge(self, observations: dict[str, Any]) -> list[dict[str, Any]]:
        """Deterministic governance rules. Zero LLM."""
        decisions = []

        for node in observations.get("non_compliant", []):
            node_id = node.get("node_id", "?")
            violations = [v["policy_id"] for v in node.get("violations", [])]
            trust_penalty = sum(
                v.get("trust_penalty", TRUST_PENALTY_PER_VIOLATION)
                for v in node.get("violations", [])
            )
            decisions.append({
                "type": "policy_violation",
                "node_id": node_id,
                "violations": violations,
                "trust_penalty": round(trust_penalty, 2),
                "action": "broadcast_violation",
            })

        ratio = observations.get("compliance_ratio", 1.0)
        if ratio < COMPLIANCE_HEALTHY_RATIO:
            decisions.append({
                "type": "federation_health_warning",
                "compliance_ratio": ratio,
                "action": "alert_steward",
            })

        return decisions

    def act(self, decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Execute governance decisions via NADI."""
        node = self._get_nadi_node()
        actions = []

        violations = [d for d in decisions if d["type"] == "policy_violation"]
        if violations:
            node.emit(
                "policy_update",
                {
                    "violations": [{
                        "node_id": v["node_id"],
                        "policies": v["violations"],
                        "trust_penalty": v["trust_penalty"],
                    } for v in violations],
                    "compliance_ratio": 0,  # will be set from observations
                    "issuer": "legislator",
                    "timestamp": time.time(),
                },
                priority=2,
            )
            actions.append({"emitted": "policy_update", "violation_count": len(violations)})
            log.info("Legislator ACT: broadcasted %d violations", len(violations))

        health_warnings = [d for d in decisions if d["type"] == "federation_health_warning"]
        for hw in health_warnings:
            node.emit(
                "governance_alert",
                {
                    "type": "federation_health_warning",
                    "compliance_ratio": hw["compliance_ratio"],
                    "source": "legislator",
                    "timestamp": time.time(),
                },
                target="steward",
                priority=2,
            )
            actions.append({"emitted": "governance_alert", "target": "steward"})
            log.info("Legislator ACT: governance_alert → steward (ratio=%.2f)", hw["compliance_ratio"])

        return actions

    def emit_status(self, observations: dict, actions: list) -> None:
        """Emit heartbeat with head_agent identification."""
        node = self._get_nadi_node()
        node.heartbeat(health=1.0)
        node.emit(
            "head_agent_status",
            {
                "head_agent": self.agent_type,
                "cycle": self.cycle_count,
                "compliance_ratio": observations.get("compliance_ratio", 0),
                "non_compliant_count": len(observations.get("non_compliant", [])),
                "actions_taken": len(actions),
                "timestamp": time.time(),
            },
            priority=1,
        )


def run_legislator(base_path: Path | None = None) -> dict:
    """Entry point for CI workflow."""
    leg = Legislator(base_path=base_path)
    return leg.heartbeat()
