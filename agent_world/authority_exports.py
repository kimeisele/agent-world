"""Authority export bundle generation for agent-world."""

from __future__ import annotations

import json
import subprocess
import time
from hashlib import sha256
from pathlib import Path
from typing import Any

from .config import load_yaml, repo_root
from .registry import load_world_registry

AGENT_WORLD_REPO_ID = "agent-world"
AGENT_WORLD_PUBLIC_WIKI_BINDING_ID = "agent-world-public-wiki"


def _document_specs() -> list[dict[str, str]]:
    return [
        {
            "document_id": "world_constitution",
            "title": "World Constitution",
            "wiki_name": "World-Constitution",
            "source_path": "docs/WORLD_CONSTITUTION.md",
            "section": "Foundations",
            "public_summary": "The constitutional baseline for world-level governance and boundaries.",
        },
        {
            "document_id": "world_registry",
            "title": "World Registry",
            "wiki_name": "World-Registry",
            "source_path": "config/world_registry.yaml",
            "section": "Registry",
            "public_summary": "The authoritative registry of known cities and their world-scoped standing.",
        },
        {
            "document_id": "world_policies",
            "title": "World Policies",
            "wiki_name": "World-Policies",
            "source_path": "config/world_policies.yaml",
            "section": "Policy",
            "public_summary": "Declared global policy rules that sit above any single city runtime.",
        },
        {
            "document_id": "repo_boundaries",
            "title": "Repo Boundaries",
            "wiki_name": "Repo-Boundaries",
            "source_path": "docs/REPO_BOUNDARIES.md",
            "section": "Boundary",
            "public_summary": "The verified responsibility split across steward-protocol, agent-world, agent-city, agent-internet, and steward.",
        },
        {
            "document_id": "cross_repo_roadmap",
            "title": "Cross Repo Roadmap",
            "wiki_name": "Cross-Repo-Roadmap",
            "source_path": "docs/CROSS_REPO_ROADMAP.md",
            "section": "Coordination",
            "public_summary": "The migration path for moving world semantics out of city-local contracts and into agent-world.",
        },
    ]


def _source_sha(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(root), text=True).strip() or "unknown"
    except Exception:
        return "unknown"


def _digest(payload: dict[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def export_canonical_surface(*, base_path: Path | None = None) -> dict[str, Any]:
    root = repo_root(base_path)
    documents: list[dict[str, Any]] = []
    for spec in _document_specs():
        source_path = str(spec["source_path"])
        documents.append(
            {
                **spec,
                "content": (root / source_path).read_text(),
            },
        )
    return {"kind": "canonical_surface", "repo_id": AGENT_WORLD_REPO_ID, "documents": documents}


def export_public_summary_registry(*, base_path: Path | None = None) -> dict[str, Any]:
    _ = repo_root(base_path)
    records = [
        {
            "id": spec["document_id"],
            "title": spec["title"],
            "wiki_name": spec["wiki_name"],
            "public_summary": spec["public_summary"],
        }
        for spec in _document_specs()
    ]
    return {"kind": "public_summary_registry", "repo_id": AGENT_WORLD_REPO_ID, "records": records}


def export_source_surface_registry(*, base_path: Path | None = None) -> dict[str, Any]:
    registry = load_world_registry(base_path=repo_root(base_path))
    documents = [
        {
            "document_id": spec["document_id"],
            "title": spec["title"],
            "wiki_name": spec["wiki_name"],
            "source_path": spec["source_path"],
            "section": spec["section"],
        }
        for spec in _document_specs()
    ]
    return {
        "kind": "source_surface_registry",
        "repo_id": registry.world_id,
        "document_count": len(documents),
        "documents": documents,
    }


def export_surface_metadata(*, base_path: Path | None = None) -> dict[str, Any]:
    root = repo_root(base_path)
    world_config = load_yaml("config/world.yaml", base_path=root).get("world") or {}
    registry_payload = export_source_surface_registry(base_path=root)
    return {
        "kind": "surface_metadata",
        "repo_id": AGENT_WORLD_REPO_ID,
        "world": world_config,
        "surface_registry": {
            "document_count": registry_payload["document_count"],
            "sections": sorted({str(record["section"]) for record in registry_payload["documents"]}),
        },
    }


def export_authority_bundle(*, base_path: Path | None = None, source_sha: str | None = None, generated_at: float | None = None) -> dict[str, Any]:
    root = repo_root(base_path)
    timestamp = float(time.time() if generated_at is None else generated_at)
    effective_source_sha = str(source_sha or _source_sha(root))
    artifacts = {
        "canonical_surface": (".authority-exports/canonical-surface.json", export_canonical_surface(base_path=root)),
        "public_summary_registry": (".authority-exports/public-summary-registry.json", export_public_summary_registry(base_path=root)),
        "source_surface_registry": (".authority-exports/source-surface-registry.json", export_source_surface_registry(base_path=root)),
        "surface_metadata": (".authority-exports/surface-metadata.json", export_surface_metadata(base_path=root)),
    }
    authority_exports = []
    artifact_paths = {}
    for export_kind, (artifact_uri, payload) in artifacts.items():
        artifact_paths[export_kind] = artifact_uri
        authority_exports.append(
            {
                "export_id": f"{AGENT_WORLD_REPO_ID}/{export_kind}",
                "repo_id": AGENT_WORLD_REPO_ID,
                "export_kind": export_kind,
                "version": effective_source_sha[:12] or "working-tree",
                "artifact_uri": artifact_uri,
                "generated_at": timestamp,
                "contract_version": 1,
                "content_sha256": _digest(payload),
                "labels": {"source_sha": effective_source_sha},
            },
        )
    return {
        "kind": "source_authority_bundle",
        "generated_at": timestamp,
        "source_sha": effective_source_sha,
        "repo_role": {
            "repo_id": AGENT_WORLD_REPO_ID,
            "role": "normative_source",
            "owner_boundary": "world_governance_surface",
            "exports": list(artifact_paths),
            "consumes": [],
            "publication_targets": [AGENT_WORLD_PUBLIC_WIKI_BINDING_ID],
            "labels": {"public_surface_owner": "agent-internet"},
        },
        "authority_exports": authority_exports,
        "artifact_paths": artifact_paths,
    }


def write_authority_bundle(*, base_path: Path | None = None, output_dir: Path | None = None, source_sha: str | None = None, generated_at: float | None = None) -> tuple[Path, dict[str, Any]]:
    root = repo_root(base_path)
    target_root = Path(output_dir).resolve() if output_dir is not None else root
    bundle = export_authority_bundle(base_path=root, source_sha=source_sha, generated_at=generated_at)
    exports_dir = target_root / ".authority-exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    for relative_path in bundle["artifact_paths"].values():
        artifact_payload = next(
            payload
            for payload in (
                export_canonical_surface(base_path=root),
                export_public_summary_registry(base_path=root),
                export_source_surface_registry(base_path=root),
                export_surface_metadata(base_path=root),
            )
            if relative_path.endswith(payload["kind"].replace("_", "-") + ".json")
        )
        target = target_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(artifact_payload, indent=2, sort_keys=True) + "\n")
    bundle_path = target_root / ".authority-export-bundle.json"
    bundle_path.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n")
    return bundle_path, bundle