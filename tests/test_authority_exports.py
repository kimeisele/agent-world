import json
from pathlib import Path

from agent_world.authority_exports import AGENT_WORLD_PUBLIC_WIKI_BINDING_ID, export_authority_bundle, write_authority_bundle


def test_export_authority_bundle_has_world_contract_shape():
    root = Path(__file__).resolve().parents[1]
    bundle = export_authority_bundle(base_path=root, source_sha="abc123", generated_at=123.0)

    assert bundle["kind"] == "source_authority_bundle"
    assert bundle["repo_role"]["repo_id"] == "agent-world"
    assert bundle["repo_role"]["publication_targets"] == [AGENT_WORLD_PUBLIC_WIKI_BINDING_ID]
    assert sorted(bundle["artifact_paths"]) == [
        "canonical_surface",
        "public_summary_registry",
        "source_surface_registry",
        "surface_metadata",
    ]
    assert bundle["authority_exports"][0]["labels"]["source_sha"] == "abc123"


def test_write_authority_bundle_materializes_artifacts(tmp_path):
    root = Path(__file__).resolve().parents[1]
    bundle_path, bundle = write_authority_bundle(base_path=root, output_dir=tmp_path, source_sha="def456", generated_at=456.0)

    assert bundle_path == (tmp_path / ".authority-export-bundle.json").resolve()
    canonical = json.loads((tmp_path / ".authority-exports" / "canonical-surface.json").read_text())
    registry = json.loads((tmp_path / ".authority-exports" / "source-surface-registry.json").read_text())
    metadata = json.loads((tmp_path / ".authority-exports" / "surface-metadata.json").read_text())
    persisted_bundle = json.loads(bundle_path.read_text())

    assert canonical["kind"] == "canonical_surface"
    assert any(document["document_id"] == "world_constitution" for document in canonical["documents"])
    assert canonical["documents"][0]["labels"]["source_role"] == "entrypoint"
    assert registry["document_count"] == 5
    assert registry["documents"][0]["authority"] == "binding"
    assert metadata["public_surface"]["overview_page"]["wiki_name"] == "Agent-World-Authority"
    assert metadata["surface_registry"]["pages"][0]["include_in_sidebar"] is True
    assert persisted_bundle["source_sha"] == "def456"
    assert bundle["repo_role"]["owner_boundary"] == "world_governance_surface"