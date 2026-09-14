# Precheck Fail Roadmap (`PRECHECK_FAIL_ROADMAP.md`)

## Übersicht

Dieses Dokument beschreibt die schrittweise Roadmap zur Behebung aller im Audit-Bericht (`ADUIT_PRECHECK_FAIL.md`) identifizierten Precheck-Fehler für das **Mini-MOSbius**-Projekt auf der **IHP SG13G2** PDK-Technologie (`ihp-sg13g2`).

Ziel ist die systematische Abarbeitung aller Fehlerursachen (Technologie-Koppelungsfehler SkyWater 130 vs. IHP SG13G2, fehlende Layer, falsche Boundary-Zuordnung sowie DEF-Template-Pfadauslösungsfehler), um einen dauerhaft grünen Status im **Tiny Tapeout Precheck** zu erreichen.

---

## Phasen-Übersicht zur Precheck-Behebung

```
┌────────────────────────────────────────────────────────┐
│ Phase 1: Workflow- & Tag-Migration auf @ttihp26b      │
│ - Aktualisierung von .github/workflows/gds.yaml        │
│ - Aktualisierung von .github/workflows/docs.yaml       │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Phase 2: DEF-Template- & Support-Tools-Pfadkorrektur   │
│ - Bereitstellung von tt_analog_3x2_3v3.def für IHP     │
│ - Auflösung relativer Pfade in tt-support-tools        │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Phase 3: GDS/LEF Layout-Re-Generierung & Layer-Mapping │
│ - Neukompilierung des Layouts mit sg13g2.tech          │
│ - Ersetzung von Sky130-Layern durch IHP SG13G2-Layer   │
│ - Einbetten der IHP prBoundary (Layer 189/4 bzw. 235/4) │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Phase 4: Behebung kaskadierender Analog-Pin-Fehler     │
│ - Validierung der Analog-Pin-Positionen (ua[0]..ua[5])  │
│ - Abgleich der Pin-Definitionen in info.yaml          │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Phase 5: Lokale Verifikation & CI/CD-Bestätigung       │
│ - Lokale Tests ausführen (make check, make lint)       │
│ - GitHub Actions Precheck-Job auf Grün verifizieren    │
└────────────────────────────────────────────────────────┘
```

---

## Phase 1: Workflow- & Tag-Migration auf `@ttihp26b`

> **Ziel:** Umstellung der CI/CD-Pipeline von SkyWater 130 (`@ttsky26c`) auf IHP SG13G2 (`@ttihp26b`), um die korrekten Tooling-Skripte und Regelwerke einzubinden.

- [ ] **1.1 Aktualisierung der Workflow-Konfiguration `.github/workflows/gds.yaml`**
  - [ ] **1.1.1** Anpassen der Action-Referenzen im `custom_gds`-Schritt auf `TinyTapeout/tt-gds-action/custom_gds@ttihp26b`.
  - [ ] **1.1.2** Anpassen der Action-Referenzen im `precheck`-Schritt auf `TinyTapeout/tt-gds-action/precheck@ttihp26b`.
  - [ ] **1.1.3** Anpassen der Action-Referenzen im `viewer`-Schritt auf `TinyTapeout/tt-gds-action/viewer@ttihp26b`.
  - [ ] **1.1.4** Überprüfen, dass der Parameter `pdk: ihp-sg13g2` im `custom_gds`-Schritt gesetzt ist.

- [ ] **1.2 Aktualisierung der Workflow-Konfiguration `.github/workflows/docs.yaml`**
  - [ ] **1.2.1** Anpassen der Action-Referenz im `docs`-Schritt auf `TinyTapeout/tt-gds-action/docs@ttihp26b`.

- [ ] **1.3 Statische Verifikation der Workflow-Tags**
  - [ ] **1.3.1** Ausführen von `python3 py/verify_cicd_config.py` zur Validierung der Tag-Einstellungen.

---

## Phase 2: DEF-Template- & Pfadauflösungs-Korrektur

> **Ziel:** Behebung des `FileNotFoundError` bei der Pfadauflösung von `../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def`.

- [ ] **2.1 Validierung der Template-Zuordnung in `info.yaml`**
  - [ ] **2.1.1** Überprüfen, dass `info.yaml` die Attribute `tiles: "3x2"`, `uses_vapwr: true` und `language: "Analog"` enthält.
  - [ ] **2.1.2** Bestätigen, dass diese Parameter bei Precheck zur automatischen Auswahl des Templates `tt_analog_3x2_3v3.def` führen.

- [ ] **2.2 Verifikation des Aufrufpfades im Runner Container**
  - [ ] **2.2.1** Sicherstellen, dass das Tag `@ttihp26b` in `tt-support-tools` die Pfade relativ zum Repository-Root bzw. PDK-Installationspfad korrekt auflöst.
  - [ ] **2.2.2** Testen, dass der Precheck-Schritt die DEF-Template-Datei `tt_analog_3x2_3v3.def` ohne Dateisystemfehler einlesen kann.

---

## Phase 3: GDS/LEF-Layout-Re-Generierung & Layer-Mapping (IHP SG13G2)

