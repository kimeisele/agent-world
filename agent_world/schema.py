"""Schema validation for world_registry.yaml.

Pure-Python validation — no extra dependencies beyond the stdlib.
Catches structural errors before they reach production.
"""

from __future__ import annotations

from typing import Any

# Valid values for constrained fields.
VALID_CITY_STATUSES = {"alive", "degraded", "offline"}
VALID_AGENT_STATUSES = {"active", "inactive", "suspended"}
VALID_TRUST_LEVELS = {"founding", "verified", "observed", "untrusted"}

KNOWN_CITY_CAPABILITIES = {
    "governance",
    "economy",
    "immigration",
    "code_execution",
    "federation_bridge",
}

KNOWN_AGENT_CAPABILITIES = {
    "authority_feed",
    "projection",
    "projection_host",
    "world_governance",
    "registry",
    "orchestration",
    "protocol_governance",
    "federation_tooling",
    "scaffolding",
    "testing",
    "governance",
    "code_execution",
    "descriptor_incomplete",
}


class RegistryValidationError(Exception):
    """Raised when the registry payload fails validation."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__(f"registry validation failed with {len(errors)} error(s): {'; '.join(errors)}")


def _check_required_str(item: dict[str, Any], key: str, path: str, errors: list[str]) -> None:
    val = item.get(key)
    if not isinstance(val, str) or not val.strip():
        errors.append(f"{path}.{key}: required non-empty string")


def _check_enum(item: dict[str, Any], key: str, allowed: set[str], path: str, errors: list[str]) -> None:
    val = item.get(key)
    if isinstance(val, str) and val not in allowed:
        errors.append(f"{path}.{key}: '{val}' not in {sorted(allowed)}")


def _check_capabilities(
    item: dict[str, Any], known: set[str], path: str, errors: list[str],
) -> None:
    caps = item.get("capabilities")
    if not isinstance(caps, list):
        errors.append(f"{path}.capabilities: must be a list")
        return
    if not caps:
        errors.append(f"{path}.capabilities: must not be empty")
    for cap in caps:
        if not isinstance(cap, str) or not cap.strip():
            errors.append(f"{path}.capabilities: entries must be non-empty strings")
        elif cap not in known:
            errors.append(f"{path}.capabilities: unknown capability '{cap}'")


def validate_registry(payload: dict[str, Any]) -> list[str]:
    """Validate a raw world_registry.yaml payload. Returns a list of error strings (empty = valid)."""
    errors: list[str] = []

    # -- world section --
    world = payload.get("world")
    if not isinstance(world, dict):
        errors.append("world: must be a mapping")
    else:
        for key in ("world_id", "origin_id", "steward_substrate", "public_projection"):
            _check_required_str(world, key, "world", errors)

    # -- cities section --
    cities = payload.get("cities")
    if cities is not None and not isinstance(cities, list):
        errors.append("cities: must be a list")
    else:
        seen_city_ids: set[str] = set()
        for i, city in enumerate(cities or []):
            path = f"cities[{i}]"
            if not isinstance(city, dict):
                errors.append(f"{path}: must be a mapping")
                continue
            for key in ("city_id", "repo", "status", "registered_at", "trust_level",
                        "federation_endpoint", "projection_source"):
                _check_required_str(city, key, path, errors)
            _check_enum(city, "status", VALID_CITY_STATUSES, path, errors)
            _check_enum(city, "trust_level", VALID_TRUST_LEVELS, path, errors)
            _check_capabilities(city, KNOWN_CITY_CAPABILITIES, path, errors)
            cid = city.get("city_id")
            if cid in seen_city_ids:
                errors.append(f"{path}.city_id: duplicate '{cid}'")
            elif isinstance(cid, str):
                seen_city_ids.add(cid)

    # -- agents section --
    agents = payload.get("agents")
    if agents is not None and not isinstance(agents, list):
        errors.append("agents: must be a list")
    else:
        seen_agent_ids: set[str] = set()
        for i, agent in enumerate(agents or []):
            path = f"agents[{i}]"
            if not isinstance(agent, dict):
                errors.append(f"{path}: must be a mapping")
                continue
            for key in ("agent_id", "repo", "status", "registered_at", "trust_level",
                        "owner_boundary"):
                _check_required_str(agent, key, path, errors)
            _check_enum(agent, "status", VALID_AGENT_STATUSES, path, errors)
            _check_enum(agent, "trust_level", VALID_TRUST_LEVELS, path, errors)
            _check_capabilities(agent, KNOWN_AGENT_CAPABILITIES, path, errors)
            aid = agent.get("agent_id")
            if aid in seen_agent_ids:
                errors.append(f"{path}.agent_id: duplicate '{aid}'")
            elif isinstance(aid, str):
                seen_agent_ids.add(aid)

    return errors


def validate_registry_or_raise(payload: dict[str, Any]) -> None:
    """Validate and raise ``RegistryValidationError`` if invalid."""
    errors = validate_registry(payload)
    if errors:
        raise RegistryValidationError(errors)
