from pathlib import Path

from agent_world.registry import load_world_registry


def test_load_world_registry_checked_in_repo():
    root = Path(__file__).resolve().parents[1]
    registry = load_world_registry(base_path=root)

    assert registry.world_id == "agent-world"
    assert registry.public_projection == "kimeisele/agent-internet"
    assert len(registry.cities) == 1
    city = registry.city_by_id("agent-city")
    assert city.status == "alive"
    assert "governance" in city.capabilities
