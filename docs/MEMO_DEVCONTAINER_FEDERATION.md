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

### Aktuelle Compliance (aus Registry-Daten):

| Repo | Descriptor | CI | DevContainer | Status |
|------|-----------|-----|-------------|--------|
| kimeisele/agent-city | OK | OK | FEHLT | teilweise compliant |
| kimeisele/agent-internet | unvollstaendig | unklar | FEHLT | non-compliant |
| kimeisele/agent-world | OK | OK | FEHLT | teilweise compliant |
| kimeisele/steward-protocol | OK | OK | FEHLT | teilweise compliant |
| kimeisele/steward | OK | OK | FEHLT | teilweise compliant |
| kimeisele/steward-federation | unvollstaendig | unklar | FEHLT | non-compliant |
| kimeisele/steward-test | unvollstaendig | unklar | FEHLT | non-compliant |
| kimeisele/agent-template | OK | OK | FEHLT | teilweise compliant |

### Diagnose

- **Kein einziges Repo** hat aktuell eine `.devcontainer/` Konfiguration
- 3 Repos (agent-internet, steward-federation, steward-test) haben `descriptor_incomplete`
- Die Foederation leidet unter 2 strukturellen Defiziten: fehlende DevContainers + unvollstaendige Descriptoren

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

## 8. Limitierung: Kein GitHub CLI verfuegbar

Ohne `gh` CLI koennen wir die Remote-Repos nicht direkt pruefen. Die Bewertung basiert auf:
- Registry-Daten aus `world_registry.yaml`
- Capability-Flags (insb. `descriptor_incomplete`)
- Lokale Analyse von agent-world selbst

Fuer eine vollstaendige Netzwerk-Bewertung braeuchte man entweder `gh` CLI oder GitHub API-Zugriff per Token.

---

**Empfehlung:** Sofort mit Schritt 1 beginnen — agent-world als Vorbild-Repo mit DevContainer ausstatten und die Policy deklarieren. Der Rest folgt per Foederations-Mechanik.
