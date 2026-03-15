import copy
from pathlib import Path

import yaml

from agent_world.schema import (
    PolicyValidationError,
    RegistryValidationError,
    validate_policies,
    validate_policies_or_raise,
    validate_registry,
    validate_registry_or_raise,
)


def _load_registry():
    root = Path(__file__).resolve().parents[1]
    return yaml.safe_load((root / "config/world_registry.yaml").read_text())


def _load_policies():
    root = Path(__file__).resolve().parents[1]
    return yaml.safe_load((root / "config/world_policies.yaml").read_text())


# ---------------------------------------------------------------------------
# Registry validation
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Policy validation
# ---------------------------------------------------------------------------
def test_checked_in_policies_are_valid():
    payload = _load_policies()
    errors = validate_policies(payload)
    assert errors == [], errors


def test_missing_policies_key():
    errors = validate_policies({"other": True})
    assert any("policies: must be a list" in e for e in errors)


def test_policy_missing_required_fields():
    payload = {"policies": [{"enforcement": "declarative"}]}
    errors = validate_policies(payload)
    assert any("id: required" in e for e in errors)
    assert any("rule: required" in e for e in errors)


def test_policy_invalid_enforcement():
    payload = _load_policies()
    payload["policies"][0]["enforcement"] = "magic"
    errors = validate_policies(payload)
    assert any("not in" in e for e in errors)


def test_policy_trust_penalty_missing_value():
    payload = {"policies": [{"id": "test", "rule": "x", "enforcement": "trust_penalty"}]}
    errors = validate_policies(payload)
    assert any("trust_penalty: required" in e for e in errors)


def test_policy_duplicate_id():
    payload = _load_policies()
    dup = copy.deepcopy(payload["policies"][0])
    payload["policies"].append(dup)
    errors = validate_policies(payload)
    assert any("duplicate" in e for e in errors)


def test_validate_policies_or_raise():
    try:
        validate_policies_or_raise({"not_policies": []})
        assert False, "should have raised"
    except PolicyValidationError as exc:
        assert len(exc.errors) >= 1
