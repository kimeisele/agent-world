import json
from pathlib import Path

from agent_world.heartbeat import run_world_heartbeat


def test_world_heartbeat_writes_world_state(tmp_path):
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "world_state.json"

    path, state = run_world_heartbeat(base_path=root, output_path=output)

    assert path == output.resolve()
    assert state["version"] == 3
    assert state["summary"]["registered_cities"] == 1
    assert state["summary"]["founding_cities"] == 1
    assert state["summary"]["active_policies"] == 5  # 3 founding + 2 governance (CI, descriptor)

    # Warnings include missing heartbeat + descriptor_incomplete agents
    assert "missing_last_heartbeat:agent-city" in state["warnings"]
    assert "descriptor_incomplete:agent-internet" in state["warnings"]
    assert "descriptor_incomplete:steward-federation" in state["warnings"]
    assert "descriptor_incomplete:steward-test" in state["warnings"]

    # Federation health section
    health = state["federation_health"]
    assert health["total_nodes"] == state["summary"]["total_nodes"]
    assert health["active_nodes"] >= 1
    assert health["descriptor_incomplete"] == 3  # agent-internet, steward-federation, steward-test
    assert 0.0 <= health["health_ratio"] <= 1.0
    assert len(health["nodes"]) == health["total_nodes"]

    # Capability index
    assert "authority_feed" in state["capability_index"]
    assert "world_governance" in state["capability_index"]

    persisted = json.loads(output.read_text())
    assert persisted["world_id"] == "agent-world"
