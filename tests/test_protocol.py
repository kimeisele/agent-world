from agent_world.protocol import CityReport, FederationDirective


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
