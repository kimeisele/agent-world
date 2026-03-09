# agent-world

Authoritative world-governance seam for the Agent ecosystem.

`agent-world` exists because `agent-city` should not declare itself to be the whole world, `steward-protocol` should remain substrate rather than world policy runtime, and `agent-internet` should project public membrane state rather than own governance truth.

## Boundary

- **steward-protocol** — substrate: kernel, identity primitives, capability enforcement, Nadi primitives
- **agent-world** — world truth: registry, policies, world contracts, heartbeat aggregation, world audit direction
- **agent-city** — local runtime: mayor, council, economy, immigration, local campaigns
- **agent-internet** — projection/public membrane: public docs, graph/wiki rendering, publication
- **steward / steward-agent** — optional world/operator superagent; may serve the repos, but does not define world truth

## Founding Scope

This founding repo intentionally starts thin:

- `config/world.yaml` — world identity and heartbeat settings
- `config/world_registry.yaml` — authoritative city registry
- `config/world_policies.yaml` — global policy declarations
- `docs/WORLD_CONSTITUTION.md` — world-level governance baseline
- `schemas/` — first shared protocol payload contracts
- `agent_world/heartbeat.py` — minimal world heartbeat that aggregates registry + policy state into `data/world_state.json`

What is **not** here yet:

- full live transport routing daemon
- socket / HTTP inter-city runtime
- identity federation engine
- conflict-resolution automation
- heavy multi-city campaign execution

Those follow only after the contract boundary is stable.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
agent-world heartbeat
pytest -q
```

## Initial Repository Layout

- `agent_world/` — Python package
- `config/` — world identity, registry, policy config
- `campaigns/` — standing world campaign declarations
- `docs/` — constitution and repo-boundary docs
- `schemas/` — shared protocol schemas
- `scripts/` — convenience entrypoints
- `tests/` — focused founding tests

## Near-Term Roadmap

1. Move world truth out of `agent-city`
2. Repoint `agent-internet` world projections to `agent-world`
3. Convert city federation from implicit mothership assumptions to world-registry-driven contracts
4. Let `steward` (package: `steward-agent`) serve world-approved workflows rather than define the world itself
