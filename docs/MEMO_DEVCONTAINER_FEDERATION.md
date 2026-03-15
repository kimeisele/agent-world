# Memo: Federation-Wide DevContainer Auto-Setup

**Datum:** 2026-03-15
**Betrifft:** Automatische Container-Einrichtung fuer alle Foederations-Repos
**Ort der Konfiguration:** `agent-world` (als World-Truth-Quelle) + `agent-template` (als Scaffolding-Quelle)

---

## 1. Problemstellung

Alle Repos der Foederation (agent-city, agent-internet, agent-world, steward-protocol, steward, steward-federation, steward-test, agent-template) muessen in beliebigen Entwicklungsumgebungen sofort funktionsfaehig sein:

- **Cloud Code Web** (Claude Code on the Web / cloud containers)
- **GitHub Codespaces**
- **VS Code Dev Containers** (lokal via Docker)
- **GitPod**
- **Standalone Docker / Podman**
- **Lokale Bare-Metal-Setups** (fallback ohne Container)

## 2. Ist agent-world der richtige Ort?

**Ja und Nein:**

| Aspekt | Ort | Begruendung |
|--------|-----|-------------|
| **Policy**, dass jedes Foederations-Repo einen DevContainer haben MUSS | `agent-world` (world_policies.yaml) | World-Policy = foederationsweite Anforderung |
| **Template/Blueprint** fuer den DevContainer | `agent-template` | Scaffolding-Capability gehoert dort hin |
| **Die eigentliche `.devcontainer/`** | In JEDEM einzelnen Repo | DevContainers muessen im jeweiligen Repo liegen, damit Plattformen sie erkennen |
| **Validierung/Compliance** | `agent-world` Heartbeat + Governance | Pruefung ob Repos compliant sind |

### Architekturentscheidung

`agent-world` definiert die **Policy + Compliance-Pruefung**. `agent-template` liefert das **Blueprint**. Jedes Repo bekommt seine eigene `.devcontainer/` Konfiguration (ggf. per Template-Sync oder manuell).

## 3. Strategie: Multi-Plattform-DevContainer

### 3.1 Universeller `.devcontainer/devcontainer.json`

Ein einzelnes `devcontainer.json` das alle gaengigen Plattformen abdeckt:

- **Features-System** statt monolithischem Dockerfile (leichter wartbar)
- **`onCreateCommand`** fuer Language-Runtime-Setup
- **`postCreateCommand`** fuer Dependency-Installation
- **`postStartCommand`** fuer Heartbeat/Liveness-Checks
- **Cloud Code Web**: Erkennt `devcontainer.json` automatisch
- **Codespaces**: Erkennt `.devcontainer/` automatisch
- **VS Code Remote**: Erkennt `.devcontainer/` automatisch
- **GitPod**: Braucht zusaetzlich `.gitpod.yml` (Fallback)

### 3.2 Python-Repos (agent-world, agent-city, steward-protocol etc.)

```json
{
  "name": "<repo-name>",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "features": {
    "ghcr.io/devcontainers/features/git:1": {},
    "ghcr.io/devcontainers/features/github-cli:1": {},
    "ghcr.io/devcontainers/features/node:1": {}
  },
  "postCreateCommand": "pip install -e '.[dev]'",
  "postStartCommand": "echo 'Container ready'",
  "customizations": {
    "vscode": {
      "extensions": ["ms-python.python", "charliermarsh.ruff"]
    }
  }
}
```

### 3.3 Node/JS-Repos (falls vorhanden)

Gleiche Struktur, nur mit `node`-base-image und `npm install`.

### 3.4 Fallback fuer Plattformen ohne DevContainer-Support

- Ein `scripts/bootstrap.sh` in jedem Repo das die gleiche Setup-Logik enthaelt
- Wird von `postCreateCommand` aufgerufen UND kann standalone laufen

## 4. Neue World-Policy

Vorgeschlagene Policy fuer `world_policies.yaml`:

```yaml
- id: federation_devcontainer_required
  rule: >-
    Federation repos must include a .devcontainer/devcontainer.json
    that enables zero-config development in container-based environments.
  enforcement: trust_penalty
  trust_penalty: 0.15
  verification: steward_diagnostic
  remediation: agent_template_devcontainer
```

## 5. Neue Governance-Capability

In `schema.py` unter `KNOWN_AGENT_CAPABILITIES`:
- `devcontainer_ready` — Repo hat funktionierenden DevContainer

## 6. Bewertung des aktuellen Foederations-Netzwerks

### Erkenntnisse aus agent-research (Nadi-Netzwerk-Analyse)

agent-research hat eine umfassende Federation-Scaling-Analyse durchgefuehrt
(`federation-scaling-billion-agents.md`), die folgende relevante Punkte ergibt:

- **agent-research war NICHT in der World Registry registriert** — obwohl es ein aktiver,
  gesunder Knoten mit Descriptor v2, 4 Workflows, Nadi-Transport und 7 Fakultaeten ist.
  **Jetzt korrigiert: agent-research ist im Registry eingetragen.**
