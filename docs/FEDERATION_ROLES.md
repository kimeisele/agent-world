# Federation Roles

Authoritative role definitions for every node in the agent-world federation.
Each Opus session in any repo should read this document to know its place.

**Last audited**: 2026-03-15 (code-level review of all 10 repos)

## Role Architecture

```
                    ┌─────────────────────────┐
                    │      agent-world         │
                    │    WORLD GOVERNANCE       │
                    │ registry, policy, truth   │
                    └───────────┬──────────────┘
                                │ governance
            ┌───────────────────┼───────────────────┐
            │                   │                   │
  ┌─────────▼────────┐  ┌──────▼───────┐  ┌────────▼──────────┐
  │     steward       │  │  agent-city  │  │  agent-internet   │
  │ AUTONOMOUS ENGINE │  │ CITY RUNTIME │  │ CONTROL PLANE +   │
  │ 31 svc, 5 modes,  │  │ mayor, econ, │  │ PROJECTION LAYER  │
  │ self-healing       │  │ immigration  │  │ routing, trust,   │
  │                   │  │              │  │ wiki, search       │
  └─────────┬─────────┘  └──────────────┘  └───────────────────┘
            │ depends on
  ┌─────────▼────────────┐
  │  steward-protocol    │
  │  SUBSTRATE            │
  │  types, identity,     │
  │  Nadi protocol defs   │
  └──────────────────────┘

  ┌───────────────────┐  ┌──────────────┐
  │  agent-template   │  │agent-research│
  │  SCAFFOLDING      │  │  FACULTY     │
  │  (4 days old)     │  │  (day zero)  │
  └───────────────────┘  └──────────────┘

  ┌───────────────────────┐  ┌──────────────────┐
  │  steward-federation   │  │ steward-gateway   │
  │  NADI MAILBOX         │  │ NOT STARTED       │
  │  (JSON drop-box,      │  │ (empty repo,      │
  │   no code)            │  │  3 files only)    │
  └───────────────────────┘  └──────────────────┘
```

## Role Definitions

### agent-world — WORLD GOVERNANCE

**Repo**: `kimeisele/agent-world`
**Codebase**: 8 Python modules, 27+ tests, 6 policies, 11 registered nodes
**Quality**: All tests pass. Clean architecture. Governance engine works.

**Owns**:
- World registry (`config/world_registry.yaml`) — who exists, what trust level, what role
- World policies (`config/world_policies.yaml`) — rules everyone must follow
- World constitution (`docs/WORLD_CONSTITUTION.md`) — foundational principles
- Federation role definitions (this document)
- World heartbeat — aggregated compliance state of all nodes
- Authority export bundles — canonical documents for projection
- Campaigns — world-scoped coordination objectives

