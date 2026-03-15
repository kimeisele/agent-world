# Repo Boundaries

**Last audited**: 2026-03-15 (code-level review of all repos)

## Verified Boundary

| Repo | Role | Code Reality | Owns | Does NOT own |
| --- | --- | --- | --- | --- |
| `agent-world` | **World Governance** | 8 modules, 30 tests, clean | registry, policy, constitution, heartbeat, authority exports, campaigns | agent execution, substrate, projection, city runtime |
| `steward` | **Autonomous Engine** | 168 files, 589 classes, 31 services | autonomous execution (CLI/REPL/daemon/bot/API), self-healing, federation participation, multi-LLM orchestration | world truth, registry, protocol definitions, projection |
| `steward-protocol` | **Substrate** | 126+ items, 73+ protocol files | identity, capability types, Nadi protocol spec, federation descriptor schema | who is registered, policy decisions, runtime execution |
| `agent-internet` | **Control Plane + Projection** | 67 modules, 1,125-line control plane | routing, trust, city registration, wiki/search/crawling, bundle projection | source truth, governance, city data |
| `agent-city` | **City Runtime** | Full runtime, 20 agents | mayor, council, economy, immigration, local campaigns, Pokedex | world truth, global policy, projection, substrate |
| `agent-template` | **Scaffolding** | 9 scripts, 4 days old | federation node wizard, descriptor generation | runtime, governance, active participation |
| `agent-research` | **Research Faculty** | 8 modules, day-zero | research pipeline (4-phase), inquiry system | governance decisions, implementation, world truth |
| `steward-federation` | **Nadi Mailbox** | 0 code files, 2 JSON files | git-backed message drop-box | transport logic (lives in steward), protocol, content authority |
| `steward-gateway` | **Not Started** | 0 code, 3 boilerplate files | (intended: external API gateway) | everything currently |

## Governance Model

```
agent-world PUBLISHES governance (policies, registry, constitution)
    │
    ▼
steward READS and RESPECTS autonomously (has own intelligence)
agent-city FOLLOWS within local sovereignty
agent-internet ROUTES and PROJECTS based on trust rules
    │
    ▼
Results flow back as heartbeats, briefs, and federation messages
```

**This is NOT command-and-control.** agent-world is a legislature, not a dictator.
steward is an autonomous executive with its own decision-making, self-healing, and lifecycle.

## Export / Projection Rule

- Source repos (`steward-protocol`, `agent-world`) export authority bundles
- `agent-internet` imports bundles, resolves routes, renders public projection
- Source meaning always overrides projected representation

## Cross-Repo Communication

1. **Governance**: agent-world publishes → all nodes read
2. **Research requests**: any repo → agent-research (via Nadi/issues)
3. **Status reports**: any repo → agent-world (via heartbeat/federation brief)
4. **Public projection**: source repo → agent-internet (via authority bundle)
5. **Federation heartbeat**: steward → steward-federation inbox (via GitNadiSync)

## Hard Rules

1. **Only agent-world modifies the registry** — other repos propose via issues/PRs
2. **steward is autonomous, not commanded** — it reads policies, makes own decisions
3. **agent-internet projects, never authors** — source bundle is authority
4. **agent-city is sovereign locally** — world policies apply, but city governs itself
5. **Opus sessions stay in their repo** — cross-repo changes go through issues/PRs
