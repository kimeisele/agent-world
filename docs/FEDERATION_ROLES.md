# Federation Roles

Authoritative role definitions for every node in the agent-world federation.
Each Opus session in any repo should read this document to know its place.

## Role Architecture

```
                    ┌─────────────────────┐
                    │    agent-world       │
                    │   WORLD ARCHITECT    │
                    │  registry, policy,   │
                    │  constitution, truth │
                    └─────────┬───────────┘
                              │ directives
              ┌───────────────┼───────────────┐
              │               │               │
    ┌─────────▼──────┐ ┌─────▼──────┐ ┌──────▼────────┐
    │    steward      │ │ agent-city │ │ agent-internet│
    │   OPERATOR      │ │   CITY     │ │  PROJECTION   │
    │  executes tasks │ │  runtime   │ │  public face  │
    └────────┬────────┘ └────────────┘ └───────────────┘
             │
    ┌────────┼────────────────┐
    │        │                │
┌───▼────┐ ┌─▼──────────┐ ┌──▼──────────────┐
│steward │ │steward-     │ │steward-         │
│protocol│ │federation   │ │gateway          │
│SUBSTRATE│ │TRANSPORT HUB│ │EXTERNAL GATEWAY │
└────────┘ └─────────────┘ └─────────────────┘

    ┌─────────────┐  ┌──────────────┐
    │agent-template│  │agent-research│
    │ SCAFFOLDING  │  │  FACULTY     │
    └─────────────┘  └──────────────┘
```

## Role Definitions

### agent-world — WORLD ARCHITECT

**Repo**: `kimeisele/agent-world`
**Role**: Single source of truth for world-level governance.

**Owns**:
- World registry (`config/world_registry.yaml`) — who exists, what trust level
- World policies (`config/world_policies.yaml`) — rules everyone must follow
- World constitution (`docs/WORLD_CONSTITUTION.md`) — foundational principles
- Federation role definitions (this document)
- World heartbeat — aggregated state of all nodes
- Authority export bundles — canonical documents for projection
- Campaigns — world-scoped coordination objectives

**Does NOT own**:
- City-local runtime, economy, or immigration
- Substrate primitives or identity
- Projection rendering or public wiki
- Operator execution logic

**Delegation model**: agent-world declares WHAT should happen.
steward (operator) executes HOW it happens across repos.

---

### steward — OPERATOR

**Repo**: `kimeisele/steward`
**Role**: Autonomous execution engine. Runs tasks across repos on behalf of world directives.

**Owns**:
- Cross-repo task execution (PRs, issues, code changes)
- Operator intelligence (Open-Claw architecture, self-healing)
- Telegram bot interface for human operator
- Federation message routing execution
- Diagnostic runs across repos

