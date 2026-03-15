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
AUTHORITY_FEED_CONTRACT_VERSION = 1


def _document_specs() -> list[dict[str, Any]]:
    return [
        {
            "document_id": "world_constitution",
            "title": "World Constitution",
            "wiki_name": "World-Constitution",
            "source_path": "docs/WORLD_CONSTITUTION.md",
            "authority": "binding",
            "domain": "governance",
            "section": "Foundations",
            "public_summary": "The constitutional baseline for world-level governance and boundaries.",
            "labels": {
                "source_kind": "markdown",
                "source_role": "entrypoint",
                "include_in_sidebar": "true",
                "featured": "true",
                "nav_label": "World Constitution",
            },
        },
        {
            "document_id": "world_registry",
            "title": "World Registry",
            "wiki_name": "World-Registry",
            "source_path": "config/world_registry.yaml",
            "authority": "reference",
            "domain": "registry",
            "section": "Registry",
            "public_summary": "The authoritative registry of known cities and their world-scoped standing.",
            "labels": {"source_kind": "yaml", "include_in_sidebar": "true", "nav_label": "World Registry"},
        },
        {
            "document_id": "world_policies",
            "title": "World Policies",
            "wiki_name": "World-Policies",
            "source_path": "config/world_policies.yaml",
            "authority": "binding",
            "domain": "policy",
            "section": "Policy",
            "public_summary": "Declared global policy rules that sit above any single city runtime.",
            "labels": {"source_kind": "yaml", "nav_label": "World Policies"},
        },
        {
            "document_id": "repo_boundaries",
            "title": "Repo Boundaries",
            "wiki_name": "Repo-Boundaries",
            "source_path": "docs/REPO_BOUNDARIES.md",
            "authority": "reference",
            "domain": "boundary",
            "section": "Boundary",
            "public_summary": "The verified responsibility split across steward-protocol, agent-world, agent-city, agent-internet, and steward.",
            "labels": {"source_kind": "markdown", "include_in_sidebar": "true", "nav_label": "Repo Boundaries"},
        },
        {
            "document_id": "cross_repo_roadmap",
            "title": "Cross Repo Roadmap",
            "wiki_name": "Cross-Repo-Roadmap",
            "source_path": "docs/CROSS_REPO_ROADMAP.md",
            "authority": "operative",
            "domain": "coordination",
            "section": "Coordination",
            "public_summary": "The migration path for moving world semantics out of city-local contracts and into agent-world.",
            "labels": {"source_kind": "markdown", "nav_label": "Cross Repo Roadmap"},
        },
    ]


def _source_sha(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(root), text=True).strip() or "unknown"
    except Exception:
        return "unknown"


def _digest(payload: dict[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> str:
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered)
    return sha256(rendered.encode("utf-8")).hexdigest()


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
            "document_id": spec["document_id"],
            "title": spec["title"],
            "wiki_name": spec["wiki_name"],
            "authority": spec["authority"],
            "domain": spec["domain"],
            "source_path": spec["source_path"],
            "public_summary": spec["public_summary"],
            "labels": dict(spec["labels"]),
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
            "authority": spec["authority"],
            "domain": spec["domain"],
            "section": spec["section"],
            "public_abstract": spec["public_summary"],
            "labels": dict(spec["labels"]),
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
        "public_surface": {
            "repo_label": "Agent World",
            "document_prefix": "agent_world",
            "overview_page": {
                "document_id": "agent_world_authority",
                "rel": "agent_world_authority",
                "kind": "agent_world_authority",
                "title": "Agent World Authority",
                "wiki_name": "Agent-World-Authority",
                "entrypoint": True,
            },
            "canonical_index_page": {
                "document_id": "agent_world_canonical_surface",
                "rel": "agent_world_canonical_surface",
                "kind": "agent_world_canonical_surface",
                "title": "Agent World Canonical Surface",
                "wiki_name": "Agent-World-Canonical-Surface",
                "entrypoint": False,
            },
        },
        "federation_surface": {
            "surface_role": "canonical_public_source_authority",
            "canonical_for_public_federation": True,
            "publication_model": "github_authority_feed_plus_projected_wiki",
            "public_channels": ["authority_feed_manifest", "canonical_surface", "public_summary_registry"],
            "operator_companion_surfaces": ["world_heartbeat_operator_plane"],
            "consumer_guidance": "Treat this authority feed and its projected wiki pages as public federation truth; authenticated control planes are companion operator surfaces.",
        },
        "surface_registry": {
            "document_count": registry_payload["document_count"],
            "sections": sorted({str(record["section"]) for record in registry_payload["documents"]}),
            "pages": [
                {
                    "id": spec["document_id"],
                    "title": spec["title"],
                    "wiki_name": spec["wiki_name"],
                    "filename": f"{spec['wiki_name']}.md",
                    "page_class": "canonical",
                    "authority": spec["authority"],
                    "domain": spec["domain"],
                    "section": spec["section"],
                    "public_summary": spec["public_summary"],
                    "featured": spec["labels"].get("featured") == "true",
                    "include_in_sidebar": spec["labels"].get("include_in_sidebar") == "true",
                    "query_aliases": [],
                }
                for spec in _document_specs()
            ],
        },
    }