- **Nadi-Transport laeuft bereits** ueber GitHub Issues (labels: `federation-nadi`).
  agent-research hat Issues an agent-world (#8), steward (#25), agent-internet (#6) gesendet.
- **WCFA-Muster identifiziert**: `file_bridge_until_upgraded` in world.yaml ist ein
  bekanntes "Wired, Crashed, Fell Back, Abandoned"-Pattern. Die Foederation nutzt
  de facto bereits GitHub Issues als Transport.
- **Descriptor v2** in agent-research hat erweiterte Felder: `node_role`, `faculties`,
  `federation_interfaces` (produces/consumes/protocols). agent-world ist noch auf v1.
- **GitHub-API Rate-Limit** wird ab ~500 Knoten zum Problem (5000 req/h authentifiziert).
  DevContainer-Setup muss auch GITHUB_TOKEN-Handling beruecksichtigen.

### Aktuelle Compliance (aus Registry + GitHub API):

| Repo | Descriptor | CI | DevContainer | Nadi-Aktiv | Status |
|------|-----------|-----|-------------|------------|--------|
| kimeisele/agent-city | OK | OK | FEHLT | ja | teilweise compliant |
| kimeisele/agent-internet | unvollstaendig | unklar | FEHLT | ja | non-compliant |
| kimeisele/agent-world | OK | OK | **NEU** | ja (empfaengt) | compliant |
| kimeisele/agent-research | **OK (v2!)** | **4 Workflows** | FEHLT | **ja (sendet)** | teilweise compliant |
| kimeisele/steward-protocol | OK | OK | FEHLT | nein | teilweise compliant |
| kimeisele/steward | OK | OK | FEHLT | ja | teilweise compliant |
| kimeisele/steward-federation | unvollstaendig | unklar | FEHLT | nein | non-compliant |
| kimeisele/steward-test | unvollstaendig | unklar | FEHLT | nein | non-compliant |
| kimeisele/agent-template | OK | OK | FEHLT | nein | teilweise compliant |

### Diagnose

- **Nur agent-world** hat jetzt eine `.devcontainer/` Konfiguration
- 3 Repos (agent-internet, steward-federation, steward-test) haben `descriptor_incomplete`
- **agent-research ist der gesundeste Nicht-World-Knoten**: v2-Descriptor, 4 CI-Workflows,
  Nadi-Transport aktiv, Research-Engine mit 4-Phasen-Zyklus
- Die Foederation nutzt bereits de facto Nadi-Transport (GitHub Issues), obwohl
  world.yaml noch `file_bridge_until_upgraded` deklariert

## 7. Umsetzungsplan

### Schritt 1 (jetzt, in agent-world):
- `.devcontainer/devcontainer.json` fuer agent-world erstellen
- Policy `federation_devcontainer_required` hinzufuegen
- Governance-Engine um DevContainer-Check erweitern
- `scripts/bootstrap.sh` als plattformunabhaengiges Fallback

### Schritt 2 (agent-template):
- DevContainer-Blueprint als Teil des Templates bereitstellen
- Damit neue Repos sofort compliant sind

### Schritt 3 (alle Repos):
- DevContainer-Config in jedes Foederations-Repo rollen
- Per PR oder per Steward-Automation

## 8. Erkenntnisse aus der Nadi-Netzwerk-Analyse

agent-research Issue #3 (federation scaling) liefert konkrete Architektur-Empfehlungen:

1. **DevContainer muss GITHUB_TOKEN-Handling einschliessen** — fuer Nadi-Transport
   und API-Zugriffe innerhalb des Containers. `containerEnv` in devcontainer.json
   sollte `GITHUB_TOKEN` forwarden (Codespaces tut das automatisch).
2. **bootstrap.sh sollte Nadi-Connectivity pruefen** — ein einfacher
   `curl https://api.github.com/rate_limit` als Health-Check.
3. **Descriptor v2 Migration** — agent-world sollte `.well-known/agent-federation.json`
   auf v2 upgraden (mit `node_role`, `federation_interfaces`).
4. **Die 4 offenen Nadi-Issues auf agent-world** (#4-#8) sollten prozessiert werden —
   sie enthalten Research-Inquiries und Review-Requests von agent-research.

## 9. Offene Issues auf agent-world via Nadi

| Issue | Typ | Von | Inhalt |
|-------|-----|-----|--------|
| #8 | research-inquiry | agent-research | Governance fuer Billion-Agent-Scale mit Sharding |
| #7 | review-request | agent-research | Test Research Result |
| #6 | review-request | agent-research | How do agents coordinate? |
| #5 | review-request | agent-research | Test Research Result |
| #4 | review-request | agent-research | How do agents coordinate? |

Diese Issues sind **lebende Nadi-Nachrichten** — der Beweis dass der
Federation-Transport bereits funktioniert.

---

**Empfehlung:** Sofort mit Schritt 1 beginnen — agent-world als Vorbild-Repo mit DevContainer ausstatten und die Policy deklarieren. agent-research als Vorbild-Knoten nutzen (v2-Descriptor, 4 Workflows, Nadi-Transport). Die offenen Nadi-Issues auf agent-world sollten in einem Folge-Schritt bearbeitet werden.
