"""Governance evaluation engine.

Turns declarative policies + registry data into computable compliance
state and effective trust scores.  This is the missing link between
"policies exist" and "policies have consequences."
"""

from __future__ import annotations

from typing import Any

from .registry import AgentRecord, CityRecord, WorldRegistry

# Trust-level base scores (higher = more trusted).
_TRUST_BASE: dict[str, float] = {
    "founding": 1.0,
    "verified": 0.8,
    "observed": 0.5,
    "untrusted": 0.2,
}


def _node_repo(node: CityRecord | AgentRecord) -> str:
    return node.repo


def _node_id(node: CityRecord | AgentRecord) -> str:
    if isinstance(node, CityRecord):
        return node.city_id
    return node.agent_id


def _node_type(node: CityRecord | AgentRecord) -> str:
    return "city" if isinstance(node, CityRecord) else "agent"


def evaluate_node_compliance(
    node: CityRecord | AgentRecord,
    policies: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Evaluate a single node against all applicable policies. Returns violations."""
    violations: list[dict[str, Any]] = []
    caps = set(node.capabilities)

    for policy in policies:
        pid = policy.get("id", "")
        enforcement = policy.get("enforcement", "")

        if pid == "federation_descriptor_required" and "descriptor_incomplete" in caps:
            violations.append({
                "policy_id": pid,
                "enforcement": enforcement,
                "trust_penalty": float(policy.get("trust_penalty", 0)),
                "reason": "missing or incomplete .well-known/agent-federation.json",
            })

        # federation_ci_required: we can't verify CI at build time, but nodes
        # with descriptor_incomplete are likely also missing CI.  A future
        # steward diagnostic will provide authoritative CI status; for now
        # this policy is only enforced via steward_diagnostic (not here).

    return violations


def compute_trust_score(
    node: CityRecord | AgentRecord,
    violations: list[dict[str, Any]],
) -> float:
    """Compute effective trust = base score - sum(penalties), clamped to [0, 1]."""
    base = _TRUST_BASE.get(node.trust_level, 0.0)
    penalty = sum(v.get("trust_penalty", 0.0) for v in violations)
    return round(max(0.0, min(1.0, base - penalty)), 2)


def evaluate_federation_governance(
    registry: WorldRegistry,
    policies: list[dict[str, Any]],
) -> dict[str, Any]:
    """Full governance evaluation across the federation.

    Returns a governance report suitable for inclusion in world_state.json.
    """
    node_reports: list[dict[str, Any]] = []
    total_penalty = 0.0

    all_nodes: list[CityRecord | AgentRecord] = [*registry.cities, *registry.agents]

    for node in all_nodes:
        violations = evaluate_node_compliance(node, policies)
        trust_score = compute_trust_score(node, violations)
        penalty = sum(v.get("trust_penalty", 0.0) for v in violations)
        total_penalty += penalty

        node_reports.append({
            "node_id": _node_id(node),
            "node_type": _node_type(node),
            "trust_level": node.trust_level,
            "trust_score": trust_score,
            "violations": violations,
            "compliant": len(violations) == 0,
        })

    compliant_count = sum(1 for r in node_reports if r["compliant"])
    total = len(node_reports)

    return {
        "evaluated_policies": len(policies),
        "evaluated_nodes": total,
        "compliant_nodes": compliant_count,
        "non_compliant_nodes": total - compliant_count,
        "compliance_ratio": round(compliant_count / total, 2) if total else 0.0,
        "total_trust_penalty": round(total_penalty, 2),
        "nodes": node_reports,
    }
