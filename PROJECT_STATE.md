# Project State

Erstellt: 2026-07-01 21:31:09Z UTC
Zuletzt aktualisiert: 2026-07-02 04:36:01Z UTC
Dokumentstatus: offen
Abschluss-Bestaetigung durch Alex: ausstehend

## Arbeitsregel

- Dieses Repository hat genau ein laufendes Projektstatus-Dokument: `PROJECT_STATE.md`.
- Es duerfen keine parallelen Status-, Plan- oder Handoff-Dokumente fuer dieses Projekt angelegt werden.
- Jeder neue Projektabschnitt in diesem Dokument bekommt Datum und Uhrzeit.
- Ein Projektabschnitt gilt erst als abgeschlossen, wenn Alex ihn ausdruecklich als abgeschlossen bestaetigt.
- Ein neues Statusdokument darf nicht eroeffnet werden, solange dieses Dokument nicht durch Alex abgeschlossen wurde.
- Memory-, Chat- und Kiro-Hinweise sind nur Suchhilfen. Massgeblich sind dieses Dokument, Git, PRs und gepruefte Runtime-Zustaende.

## 2026-07-01 21:31:09Z UTC - Codex-Minimalprofil und AgentSkill-Router

Status: offen
Abschluss-Bestaetigung durch Alex: ausstehend

### Aktueller Git-Stand

- Repository: `/home/alex/obsidian-wiki`
- Branch: `codex/codex-minimal-skill-profile-20260630`
- Remote: `origin/codex/codex-minimal-skill-profile-20260630`
- Letzter Commit: `2b2929a add codex minimal skill profile`
- PR: noch nicht erstellt
- Merge: noch nicht erfolgt
- `PROJECT_STATE.md`: neu angelegt, noch nicht committed oder gepusht
- Lokaler Sonderfall: `.local-quarantine/` bleibt untracked und darf nicht gestaged oder gepusht werden.

### Umgesetzt

- Codex-Minimalprofil eingefuehrt.
- Neuer Router-Skill `wiki-tools` hinzugefuegt.
- Minimalprofil enthaelt 12 Kernskills inklusive `wiki-tools`.
- `obsidian-wiki setup --codex-profile full` bleibt als bewusster Vollmodus moeglich.
- `setup.sh` unterstuetzt `OBSIDIAN_CODEX_SKILL_PROFILE=full`.
- `obsidian-wiki info` erkennt Profil-Drift.
- README und SETUP dokumentieren Minimalprofil, Vollprofil und Router-Mechanik.
- Tests fuer Skillprofile und Router-Ziele hinzugefuegt.

### Verifiziert

- `python -m pytest` -> 37 passed
- `python -m compileall obsidian_wiki` -> OK
- `bash -n setup.sh` -> OK
- `git diff --check` -> OK
- Isolierter Setup-Test mit temporaerem `HOME`:
  - Python-CLI Minimalprofil -> 12 Codex-Skills
  - Python-CLI Fullprofil -> 40 Codex-Skills
  - Python-CLI Full -> Minimal pruning -> 12 Codex-Skills
  - `setup.sh` in temporaerer Repo-Kopie -> 12 Codex-Skills

### Nicht angewendet

- Echtes `obsidian-wiki setup` wurde nicht ausgefuehrt.
- Echtes `/home/alex/.codex/skills/` wurde nicht bereinigt.
- Laufende oder kritische Codex-Sessions, insbesondere fuer `archaerotrrain-rtx`, wurden nicht beruehrt.

### Aktueller Runtime-Befund

- Echtes Codex-Profil hat weiterhin Drift:
  - Minimalprofil erwartet 12 Skills.
  - Aktuell vorhanden: 11/12 Minimal-Skills.
  - Zusaetzlich vorhanden: 28 extra bundled Wiki-Symlinks.
- Dieser Drift ist bewusst nicht behoben, um laufende Codex-Arbeit nicht zu gefaehrden.

### Uebergeordneter Projektstatus Ordnung/Obsidian

Status: nicht abgeschlossen

Abgeschlossen oder weitgehend abgeschlossen:

- Guarded write path fuer `log.md` wurde implementiert, getestet, gepusht und gemerged.
- Guarded skill telemetry fuer `wiki-query` und `wiki-context-pack` wurde implementiert, getestet, gepusht und gemerged.
- Metadata-/Frontmatter-Regel fuer neue Nicht-Paper-Seiten wurde implementiert, getestet, gepusht und gemerged.
- README wurde auf den aktuellen Projektstand gebracht, getestet, gepusht und gemerged.
- Ein-Dokument-Regel fuer Projektstatus wurde festgelegt und in diesem Dokument begonnen.

Noch offen:

- Dieses Statusdokument ist noch nicht committed oder gepusht.
- Aktueller Branch mit Codex-Minimalprofil und `wiki-tools` ist gepusht, aber noch ohne PR und ohne Merge.
- Echtes Codex-Profil wurde aus Sicherheitsgruenden nicht umgestellt.
- Realer Agent-Rollout wurde nicht verifiziert, weil `obsidian-wiki setup` absichtlich nicht auf dem echten Profil lief.
- Die einfache Router-Loesung `wiki-tools` ist nur eine Zwischenstufe.
- Der 2026-konforme AgentSkill-Router mit Skill-Registry, Full-Text-Retrieval, Reranking, Skill-Lifecycle und Dedup ist noch nicht konzipiert oder implementiert.
- Abschluss des Gesamtprojekts "Ordnung/Obsidian" braucht ausdrueckliche Bestaetigung durch Alex.

### Offene Entscheidung

- PR fuer den Branch erstellen und mergen?
- `PROJECT_STATE.md` in denselben Branch committen und pushen?
- Echtes Codex-Profil erst spaeter in einem Wartungsfenster mit Backup/Rollback umstellen?
- Ein 2026-konformer AgentSkill-Router mit Skill-Registry, Full-Text-Retrieval und Reranking als naechsten Architekturabschnitt planen?

### Naechster empfohlener Schritt

Kein Runtime-Eingriff. Zuerst `PROJECT_STATE.md` committen/pushen, wenn Alex die Ein-Dokument-Regel bestaetigt. Danach entscheiden, ob der aktuelle Branch als PR erstellt werden soll, waehrend das echte Codex-Profil unveraendert bleibt.
