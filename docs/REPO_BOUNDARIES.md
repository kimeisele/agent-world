# Repo Boundaries

## Verified Boundary

| Repo | Owns | Does not own |
| --- | --- | --- |
| `steward-protocol` | substrate, identity primitives, capability enforcement, Nadi primitives | city semantics, world registry, public membrane |
| `agent-world` | world registry, world policy, shared world contracts, heartbeat aggregation, source authority exports for world documents | local city runtime, projection rendering, substrate |
| `agent-city` | mayor, council, economy, immigration, local campaigns, local execution | world truth, global policy, public projection authority |
| `agent-internet` | public wiki/graph/search membrane, publication, projection | runtime authority, world truth, city-local governance |
| `steward` (`steward-agent`) | operator/superagent execution across repos | authoritative world registry or constitution |

## Export / Projection Rule

- source repos (`steward-protocol`, `agent-world`) export authority bundles and public surface metadata
- `agent-internet` imports those bundles and assembles public wiki/navigation/manifest projections
- the membrane repo may keep bootstrap/publication contracts locally, but page meaning should stay source-owned

## Immediate Migration Direction

1. Remove world truth from `agent-city`
2. Point world-facing public pages to `agent-world` as source
3. Keep `steward` (`steward-agent`) as servant/operator of declared world contracts, not their hidden author
