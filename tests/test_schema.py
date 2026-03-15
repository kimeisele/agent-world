import copy
from pathlib import Path

import yaml

from agent_world.schema import RegistryValidationError, validate_registry, validate_registry_or_raise


def _load_registry():
    root = Path(__file__).resolve().parents[1]
    return yaml.safe_load((root / "config/world_registry.yaml").read_text())


def test_checked_in_registry_is_valid():
    payload = _load_registry()
    errors = validate_registry(payload)
    assert errors == [], errors


def test_missing_world_section():
    payload = _load_registry()
    del payload["world"]
    errors = validate_registry(payload)
    assert any("world: must be a mapping" in e for e in errors)


def test_duplicate_agent_id():
    payload = _load_registry()
    dup = copy.deepcopy(payload["agents"][0])
    payload["agents"].append(dup)
    errors = validate_registry(payload)
    assert any("duplicate" in e for e in errors)


def test_unknown_capability():
    payload = _load_registry()
    payload["agents"][0]["capabilities"] = ["teleportation"]
    errors = validate_registry(payload)
    assert any("unknown capability 'teleportation'" in e for e in errors)


def test_empty_capabilities_rejected():
    payload = _load_registry()
    payload["agents"][0]["capabilities"] = []
    errors = validate_registry(payload)
    assert any("must not be empty" in e for e in errors)


def test_invalid_status():
    payload = _load_registry()
    payload["agents"][0]["status"] = "exploded"
    errors = validate_registry(payload)
    assert any("not in" in e for e in errors)


def test_validate_or_raise_raises():
    payload = _load_registry()
    del payload["world"]
    try:
        validate_registry_or_raise(payload)
        assert False, "should have raised"
    except RegistryValidationError as exc:
        assert len(exc.errors) >= 1
