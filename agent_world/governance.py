"""Governance evaluation engine.

Turns declarative policies + registry data into computable compliance
state and effective trust scores.  This is the missing link between
"policies exist" and "policies have consequences."

Policy evaluability from registry data alone:
- federation_descriptor_required: FULL (descriptor_incomplete in capabilities)
- federation_ci_required: FULL for descriptor_incomplete nodes (they can't
  have CI if they don't even have a proper descriptor); UNVERIFIABLE for
  others without steward diagnostic data.
- cross_city_visa_recognition: PRECONDITION CHECK (cities below trust_minimum
  cannot issue recognized visas — flag as advisory)
- city_autonomy_limits: RUNTIME ONLY (event-driven governance gate)
- federation_bandwidth_quota: RUNTIME ONLY (rate limiter)
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

# Policies that can only be checked at runtime, not at heartbeat time.
_RUNTIME_ONLY_POLICIES = {"city_autonomy_limits", "federation_bandwidth_quota"}


def _node_id(node: CityRecord | AgentRecord) -> str:
    if isinstance(node, CityRecord):
        return node.city_id
    return node.agent_id


def _node_type(node: CityRecord | AgentRecord) -> str:
    return "city" if isinstance(node, CityRecord) else "agent"


def _check_descriptor_required(
    node: CityRecord | AgentRecord,
    policy: dict[str, Any],
    violations: list[dict[str, Any]],
) -> None:
    if "descriptor_incomplete" in node.capabilities:
        violations.append({
            "policy_id": policy["id"],
            "enforcement": policy.get("enforcement", ""),
            "trust_penalty": float(policy.get("trust_penalty", 0)),
            "reason": "missing or incomplete .well-known/agent-federation.json",
        })


def _check_ci_required(
    node: CityRecord | AgentRecord,
    policy: dict[str, Any],
    violations: list[dict[str, Any]],
) -> None:
    # Nodes with descriptor_incomplete definitively lack CI —
    # if they can't even maintain a descriptor, they don't have CI.
    # Nodes WITH a descriptor: we can't verify CI without steward diagnostic,
    # so they get the benefit of the doubt.
    if "descriptor_incomplete" in node.capabilities:
        violations.append({
            "policy_id": policy["id"],
            "enforcement": policy.get("enforcement", ""),
            "trust_penalty": float(policy.get("trust_penalty", 0)),
            "reason": "descriptor_incomplete implies no CI (unverifiable without steward diagnostic)",
        })


def _check_devcontainer_required(
    node: CityRecord | AgentRecord,
    policy: dict[str, Any],
    violations: list[dict[str, Any]],
) -> None:
    # Nodes that explicitly declare devcontainer_ready are compliant.
    # Nodes without the capability AND with descriptor_incomplete are definitely non-compliant.
    # Others: unverifiable without steward diagnostic, benefit of the doubt.
    if "devcontainer_ready" not in node.capabilities and "descriptor_incomplete" in node.capabilities:
        violations.append({
            "policy_id": policy["id"],
            "enforcement": policy.get("enforcement", ""),
            "trust_penalty": float(policy.get("trust_penalty", 0)),
            "reason": "no devcontainer_ready capability and descriptor_incomplete",
        })


def _check_visa_recognition_precondition(
    node: CityRecord | AgentRecord,
    policy: dict[str, Any],
    advisories: list[dict[str, Any]],
) -> None:
    # Only applies to cities — agents don't issue visas.
    if not isinstance(node, CityRecord):
        return
    trust_minimum = policy.get("trust_minimum", "verified")
    trust_order = ["untrusted", "observed", "verified", "founding"]
    node_rank = trust_order.index(node.trust_level) if node.trust_level in trust_order else -1
    min_rank = trust_order.index(trust_minimum) if trust_minimum in trust_order else 0
    if node_rank < min_rank:
        advisories.append({
            "policy_id": policy["id"],
            "severity": "advisory",
            "trust_penalty": 0.0,
            "reason": f"trust_level '{node.trust_level}' below minimum '{trust_minimum}' for visa recognition",
        })


# Dispatch table: policy_id → checker function.
_POLICY_CHECKERS: dict[str, Any] = {
    "federation_descriptor_required": _check_descriptor_required,
    "federation_ci_required": _check_ci_required,
    "federation_devcontainer_required": _check_devcontainer_required,
}

_ADVISORY_CHECKERS: dict[str, Any] = {
    "cross_city_visa_recognition": _check_visa_recognition_precondition,
}


def evaluate_node_compliance(
    node: CityRecord | AgentRecord,
    policies: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Evaluate a single node against all applicable policies.

    Returns (violations, advisories).  Violations carry trust penalties.
    Advisories are informational (precondition checks, runtime-only notices).
    """
    violations: list[dict[str, Any]] = []
    advisories: list[dict[str, Any]] = []

    for policy in policies:
        pid = policy.get("id", "")

        checker = _POLICY_CHECKERS.get(pid)
        if checker:
            checker(node, policy, violations)

        advisory_checker = _ADVISORY_CHECKERS.get(pid)
        if advisory_checker:
            advisory_checker(node, policy, advisories)

    return violations, advisories


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
    """Full governance evaluation across the federation."""
    node_reports: list[dict[str, Any]] = []
    total_penalty = 0.0
    evaluable_policies = [p for p in policies if p.get("id") not in _RUNTIME_ONLY_POLICIES]

    all_nodes: list[CityRecord | AgentRecord] = [*registry.cities, *registry.agents]

    for node in all_nodes:
        violations, advisories = evaluate_node_compliance(node, policies)
        trust_score = compute_trust_score(node, violations)
        penalty = sum(v.get("trust_penalty", 0.0) for v in violations)
        total_penalty += penalty

        report: dict[str, Any] = {
            "node_id": _node_id(node),
            "node_type": _node_type(node),
            "trust_level": node.trust_level,
            "trust_score": trust_score,
            "violations": violations,
            "compliant": len(violations) == 0,
        }
        if advisories:
            report["advisories"] = advisories
        node_reports.append(report)

    compliant_count = sum(1 for r in node_reports if r["compliant"])
    total = len(node_reports)

    return {
        "evaluated_policies": len(evaluable_policies),
        "runtime_only_policies": len(policies) - len(evaluable_policies),
        "evaluated_nodes": total,
        "compliant_nodes": compliant_count,
        "non_compliant_nodes": total - compliant_count,
        "compliance_ratio": round(compliant_count / total, 2) if total else 0.0,
        "total_trust_penalty": round(total_penalty, 2),
        "nodes": node_reports,
    }
