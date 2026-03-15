from pathlib import Path

import yaml

from agent_world.governance import (
    compute_trust_score,
    evaluate_federation_governance,
    evaluate_node_compliance,
)
from agent_world.registry import load_world_registry


def _root():
    return Path(__file__).resolve().parents[1]


def _policies():
    return yaml.safe_load((_root() / "config/world_policies.yaml").read_text()).get("policies", [])


def test_compliant_node_has_no_violations():
    registry = load_world_registry(base_path=_root())
    agent = registry.agent_by_id("agent-world")  # has full descriptor
    violations, advisories = evaluate_node_compliance(agent, _policies())
    assert violations == []
    assert advisories == []


def test_descriptor_incomplete_node_gets_all_violations():
    registry = load_world_registry(base_path=_root())
    agent = registry.agent_by_id("agent-internet")  # descriptor_incomplete
    violations, advisories = evaluate_node_compliance(agent, _policies())
    policy_ids = {v["policy_id"] for v in violations}
    # descriptor_incomplete triggers descriptor + CI + devcontainer violations
    assert "federation_descriptor_required" in policy_ids
    assert "federation_ci_required" in policy_ids
    assert "federation_devcontainer_required" in policy_ids
    assert len(violations) == 3


def test_trust_score_with_both_penalties():
    registry = load_world_registry(base_path=_root())
    agent = registry.agent_by_id("agent-internet")  # observed (0.5) - 0.3 - 0.2 = 0.0
    violations, _ = evaluate_node_compliance(agent, _policies())
    score = compute_trust_score(agent, violations)
    assert score == 0.0


def test_trust_score_without_penalty():
    registry = load_world_registry(base_path=_root())
    agent = registry.agent_by_id("agent-world")  # founding (base 1.0), no violations
    violations, _ = evaluate_node_compliance(agent, _policies())
    score = compute_trust_score(agent, violations)
    assert score == 1.0


def test_founding_city_trust_score():
    registry = load_world_registry(base_path=_root())
    city = registry.city_by_id("agent-city")  # founding (base 1.0), no violations
    violations, advisories = evaluate_node_compliance(city, _policies())
    score = compute_trust_score(city, violations)
    assert score == 1.0
    assert violations == []
    # Founding city has trust >= verified, so no visa advisory
    assert advisories == []


def test_federation_governance_report():
    registry = load_world_registry(base_path=_root())
    policies = _policies()
    report = evaluate_federation_governance(registry, policies)

    assert report["evaluated_policies"] == 4  # 6 total - 2 runtime-only
    assert report["runtime_only_policies"] == 2  # city_autonomy_limits, bandwidth_quota
    assert report["evaluated_nodes"] == 11  # 1 city + 10 agents
    assert report["non_compliant_nodes"] == 4  # agent-internet, steward-federation, steward-test, steward-gateway
    assert report["compliant_nodes"] == 7
    assert report["compliance_ratio"] == round(7 / 11, 2)
    # 4 nodes * (0.3 descriptor + 0.2 CI + 0.15 devcontainer) = 2.6
    assert report["total_trust_penalty"] == 2.6
