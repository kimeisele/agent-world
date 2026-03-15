import json
from pathlib import Path

from agent_world.heartbeat import run_world_heartbeat


def test_world_heartbeat_writes_world_state(tmp_path):
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "world_state.json"

    path, state = run_world_heartbeat(base_path=root, output_path=output)

    assert path == output.resolve()
    assert state["version"] == 4
    assert state["summary"]["registered_cities"] == 1
    assert state["summary"]["founding_cities"] == 1
    assert state["summary"]["active_policies"] == 6  # 3 founding + 3 governance (CI, descriptor, devcontainer)

    # Warnings include missing heartbeat + descriptor_incomplete + policy violations
    assert "missing_last_heartbeat:agent-city" in state["warnings"]
    assert "descriptor_incomplete:agent-internet" in state["warnings"]
    assert "descriptor_incomplete:steward-federation" in state["warnings"]
    assert "descriptor_incomplete:steward-test" in state["warnings"]
    assert "descriptor_incomplete:steward-gateway" in state["warnings"]
    assert "policy_violation:agent-internet:federation_descriptor_required" in state["warnings"]
    assert "policy_violation:agent-internet:federation_ci_required" in state["warnings"]

    # Federation health section
    health = state["federation_health"]
    assert health["total_nodes"] == state["summary"]["total_nodes"]
    assert health["active_nodes"] >= 1
    assert health["descriptor_incomplete"] == 4  # agent-internet, steward-federation, steward-test, steward-gateway
    assert 0.0 <= health["health_ratio"] <= 1.0
    assert len(health["nodes"]) == health["total_nodes"]

    # Governance section
    gov = state["governance"]
    assert gov["evaluated_policies"] == 4  # 6 total - 2 runtime-only
    assert gov["runtime_only_policies"] == 2
    assert gov["evaluated_nodes"] == state["summary"]["total_nodes"]
    assert gov["non_compliant_nodes"] == 4  # agent-internet, steward-federation, steward-test, steward-gateway
    assert 0.0 <= gov["compliance_ratio"] <= 1.0
    assert gov["total_trust_penalty"] == 2.6  # 4 nodes * (0.3 + 0.2 + 0.15)

    # Verify trust scores are computed
    for node in gov["nodes"]:
        assert "trust_score" in node
        assert 0.0 <= node["trust_score"] <= 1.0

    # Capability index
    assert "authority_feed" in state["capability_index"]
    assert "world_governance" in state["capability_index"]
    assert "research_synthesis" in state["capability_index"]
    assert "agent-research" in state["capability_index"]["research_synthesis"]

    persisted = json.loads(output.read_text())
    assert persisted["world_id"] == "agent-world"
