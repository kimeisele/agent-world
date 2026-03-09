"""Founding world-level protocol payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class CityReport:
    city_id: str
    reported_at_utc: str
    status: str
    summary: dict[str, Any] = field(default_factory=dict)

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

    def to_payload(self) -> dict[str, Any]:
        return {
            "directive_id": self.directive_id,
            "target_city_id": self.target_city_id,
            "directive_type": self.directive_type,
            "issued_at_utc": self.issued_at_utc,
            "payload": dict(self.payload),
        }