> **Ziel:** Beseitigung aller SkyWater 130 Layer (`(68,20)`, `(69,20)`, `(235,4)` etc.) und vollständige Re-Generierung des GDS/LEF-Artefakts unter Verwendung der IHP SG13G2 Layer-Map.

- [ ] **3.1 Aktualisierung der Layout-Skripte & Technologiedateien**
  - [ ] **3.1.1** Einbinden der IHP SG13G2 Technologiedatei (`sg13g2.tech` für Magic VLSI).
  - [ ] **3.1.2** Anpassung der Python-Generatorskripte (`py/common.py`, `py/gen_asw_ctrl.py`, `py/gen_dev_ctrl.py`) an IHP SG13G2 Grid- und Pitch-Vorgaben.
  - [ ] **3.1.3** Neugenerierung der Standardzellen- und Decap-Instanziierungen für IHP SG13G2 (`sg13g2_decap_*`).

- [ ] **3.2 Neukompilierung & Export des Top-Level Layouts**
  - [ ] **3.2.1** Neu-Assemblierung der Top-Level-Cell `tt_um_tnt_mosbius` in Magic / KLayout.
  - [ ] **3.2.2** Exportieren des neuen GDSII-Layouts nach `gds/tt_um_tnt_mosbius.gds`.
  - [ ] **3.2.3** Exportieren der abstrakten LEF-Beschreibung nach `lef/tt_um_tnt_mosbius.lef`.

- [ ] **3.3 Verifikation des `prBoundary`-Layers**
  - [ ] **3.3.1** Sicherstellen, dass das IHP PR-Boundary Layer (z. B. `189/4` / `235/4`) in `tt_um_tnt_mosbius.gds` vorhanden ist.
  - [ ] **3.3.2** Überprüfen der MACRO SIZE-Dimensionen in `lef/tt_um_tnt_mosbius.lef` entsprechend dem 3x2 Kachellayout.

- [ ] **3.4 Prüfung unzulässiger Layer (Layer Check)**
  - [ ] **3.4.1** Überprüfen, dass keine verbleibenden SkyWater 130 Layer-IDs im GDS vorhanden sind.
  - [ ] **3.4.2** Verifizierung, dass alle verbleibenden Geometrien ausschließlich gültigen IHP SG13G2 Layern zugeordnet sind (Metal1=67/20, Metal2=68/20, Metal3=69/20, Metal4=70/20, Metal5=71/20, etc.).

---

## Phase 4: Behebung kaskadierender Analog-Pin- & Boundary-Fehler

> **Ziel:** Erfolgreicher Abschluss der Analog-Pin-Prüfung und Boundary-Überprüfung nach Behebung von Phase 2 und Phase 3.

- [ ] **4.1 Verifikation der Analog-Pin-Platzierung (`ua[0]` bis `ua[5]`)**
  - [ ] **4.1.1** Abgleich der Analog-Pin-Koordinaten im GDS/LEF mit den Vorgaben des Templates `tt_analog_3x2_3v3.def`.
  - [ ] **4.1.2** Bestätigen, dass Pin-Namen (`ua[0]` bis `ua[5]`) und Pin-Richtungen mit den Deklarationen in `info.yaml` übereinstimmen.

- [ ] **4.2 Boundary Check Bestätigung**
  - [ ] **4.2.1** Verifizieren, dass die äußere Chip-Boundary exakt auf das 3x2 Tile-Template ausgerichtet ist.

---

## Phase 5: Lokale Verifikation, CI/CD-Precheck & Validierung

> **Ziel:** Lokale Vorab-Tests durchführen und grünen Precheck-Status im GitHub Actions CI/CD-Lauf nachweisen.

- [ ] **5.1 Lokale Testausführung**
  - [ ] **5.1.1** Ausführen von `make check` zur statischen Verifikation aller Konfigurationen und Synthese-Stubs.
  - [ ] **5.1.2** Ausführen von `make lint` zur Überprüfung der Verilog-Syntax.
  - [ ] **5.1.3** Ausführen der Python-UnitTest-Suite: `python3 -m unittest discover -s py`.

- [ ] **5.2 CI/CD Pipeline-Ausführung & Precheck-Audit**
  - [ ] **5.2.1** Push der Änderungen auf den Remote-Branch zur Ausführung der Workflows.
  - [ ] **5.2.2** Überwachung der Job-Ergebnisse im `precheck`-Schritt in GitHub Actions.
  - [ ] **5.2.3** Bestätigen der grünen Haken für alle Precheck-Teilprüfungen:
    - [ ] KLayout pin label overlapping drawing: ✅ Pass
    - [ ] KLayout SG13G2 DRC: ✅ Pass
    - [ ] KLayout zero area: ✅ Pass
    - [ ] KLayout Checks (`prBoundary`): ✅ Pass
    - [ ] Pin check: ✅ Pass
    - [ ] Boundary check: ✅ Pass
    - [ ] Layer check: ✅ Pass
    - [ ] Cell name check: ✅ Pass
    - [ ] Analog pin check: ✅ Pass
    - [ ] Verilog syntax check: ✅ Pass
