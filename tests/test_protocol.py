import pytest

from agent_world.protocol import CityReport, FederationDirective, ProtocolValidationError


def test_protocol_payload_shapes_are_stable():
    report = CityReport(
        city_id="agent-city",
        reported_at_utc="2026-03-09T00:00:00+00:00",
        status="alive",
        summary={"agents": 3},
    )
    directive = FederationDirective(
        directive_id="dir-001",
        target_city_id="agent-city",
        directive_type="campaign_sync",
        issued_at_utc="2026-03-09T00:05:00+00:00",
        payload={"campaign_id": "world_infrastructure_v1"},
    )

    assert report.to_payload()["summary"]["agents"] == 3
    assert directive.to_payload()["directive_type"] == "campaign_sync"


def test_city_report_rejects_invalid_status():
    with pytest.raises(ProtocolValidationError, match="CityReport"):
        CityReport(city_id="x", reported_at_utc="2026-01-01", status="exploded")


def test_city_report_rejects_empty_city_id():
    with pytest.raises(ProtocolValidationError, match="city_id"):
        CityReport(city_id="", reported_at_utc="2026-01-01", status="alive")


def test_directive_rejects_invalid_type():
    with pytest.raises(ProtocolValidationError, match="directive_type"):
        FederationDirective(
            directive_id="d1", target_city_id="c1",
            directive_type="nuke_city", issued_at_utc="2026-01-01",
        )


def test_directive_rejects_empty_fields():
    with pytest.raises(ProtocolValidationError, match="FederationDirective"):
        FederationDirective(
            directive_id="", target_city_id="c1",
            directive_type="campaign_sync", issued_at_utc="2026-01-01",
        )
