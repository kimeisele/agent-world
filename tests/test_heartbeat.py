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
    assert state["summary"]["active_policies"] == 5  # 3 founding + 2 governance (CI, descriptor)

    # Warnings include missing heartbeat + descriptor_incomplete + policy violations
    assert "missing_last_heartbeat:agent-city" in state["warnings"]
    assert "descriptor_incomplete:agent-internet" in state["warnings"]
    assert "descriptor_incomplete:steward-federation" in state["warnings"]
    assert "descriptor_incomplete:steward-test" in state["warnings"]
    assert "policy_violation:agent-internet:federation_descriptor_required" in state["warnings"]

    # Federation health section
    health = state["federation_health"]
    assert health["total_nodes"] == state["summary"]["total_nodes"]
    assert health["active_nodes"] >= 1
    assert health["descriptor_incomplete"] == 3
    assert 0.0 <= health["health_ratio"] <= 1.0
    assert len(health["nodes"]) == health["total_nodes"]

    # Governance section
    gov = state["governance"]
    assert gov["evaluated_policies"] == 5
    assert gov["evaluated_nodes"] == state["summary"]["total_nodes"]
    assert gov["non_compliant_nodes"] == 3  # agent-internet, steward-federation, steward-test
    assert 0.0 <= gov["compliance_ratio"] <= 1.0
    assert gov["total_trust_penalty"] > 0

    # Verify trust scores are computed
    for node in gov["nodes"]:
        assert "trust_score" in node
        assert 0.0 <= node["trust_score"] <= 1.0

    # Capability index
    assert "authority_feed" in state["capability_index"]
    assert "world_governance" in state["capability_index"]

    persisted = json.loads(output.read_text())
    assert persisted["world_id"] == "agent-world"
