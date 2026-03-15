import json
from pathlib import Path

from agent_world.heartbeat import run_world_heartbeat


def test_world_heartbeat_writes_world_state(tmp_path):
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "world_state.json"

    path, state = run_world_heartbeat(base_path=root, output_path=output)

    assert path == output.resolve()
    assert state["summary"]["registered_cities"] == 1
    assert state["summary"]["founding_cities"] == 1
    assert state["summary"]["active_policies"] == 5  # 3 founding + 2 governance (CI, descriptor)
    assert state["warnings"] == ["missing_last_heartbeat:agent-city"]
    persisted = json.loads(output.read_text())
    assert persisted["world_id"] == "agent-world"