**Does NOT own**:
- World truth or registry (that's agent-world)
- Protocol definitions (that's steward-protocol)
- Public projection (that's agent-internet)
- Any authoritative governance decisions

**Key principle**: steward is a SERVANT of declared world contracts.
It executes, it does not author governance. It can propose via issues/PRs,
but agent-world is the authority.

**Relationship to agent-world**: steward reads directives from agent-world
and executes them. It reports results back. It never unilaterally changes
world truth.

---

### steward-protocol — SUBSTRATE

**Repo**: `kimeisele/steward-protocol`
**Role**: Foundation layer. Identity, capability primitives, Nadi transport definitions.

**Owns**:
- Identity primitives and oath system
- Capability type definitions and enforcement contracts
- Nadi transport protocol specification
- Federation descriptor schema
- Protocol versioning

**Does NOT own**:
- Who is registered (that's agent-world registry)
- Policy decisions (that's agent-world)
- Runtime execution (that's steward)
- City-local semantics

**Key principle**: steward-protocol defines the LANGUAGE.
agent-world decides who may SPEAK it and under what RULES.

---

### steward-federation — TRANSPORT HUB

**Repo**: `kimeisele/steward-federation`
**Role**: Shared state and message relay for the agent mesh.

**Owns**:
- Federation Nadi inbox/outbox relay
- Cross-repo message persistence
- Shared federation state snapshots
- Transport health monitoring

**Does NOT own**:
- Transport protocol definition (that's steward-protocol)
- Message content authority (source repos own their messages)
- World governance (that's agent-world)

**Key principle**: steward-federation is a PIPE, not a BRAIN.
It moves messages, it doesn't decide what they mean.

---

### steward-gateway — EXTERNAL GATEWAY

**Repo**: `kimeisele/steward-gateway`
**Role**: External API surface for the federation.

**Owns**:
- HTTP/API endpoints exposed to the outside world
- Authentication and rate limiting for external consumers
- API documentation

**Does NOT own**:
- Internal federation routing
- World governance
- Data authority (proxies to source repos)

**Status**: Early stage. Not yet fully integrated.

---

### agent-city — CITY RUNTIME

**Repo**: `kimeisele/agent-city`
**Role**: The first and founding city. Local autonomous governance.

**Owns**:
- Mayor, council, and local governance
- City economy (credits, transactions)
- Immigration pipeline (visa system: TEMPORARY → CITIZEN)
- Local campaigns and missions
- Agent population (Pokedex)
- Local code execution environment

**Does NOT own**:
- World truth or global policies (that's agent-world)
- Public projection rendering (that's agent-internet)
- Cross-city routing (deferred, future agent-world responsibility)
- Substrate definitions (that's steward-protocol)

**Key principle**: agent-city is SOVEREIGN in local matters.
It follows world policies but governs itself internally.
World directives can request, not command, city-internal changes.

---

### agent-internet — PROJECTION LAYER

**Repo**: `kimeisele/agent-internet`
**Role**: Public face of the federation. Wiki, search, rendering.

**Owns**:
- Public wiki assembly and rendering
- Search and discovery for external consumers
- Authority bundle consumption and projection
- Mothership pages (public-facing navigation)
- Renderer exports (HTML/static output)

**Does NOT own**:
- Source truth for any document (imports from source repos)
- Runtime authority or governance
- City-local data

**Key principle**: agent-internet PROJECTS, it does not AUTHOR.
It consumes authority bundles from source repos and renders them.
If a page contradicts the source bundle, the bundle wins.

---

### agent-template — SCAFFOLDING

**Repo**: `kimeisele/agent-template`
**Role**: One-click template for new federation nodes.

**Owns**:
- Federation node template (cookiecutter/scaffold)
- DevContainer blueprint for federation compliance
- Onboarding documentation for new nodes
- Reference `.well-known/agent-federation.json` structure

**Does NOT own**:
- Any runtime capability
- Governance decisions
- Active federation participation beyond template provision

**Key principle**: agent-template makes it EASY to join the federation.
New repos clone this template and immediately pass compliance checks.

---

### agent-research — RESEARCH FACULTY

**Repo**: `kimeisele/agent-research`
**Role**: Cross-domain research engine. Investigates questions for the federation.

**Owns**:
- Research synthesis and cross-domain analysis
- Open inquiry system (accepts research questions via issues)
- Research result publication
- Nadi-based research request/response flow

**Does NOT own**:
- Governance decisions based on research
- Implementation of recommendations (that's steward's job)
- World truth modification

**Key principle**: agent-research ADVISES, it does not DECIDE.
It produces findings. agent-world decides what to act on.
steward executes the actions.

---

## Decision Flow

```
Question arises
    │
    ▼
agent-research investigates (if needed)
    │
    ▼
agent-world decides (policy/registry change)
    │
    ▼
steward executes (PRs, code, cross-repo tasks)
    │
    ▼
agent-internet projects (public visibility)
    │
    ▼
agent-city adapts locally (if city-relevant)
```

## Trust Hierarchy

| Trust Level | Meaning | Who |
|-------------|---------|-----|
| `founding` | Built the federation. Full trust. | agent-world, agent-city |
| `verified` | Proven compliant. Descriptor + CI + DevContainer. | (target for all nodes) |
| `observed` | Registered but not yet fully compliant. | Most nodes currently |
| `untrusted` | Known but not meeting minimum standards. | Nodes with descriptor_incomplete |

## Scaling Rules

1. **New city?** → Clone agent-template, register in agent-world registry, get reviewed
2. **New agent?** → Same process. agent-world is the gatekeeper
3. **New capability?** → Propose in agent-world issue, add to schema.py, update registry
4. **Cross-repo task?** → agent-world issues directive, steward executes
5. **Public visibility?** → Source repo exports bundle, agent-internet consumes and renders
6. **Research needed?** → Open issue in agent-research, results come back via Nadi

## Anti-Patterns

- **steward authors world truth** → NO. steward executes, agent-world decides
- **agent-city sets global policy** → NO. agent-city is sovereign locally, not globally
- **agent-internet invents content** → NO. It projects what source repos declare
- **Any repo modifies another's registry entry** → NO. Only agent-world modifies the registry
- **Opus session in repo X changes repo Y directly** → NO. Open an issue or PR, let that repo's session handle it
