# Repo Boundaries

## Verified Boundary

| Repo | Role | Owns | Does NOT own |
| --- | --- | --- | --- |
| `agent-world` | **World Architect** | registry, policy, constitution, heartbeat, authority exports, federation roles, campaigns | city runtime, projection rendering, substrate, operator execution |
| `steward` | **Operator** | cross-repo task execution, operator intelligence, diagnostic runs, Telegram bot | world truth, registry, governance decisions, protocol definitions |
| `steward-protocol` | **Substrate** | identity primitives, capability enforcement, Nadi protocol spec, federation descriptor schema | who is registered, policy decisions, runtime execution |
| `steward-federation` | **Transport Hub** | Nadi relay, message persistence, shared federation state | transport protocol definition, message content authority, governance |
| `steward-gateway` | **External Gateway** | HTTP/API endpoints, external auth, rate limiting | internal routing, data authority, governance |
| `agent-city` | **City Runtime** | mayor, council, economy, immigration, local campaigns, agent population, local execution | world truth, global policy, public projection, substrate |
| `agent-internet` | **Projection Layer** | public wiki/graph/search, bundle consumption, rendering, mothership pages | source truth, runtime authority, governance |
| `agent-template` | **Scaffolding** | federation node template, DevContainer blueprint, onboarding docs | runtime capability, governance, active federation participation |
| `agent-research` | **Research Faculty** | research synthesis, cross-domain analysis, open inquiry | governance decisions, implementation, world truth modification |

## Delegation Chain

```
agent-world DECIDES  →  steward EXECUTES  →  target repo ADAPTS
         ↑                                          │
         └──────────── results flow back ───────────┘
```

## Export / Projection Rule

- Source repos (`steward-protocol`, `agent-world`) export authority bundles and public surface metadata
- `agent-internet` imports those bundles and assembles public wiki/navigation/manifest projections
- The membrane repo may keep bootstrap/publication contracts locally, but page meaning stays source-owned

## Cross-Repo Communication

1. **Directives**: agent-world → steward (via issues or federation directive)
2. **Research requests**: any repo → agent-research (via Nadi issue)
3. **Status reports**: any repo → agent-world (via heartbeat or federation brief)
4. **Public projection**: source repo → agent-internet (via authority bundle)

## Hard Rules

1. **No repo modifies another repo's registry entry** — only agent-world modifies the registry
2. **steward is servant, not author** — it executes declared contracts, never invents governance
3. **agent-internet projects, never authors** — if page contradicts source bundle, bundle wins
4. **agent-city is sovereign locally** — world directives REQUEST, not COMMAND, city-internal changes
5. **Opus sessions stay in their repo** — cross-repo changes go through issues/PRs, not direct edits
