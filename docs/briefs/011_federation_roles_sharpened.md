# Federation Brief #11: Role Definitions Sharpened by Code-Level Audit

**Category**: Governance / Federation Architecture
**Date**: 2026-03-16
**Status**: Published
**Scope**: All 10 federation repos audited at the code level

---

## Summary

FEDERATION_ROLES.md and REPO_BOUNDARIES.md have been rewritten based on a
code-level audit of every repo in the federation. Key corrections:

### Major Role Corrections

| Repo | Old Label | New Label | Why |
|------|-----------|-----------|-----|
| steward | "Operator" (task runner) | **Autonomous Agent Engine** | 168 files, 589 classes, 31 services, 5 run modes, self-healing. Not a dumb task runner. |
| steward-federation | "Transport Hub" | **Nadi Mailbox** | Zero code. Two JSON files. All transport logic lives in steward's FederationBridge. |
| steward-gateway | "External Gateway" | **Not Started** | 3 boilerplate files. Zero code. No activity in 3 weeks. |
| agent-internet | "Projection Layer" | **Control Plane + Projection** | 67 modules, 1,125-line control plane with real routing, trust verification, and city registration. |

### Governance Model Correction

The old document implied command-and-control: "agent-world declares WHAT,
steward executes HOW." This is wrong.

**Corrected model**: agent-world is a **legislature** — it publishes policies
and registry state. steward is an **autonomous executive** that reads those
policies and incorporates them into its own decision-making. steward has its
own intelligence (31 services, self-healing, anomaly detection, multi-LLM
orchestration). It's a peer that respects governance, not a servant that
takes orders.

### Maturity Assessment Added

| Repo | Code Files | Real Substance | Maturity |
|------|-----------|----------------|----------|
| steward | 168 | 589 classes, 31 services | Production-grade but tech debt |
| steward-protocol | 126+ | 73+ protocol files | Ambitious, indirection-heavy |
| agent-internet | 67 | 1,125-line control plane | Most substantive infra repo |
| agent-world | 8 | Clean governance engine | Solid, minimal, correct |
| agent-template | 9 scripts | Working wizard, no DevContainer | Young (4 days) |
| agent-research | 8 + 5 dirs | Real 201-line engine | Day-zero |
| steward-federation | 0 | Two JSON files | Passive mailbox |
| steward-gateway | 0 | Three boilerplate files | Empty |

### Open Questions Raised

1. **steward-federation**: Keep as separate repo or fold into steward?
   GitHub Issues already serve as de facto Nadi transport.
2. **steward-gateway**: Start development or archive?
3. **steward-protocol indirection**: How much of the 73+ protocol files
   is working implementation vs. organizational scaffolding?
4. **agent-template DevContainer**: The template repo doesn't have DevContainer
   config despite the federation policy requiring it.
5. **steward governance integration**: How does steward actually consume
   agent-world policies today? Live integration or manual?

## Files Changed

- `docs/FEDERATION_ROLES.md` — complete rewrite (285 lines added, 166 removed)
- `docs/REPO_BOUNDARIES.md` — updated to match factual findings

## Branch

`claude/publish-federation-briefs-THxBM`
