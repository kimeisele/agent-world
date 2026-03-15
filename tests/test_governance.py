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
    violations = evaluate_node_compliance(agent, _policies())
    assert violations == []


def test_descriptor_incomplete_node_has_violation():
    registry = load_world_registry(base_path=_root())
    agent = registry.agent_by_id("agent-internet")  # descriptor_incomplete
    violations = evaluate_node_compliance(agent, _policies())
    assert len(violations) == 1
    assert violations[0]["policy_id"] == "federation_descriptor_required"
    assert violations[0]["trust_penalty"] == 0.3


def test_trust_score_with_penalty():
    registry = load_world_registry(base_path=_root())
    agent = registry.agent_by_id("agent-internet")  # observed (base 0.5) - 0.3 penalty
    violations = evaluate_node_compliance(agent, _policies())
    score = compute_trust_score(agent, violations)
    assert score == 0.2


def test_trust_score_without_penalty():
    registry = load_world_registry(base_path=_root())
    agent = registry.agent_by_id("agent-world")  # observed (base 0.5), no violations
    violations = evaluate_node_compliance(agent, _policies())
    score = compute_trust_score(agent, violations)
    assert score == 0.5


def test_founding_city_trust_score():
    registry = load_world_registry(base_path=_root())
    city = registry.city_by_id("agent-city")  # founding (base 1.0), no violations
    violations = evaluate_node_compliance(city, _policies())
    score = compute_trust_score(city, violations)
    assert score == 1.0


def test_federation_governance_report():
    registry = load_world_registry(base_path=_root())
    policies = _policies()
    report = evaluate_federation_governance(registry, policies)

    assert report["evaluated_policies"] == 5
    assert report["evaluated_nodes"] == 9  # 1 city + 8 agents
    assert report["non_compliant_nodes"] == 3  # agent-internet, steward-federation, steward-test
    assert report["compliant_nodes"] == 6
    assert report["compliance_ratio"] == round(6 / 9, 2)
    assert report["total_trust_penalty"] == 0.9  # 3 nodes * 0.3 each
