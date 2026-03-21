"""CLI entrypoints for agent-world."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .authority_exports import write_authority_bundle, write_authority_feed
from .heartbeat import run_world_heartbeat


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent-world")
    subparsers = parser.add_subparsers(dest="command", required=True)
    heartbeat = subparsers.add_parser("heartbeat", help="aggregate world state")
    heartbeat.add_argument("--repo-root", type=Path, default=None)
    heartbeat.add_argument("--output", type=Path, default=None)
    export_bundle = subparsers.add_parser("export-authority-bundle", help="write world authority export artifacts and bundle")
    export_bundle.add_argument("--repo-root", type=Path, default=None)
    export_bundle.add_argument("--output-dir", type=Path, default=None)
    export_feed = subparsers.add_parser("export-authority-feed", help="write a versioned authority feed manifest plus bundle artifacts")
    export_feed.add_argument("--repo-root", type=Path, default=None)
    export_feed.add_argument("--output-dir", type=Path, default=None)
    subparsers.add_parser("sync", help="run NADI federation sync cycle")
    subparsers.add_parser("federation-status", help="show federation NADI status")
    args = parser.parse_args(argv)
    if args.command == "heartbeat":
        path, state = run_world_heartbeat(base_path=args.repo_root, output_path=args.output)
        health = state.get("federation_health", {})
        gov = state.get("governance", {})
        print(json.dumps({
            "output": str(path),
            "summary": state["summary"],
            "federation_health": {
                "health_ratio": health.get("health_ratio"),
                "active_nodes": health.get("active_nodes"),
                "descriptor_incomplete": health.get("descriptor_incomplete"),
            },
            "governance": {
                "compliance_ratio": gov.get("compliance_ratio"),
                "non_compliant_nodes": gov.get("non_compliant_nodes"),
                "total_trust_penalty": gov.get("total_trust_penalty"),
            },
            "warnings": state["warnings"],
        }, indent=2))
        return 0
    if args.command == "export-authority-bundle":
        path, bundle = write_authority_bundle(base_path=args.repo_root, output_dir=args.output_dir)
        print(json.dumps({"output": str(path), "repo_id": bundle["repo_role"]["repo_id"], "exports": [record["export_kind"] for record in bundle["authority_exports"]]}, indent=2))
        return 0
    if args.command == "export-authority-feed":
        path, manifest = write_authority_feed(base_path=args.repo_root, output_dir=args.output_dir)
        print(json.dumps({"output": str(path), "repo_id": manifest["source_repo_id"], "source_sha": manifest["source_sha"]}, indent=2))
        return 0
    if args.command == "sync":
        from .federation import create_world_node

        node = create_world_node()
        stats = node.sync()
        print(json.dumps(stats, indent=2))
        return 0
    if args.command == "federation-status":
        from .federation import create_world_node

        node = create_world_node()
        stats = node.stats()
        print(json.dumps(stats, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