def _compute_artifact_payloads(root: Path) -> dict[str, tuple[str, dict[str, Any]]]:
    """Compute all 4 export payloads exactly once. Returns {kind: (relative_path, payload)}."""
    return {
        "canonical_surface": (".authority-exports/canonical-surface.json", export_canonical_surface(base_path=root)),
        "public_summary_registry": (".authority-exports/public-summary-registry.json", export_public_summary_registry(base_path=root)),
        "source_surface_registry": (".authority-exports/source-surface-registry.json", export_source_surface_registry(base_path=root)),
        "surface_metadata": (".authority-exports/surface-metadata.json", export_surface_metadata(base_path=root)),
    }


def export_authority_bundle(*, base_path: Path | None = None, source_sha: str | None = None, generated_at: float | None = None) -> dict[str, Any]:
    root = repo_root(base_path)
    timestamp = float(time.time() if generated_at is None else generated_at)
    effective_source_sha = str(source_sha or _source_sha(root))
    artifacts = _compute_artifact_payloads(root)
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


def _write_bundle_artifacts(
    target_root: Path, root: Path, bundle: dict[str, Any],
) -> None:
    """Write the 4 export artifacts using a single computation pass."""
    payloads = _compute_artifact_payloads(root)
    for _kind, (relative_path, payload) in payloads.items():
        target = target_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_authority_bundle(*, base_path: Path | None = None, output_dir: Path | None = None, source_sha: str | None = None, generated_at: float | None = None) -> tuple[Path, dict[str, Any]]:
    root = repo_root(base_path)
    target_root = Path(output_dir).resolve() if output_dir is not None else root
    bundle = export_authority_bundle(base_path=root, source_sha=source_sha, generated_at=generated_at)
    _write_bundle_artifacts(target_root, root, bundle)
    bundle_path = target_root / ".authority-export-bundle.json"
    bundle_path.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n")
    return bundle_path, bundle


def write_authority_feed(*, base_path: Path | None = None, output_dir: Path | None = None, source_sha: str | None = None, generated_at: float | None = None) -> tuple[Path, dict[str, Any]]:
    root = repo_root(base_path)
    target_root = Path(output_dir).resolve() if output_dir is not None else root / ".authority-feed"
    bundle = export_authority_bundle(base_path=root, source_sha=source_sha, generated_at=generated_at)
    effective_source_sha = str(bundle.get("source_sha", "")).strip() or "working-tree"
    bundle_root = target_root / "bundles" / effective_source_sha
    payloads = _compute_artifact_payloads(root)
    artifacts_manifest: dict[str, dict[str, str]] = {}
    for kind, (relative_path, payload) in payloads.items():
        file_sha = _write_json(bundle_root / relative_path, payload)
        artifacts_manifest[relative_path] = {
            "path": str(Path("bundles") / effective_source_sha / relative_path),
            "sha256": file_sha,
            "export_kind": kind,
        }
    bundle_path = bundle_root / "source-authority-bundle.json"
    bundle_sha = _write_json(bundle_path, bundle)
    manifest = {
        "kind": "source_authority_feed_manifest",
        "contract_version": AUTHORITY_FEED_CONTRACT_VERSION,
        "generated_at": bundle["generated_at"],
        "source_repo_id": AGENT_WORLD_REPO_ID,
        "source_sha": effective_source_sha,
        "bundle": {
            "path": str(Path("bundles") / effective_source_sha / "source-authority-bundle.json"),
            "sha256": bundle_sha,
            "kind": "source_authority_bundle",
        },
        "artifacts": artifacts_manifest,
    }
    manifest_path = target_root / "latest-authority-manifest.json"
    _write_json(manifest_path, manifest)
    return manifest_path, manifest