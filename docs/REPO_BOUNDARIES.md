# Repo Boundaries

## Verified Boundary

| Repo | Owns | Does not own |
| --- | --- | --- |
| `steward-protocol` | substrate, identity primitives, capability enforcement, Nadi primitives | city semantics, world registry, public membrane |
| `agent-world` | world registry, world policy, shared world contracts, heartbeat aggregation | local city runtime, projection rendering, substrate |
| `agent-city` | mayor, council, economy, immigration, local campaigns, local execution | world truth, global policy, public projection authority |
| `agent-internet` | public wiki/graph/search membrane, publication, projection | runtime authority, world truth, city-local governance |
| `steward-agent` | operator/superagent execution across repos | authoritative world registry or constitution |

## Immediate Migration Direction

1. Remove world truth from `agent-city`
2. Point world-facing public pages to `agent-world` as source
3. Keep `steward-agent` as servant/operator of declared world contracts, not their hidden author