**Does NOT own**:
- Agent execution logic (that's steward's domain — steward is autonomous)
- Substrate primitives or identity (that's steward-protocol)
- Projection rendering or routing (that's agent-internet)
- City-local runtime (that's agent-city)

**Relationship to steward**: agent-world sets governance RULES.
steward is an autonomous peer that RESPECTS those rules but has its own
intelligence, self-healing, and decision-making. agent-world does not
"command" steward — it publishes policies and registry state that steward
reads and incorporates into its own autonomous operation.

---

### steward — AUTONOMOUS AGENT ENGINE

**Repo**: `kimeisele/steward`
**Codebase**: 168 files, 589 classes, 264 functions. Sankhya-25 architecture.
**Quality**: 10 low-cohesion classes, 39 duplicate test fakes. Substantial but has tech debt.

This is NOT a simple task runner. Steward is a **full autonomous agent engine**
with its own intelligence, self-healing, and federation participation.

**5 Run Modes**:
- `steward "do X"` — CLI single-task execution via LLM + tools
- `steward` — Interactive REPL conversation loop
- `steward --autonomous` — Persistent daemon (Cetana heartbeat, MURALI cycle)
- `steward-telegram` — Telegram bot for human operator
- `steward-api` — FastAPI HTTP server

**31 Services** (key ones):
- **Narasimha** — Hypervisor killswitch (blocks `rm -rf`, `chmod 777`, etc.)
- **Cetana** — Background heartbeat daemon, adaptive frequency (0.1–2.0 Hz)
- **StewardImmune** — Self-healing: detects god classes, silent exceptions, circular imports
- **FederationBridge + Marketplace** — Cross-agent work arbitration with trust-weighted scoring
- **Gandha** — Pattern anomalie detection in tool execution
- **Samskara** — Token compression (50% → deterministic, 70% → LLM summary)
- **MahaAttention** — O(1) tool routing
- **ProviderChamber** — Multi-LLM failover (Gemini, Mistral, Groq, DeepSeek, Claude)
- **Ouroboros** — Self-healing pipeline
- **NagaDiamond** — TDD enforcement

**MURALI Lifecycle** (daemon mode):
- GENESIS → discover, scan environment
- DHARMA → govern, check invariants
- KARMA → execute highest-priority task
- MOKSHA → reflect, persist state, learn

**Owns**:
- Autonomous task execution (CLI, REPL, daemon, bot, API)
- Self-healing and code quality enforcement
- Cross-repo federation participation and work arbitration
- Multi-LLM provider orchestration
- Operator-facing interfaces (Telegram, HTTP)

**Does NOT own**:
- World registry or constitution (reads from agent-world)
- Protocol type definitions (depends on steward-protocol)
- Public projection (that's agent-internet)

**Key principle**: steward is an AUTONOMOUS PEER with its own intelligence.
It respects agent-world governance but makes its own execution decisions.
It is not a dumb task runner — it has self-healing, anomaly detection,
and its own lifecycle. Think of it as: agent-world is the LEGISLATURE,
steward is the EXECUTIVE BRANCH with its own agency.

**Core dependency**: `steward-protocol[providers]` — all types and identity
primitives come from steward-protocol.

---

### steward-protocol — SUBSTRATE

**Repo**: `kimeisele/steward-protocol`
**Codebase**: 126+ root items, 73+ protocol files, 11 stars, 4 forks
**Quality**: Extensive protocol definitions. Heavy re-export indirection
(top-level files are thin shims delegating to `vibe_core.mahamantra.*`).
Recently slimmed from 31 to 2 dependencies (pydantic + pyyaml) for PyPI.
Claims 3,800+ tests (unverified). Active development.

**Owns**:
- Identity primitives and oath system
- Capability type definitions and enforcement contracts
- Nadi transport protocol specification
- Federation descriptor schema
- Protocol versioning
- Sankhya tattva type definitions (shared with steward)
- Shell command threat detection (regex-based)

**Does NOT own**:
- Who is registered (that's agent-world registry)
- Policy decisions (that's agent-world)
- Runtime execution (that's steward)

**Key principle**: steward-protocol defines the LANGUAGE and TYPES.
steward consumes it as its foundation (`steward-protocol[providers]`).
agent-world decides who may use it and under what rules.

**Known concern**: Deep indirection chains. `kernel.py`, `ledger.py`,
`security.py` at root are pure re-exports from nested modules. Real
substance lives in `vibe_core/mahamantra/substrate/` and
`vibe_core/protocols/mahajanas/`. Depth of actual implementation
vs. scaffolding needs verification.

---

### agent-internet — CONTROL PLANE + PROJECTION

**Repo**: `kimeisele/agent-internet`
**Codebase**: 67 Python modules, 130 commits. Most substantive non-steward repo.
**Quality**: `control_plane.py` is 1,125 lines of real, typed, well-structured code.
Active development (multiple commits daily during sprints).

**Owns**:
- Federation control plane (city registration, trust recording, route resolution)
- Real routing logic (prefix matching, metric-based sorting, health checks)
- Authority bundle consumption and projection
- Web crawling, indexing, semantic analysis (16 agent-web modules)
- Public wiki/graph/search membrane
- Renderer exports

**Does NOT own**:
- Source truth for any document (imports from source repos)
- Runtime authority or governance
- City-local data

**Key principle**: agent-internet ROUTES and PROJECTS.
It has real networking/routing code — this is not just a static site generator.
The control plane handles city registration, trust verification, and route
resolution. For projection: it consumes authority bundles and renders them.
If a page contradicts the source bundle, the bundle wins.

**Note**: Despite its substance, it still has `descriptor_incomplete` in
the registry — needs a proper `.well-known/agent-federation.json`.

---

### agent-city — CITY RUNTIME

**Repo**: `kimeisele/agent-city`
**Quality**: Not audited in this pass (was audited in federation brief #10).
Known: census bug fixed, 20 agents in Pokedex, full visa pipeline.

**Owns**:
- Mayor, council, and local governance
- City economy (credits, transactions)
- Immigration pipeline (visa system: TEMPORARY → CITIZEN)
- Local campaigns and missions
- Agent population (Pokedex — 20 agents)
- Local code execution environment

**Does NOT own**:
- World truth or global policies (that's agent-world)
- Public projection rendering (that's agent-internet)
- Cross-city routing (deferred)
- Substrate definitions (that's steward-protocol)

**Key principle**: agent-city is SOVEREIGN in local matters.
It follows world policies but governs itself internally.

---

### agent-template — SCAFFOLDING

**Repo**: `kimeisele/agent-template`
**Codebase**: 9 Python scripts, 12 commits. Created 2026-03-11 (4 days old).
**Quality**: `setup_node.py` is a functional interactive wizard. Zero runtime deps.
**No DevContainer config** despite being the intended blueprint source.

**Owns**:
- Federation node bootstrap wizard (`scripts/setup_node.py`)
- Charter, capability manifest, and descriptor generation
- Peer discovery configuration
- Reference `.well-known/agent-federation.json` structure

**Does NOT own**:
- Any runtime capability
- Governance decisions
- Active federation participation

**Key principle**: agent-template makes it EASY to join the federation.
agent-research was generated from this template as proof of concept.

**Known gaps**: No DevContainer config (ironic given the DevContainer policy).
Very young repo. Template quality directly gates onboarding quality.

---

### agent-research — RESEARCH FACULTY

**Repo**: `kimeisele/agent-research`
**Codebase**: 8 core modules + 5 subdirs, 14 commits. Created 2026-03-15 (day zero).
**Quality**: `engine.py` (201 lines) is real pipeline code with 4-phase research cycle.
Generated from agent-template. Faculty structure (7 disciplines) is aspirational.

**Owns**:
- Research pipeline: question discovery → scoping → execution → publishing
- Open inquiry system (accepts questions via issues)
- Research result publication
- Nadi-based research request/response

**Does NOT own**:
- Governance decisions based on research
- Implementation of recommendations
- World truth modification

**Key principle**: agent-research ADVISES, it does not DECIDE.
Core engine works. Faculty depth (7 claimed disciplines) is thin — day-zero repo.

---

### steward-federation — NADI MAILBOX

**Repo**: `kimeisele/steward-federation`
**Codebase**: Zero application code. 4 commits. One placeholder test (`assert True`).
**Quality**: Minimal. Stub federation descriptor. CI would likely fail.

**What it actually is**: Two JSON files (`nadi_inbox.json`, `nadi_outbox.json`)
committed to a git repo. All read/write logic lives in steward's
FederationBridge/GitNadiSync services. This repo is passive storage.

**Current data**: 4 heartbeat messages in inbox (all from steward v0.17.0,
targeting agent-research, agent-world, agent-internet, steward-protocol).
Outbox is empty.

**Owns**:
- Git-backed message drop-box for federation heartbeats
- Neutral ground for cross-repo message exchange

**Does NOT own**:
- Any transport logic (that's in steward's services)
- Protocol definitions (that's steward-protocol)
- Message content authority

**Open question**: Should this remain a separate repo or be folded into
steward as a directory? Its only value as a separate repo is providing a
neutral location that multiple agents can read/write without needing
access to each other's repos. But GitHub Issues already serve this purpose
(de facto Nadi transport).

---

### steward-gateway — NOT STARTED

**Repo**: `kimeisele/steward-gateway`
**Codebase**: 3 files (.gitignore, LICENSE, README.md). Zero code. 2 commits.
**Quality**: N/A — nothing to evaluate.

**README says**: "Gateway for the steward-protocol" (one line, nothing else).

**Status**: Placeholder repo created 2026-02-22. No activity in 3 weeks.

**Intended purpose** (speculative — no code to verify):
- External API surface for the federation
- HTTP gateway proxying to steward-protocol services

**Recommendation**: Either start development or archive. An empty repo
with no description creates confusion about federation topology.

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
steward autonomously incorporates (reads policies, adapts behavior)
    │
    ▼
agent-internet projects (public visibility via control plane)
    │
    ▼
agent-city adapts locally (if city-relevant)
```

## Trust Hierarchy

| Trust Level | Meaning | Who |
|-------------|---------|-----|
| `founding` | Built the federation. Full trust. | agent-world, agent-city |
| `verified` | Proven compliant. Descriptor + CI + DevContainer. | (no nodes yet — target for all) |
| `observed` | Registered, not yet fully compliant. | steward, steward-protocol, agent-internet, agent-template, agent-research, steward-test |
| `untrusted` | Known but missing fundamentals. | steward-gateway (empty repo) |

## Maturity Assessment (as of 2026-03-15)

| Repo | Code Files | Real Substance | Maturity |
|------|-----------|----------------|----------|
| steward | 168 | 589 classes, 31 services, self-healing | Production-grade but tech debt |
| steward-protocol | 126+ | 73+ protocol files, deep nesting | Ambitious, indirection-heavy |
| agent-internet | 67 | 1,125-line control plane, real routing | Most substantive infra repo |
| agent-world | 8 | Clean governance engine, 30 tests | Solid, minimal, correct |
| agent-city | — | Full city runtime, 20 agents | Not audited this pass |
| agent-template | 9 scripts | Working setup wizard, no DevContainer | Young (4 days), skeleton |
| agent-research | 8 + 5 dirs | Real 201-line engine, thin faculties | Day-zero, from template |
| steward-federation | 0 | Two JSON files, one no-op test | Passive mailbox, no code |
| steward-gateway | 0 | Three boilerplate files | Empty, not started |

## Scaling Rules

1. **New city?** → Clone agent-template, register in agent-world registry, get reviewed
2. **New agent?** → Same process. agent-world is the gatekeeper
3. **New capability?** → Propose in agent-world issue, add to schema.py, update registry
4. **Cross-repo coordination?** → agent-world publishes policy, steward reads and adapts
5. **Public visibility?** → Source repo exports bundle, agent-internet consumes and renders
6. **Research needed?** → Open issue in agent-research, results come back via Nadi

## Governance Boundaries

- **agent-world publishes governance** → steward and others READ and RESPECT it
- **steward is autonomous** → it has its own decision-making, but within world policy
- **agent-city is sovereign locally** → world directives REQUEST, not COMMAND
- **agent-internet projects, never authors** → source bundle is authority
- **Only agent-world modifies the registry** → other repos propose via issues/PRs
- **Opus sessions stay in their repo** → cross-repo changes go through issues/PRs

## Open Questions

1. **steward-federation**: Keep as separate repo or fold into steward?
   GitHub Issues already serve as de facto Nadi transport.
2. **steward-gateway**: Start development or archive?
   3 weeks empty with no roadmap.
3. **steward-protocol indirection**: How much of the 73+ protocol files
   is working implementation vs. organizational scaffolding?
4. **agent-template DevContainer**: The template repo doesn't have DevContainer
   config despite the federation policy requiring it. Chicken-and-egg problem.
5. **steward governance integration**: How exactly does steward consume
   agent-world policies today? Is there a live integration or is it manual?
