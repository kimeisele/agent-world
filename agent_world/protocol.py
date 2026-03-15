"""Founding world-level protocol payloads with boundary validation.

These are the contracts at the system boundary — where agent-city talks
to agent-world.  Every field is validated because this is the exact point
where garbage enters the federation if we don't enforce.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Constraints absorbed from the (formerly dead) JSON schemas in schemas/.
VALID_CITY_REPORT_STATUSES = {"alive", "dormant", "degraded", "suspended"}
VALID_DIRECTIVE_TYPES = {"campaign_sync", "policy_update", "trust_update", "heartbeat_request"}


class ProtocolValidationError(Exception):
    """Raised when a protocol payload fails boundary validation."""

    def __init__(self, contract: str, errors: list[str]) -> None:
        self.contract = contract
        self.errors = errors
        super().__init__(f"{contract} validation failed: {'; '.join(errors)}")


def _require_nonempty_str(value: Any, name: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{name}: required non-empty string")


@dataclass(frozen=True, slots=True)
class CityReport:
    city_id: str
    reported_at_utc: str
    status: str
    summary: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        errors: list[str] = []
        _require_nonempty_str(self.city_id, "city_id", errors)
        _require_nonempty_str(self.reported_at_utc, "reported_at_utc", errors)
        _require_nonempty_str(self.status, "status", errors)
        if isinstance(self.status, str) and self.status not in VALID_CITY_REPORT_STATUSES:
            errors.append(f"status: '{self.status}' not in {sorted(VALID_CITY_REPORT_STATUSES)}")
        if not isinstance(self.summary, dict):
            errors.append("summary: must be a dict")
        if errors:
            raise ProtocolValidationError("CityReport", errors)

    def to_payload(self) -> dict[str, Any]:
        return {
            "city_id": self.city_id,
            "reported_at_utc": self.reported_at_utc,
            "status": self.status,
            "summary": dict(self.summary),
        }


@dataclass(frozen=True, slots=True)
class FederationDirective:
    directive_id: str
    target_city_id: str
    directive_type: str
    issued_at_utc: str
    payload: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        errors: list[str] = []
        _require_nonempty_str(self.directive_id, "directive_id", errors)
        _require_nonempty_str(self.target_city_id, "target_city_id", errors)
        _require_nonempty_str(self.directive_type, "directive_type", errors)
        _require_nonempty_str(self.issued_at_utc, "issued_at_utc", errors)
        if isinstance(self.directive_type, str) and self.directive_type not in VALID_DIRECTIVE_TYPES:
            errors.append(f"directive_type: '{self.directive_type}' not in {sorted(VALID_DIRECTIVE_TYPES)}")
        if not isinstance(self.payload, dict):
            errors.append("payload: must be a dict")
        if errors:
            raise ProtocolValidationError("FederationDirective", errors)

    def to_payload(self) -> dict[str, Any]:
        return {
            "directive_id": self.directive_id,
            "target_city_id": self.target_city_id,
            "directive_type": self.directive_type,
            "issued_at_utc": self.issued_at_utc,
            "payload": dict(self.payload),
        }
