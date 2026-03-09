# Cross-Repo Roadmap

## Phase 1 — Establish world truth

### `agent-world`
- keep world registry, policy, schemas, and heartbeat authoritative
- add more cities only through explicit registry entries

### `agent-city`
- remove `world_id: agent-city` style world claims from world-facing source contracts
- demote world pages to city-local pages or migrate them to `agent-world`

### `agent-internet`
- treat `agent-world` as the source for world-facing public pages
- keep projection/public membrane logic here, but not world authority

### `steward-protocol`
- continue shrinking toward substrate + source-authority exports only

### `steward` / `steward-agent`
- remain operator/runtime tooling, not hidden world registry authority

## Phase 2 — Move world semantics out of city runtime

1. Replace city-local world truth with registry references to `agent-world`
2. Shift world-facing docs/pages to `agent-world` as authored source
3. Repoint any world projection paths in `agent-internet` accordingly

## Phase 3 — Federation contract cleanup

1. Replace `mothership` assumptions with world-registry-driven targets
2. Promote shared payloads like `CityReport` and `FederationDirective` from implicit city-local shapes to explicit world contracts
3. Keep transport conservative until real multi-city pain demands a stronger runtime

## Phase 4 — Operator integration

1. Let `steward` consume `agent-world` contracts
2. Allow steward-driven service across repos under declared world policy
3. Keep world truth declarative even if steward becomes the practical superagent operator
