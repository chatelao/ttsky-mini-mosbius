# Audit-Bericht: Precheck-Fehlgeschlagen (`ADUIT_PRECHECK_FAIL.md`)

## Executive Summary
Dieser Bericht analysiert die Ursachen für das Fehlschlagen des **Tiny Tapeout Precheck**-Jobs in der GitHub Actions Pipeline (Workflow Job Run `a18ab1e1-065b-5e56-8406-f88ca5b77d1c` / GitHub Action Run `34826069721`).

Obwohl die Action-Version korrekt auf `@ttihp26b` für die **IHP SG13G2** PDK-Technologie eingestellt war, schlug der Precheck bei mehreren Überprüfungen fehl. Die Hauptursache liegt in einem **Technologie-Koppelungsfehler (SkyWater 130 vs. IHP SG13G2)** in dem eingereichten GDS-Artefakt sowie in einem Pfadauflösungsfehler des Precheck-Tools bezüglich des analogen DEF-Templates.

---

## 1. Übersicht der Precheck-Ergebnisse

Die folgende Tabelle fasst die Ergebnisse des Precheck-Laufs aus den CI/CD-Protokollen zusammen:

| Überprüfung (Check) | Status | Fehlermeldung / Details |
| :--- | :---: | :--- |
| **KLayout pin label overlapping drawing** | ✅ Pass | Keine Überlappungsfehler gefunden |
| **KLayout SG13G2 DRC** | ✅ Pass | Keine SG13G2 DRC-Verletzungen gefunden |
| **KLayout zero area** | ✅ Pass | Keine Null-Flächen-Objekte vorhanden |
| **KLayout Checks** | ❌ Fail | `prBoundary.boundary (189/4) layer not found in tt_um_tnt_mosbius.gds` |
| **Pin check** | ❌ Fail | `[Errno 2] No such file or directory: '../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def'` |
| **Boundary check** | ❌ Fail | `[Errno 2] No such file or directory: '../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def'` |
| **Layer check** | ❌ Fail | `Invalid layers in GDS: {(64, 5), (95, 20), (71, 20), (64, 20), (67, 16), (68, 5), (75, 20), (68, 20), (66, 20), (64, 59), (71, 16), (81, 23), (66, 44), (64, 16), (70, 5), (68, 44), (125, 20), (94, 20), (70, 20), (236, 0), (235, 4), (65, 20), (81, 4), (70, 44), (68, 16), (83, 44), (67, 5), (65, 44), (67, 20), (70, 16), (69, 20), (67, 44), (78, 44), (66, 15), (71, 5), (69, 44), (122, 16), (93, 44)}` |
| **Cell name check** | ✅ Pass | Top-Modulname `tt_um_tnt_mosbius` stimmt überein |
| **Analog pin check** | ❌ Fail | Folgefehler wegen fehlender DEF-Template-Datei |
| **Verilog syntax check** | ✅ Pass | SystemVerilog Parsing via Yosys erfolgreich |

---

## 2. Detaillierte Ursachenanalyse (Root Cause Analysis)

### Ursache 1: GDS Layer-Map Mismatch (SkyWater 130 vs. IHP SG13G2)
* **Symptom:**
  `Invalid layers in GDS: {(64, 5), (68, 20), (69, 20), (70, 20), (71, 20), (235, 4), ...}`
* **Analyse:**
  Die im eingereichten GDS-Artefakt (`tt_submission/tt_um_tnt_mosbius.gds`) vorhandenen Layer-Nummern entsprechen der **SkyWater 130nm (`sky130A`) PDK Layer-Map**:
  - `(68, 20)`: Sky130 `met1.drawing`
  - `(69, 20)`: Sky130 `met2.drawing`
  - `(70, 20)`: Sky130 `met3.drawing`
  - `(71, 20)`: Sky130 `met4.drawing`
  - `(235, 4)`: Sky130 `prBoundary.boundary`
  - `(64, 20)`: Sky130 `nwell.drawing`
  - `(65, 20)`: Sky130 `diff.drawing`
  - `(67, 20)`: Sky130 `li1.drawing`
* **Auswirkung:**
  Der IHP SG13G2 Precheck erwartet IHP-spezifische Layer (z. B. Met1=67/20, Met2=69/20, Met3=70/20, Met4=71/20, Met5=72/20, PR Boundary=189/4). Da das GDS für Sky130 generiert wurde, erkennt der IHP-Layercheck alle Sky130-Layer als unzulässig/ungültig.

---

### Ursache 2: Fehlendes `prBoundary` Layer `189/4`
* **Symptom:**
  `KLayout Checks: Fail: prBoundary.boundary (189/4) layer not found in tt_um_tnt_mosbius.gds`
* **Analyse:**
  In IHP SG13G2 ist das `prBoundary` auf Layer `189`, Datatype `4` definiert. Das geprüfte GDS enthielt jedoch das Sky130 Boundary-Layer `(235, 4)`. Dadurch schlug die Geometrie- und Boundary-Prüfung von KLayout für IHP SG13G2 fehl.

---

### Ursache 3: Pfadauflösungsfehler für DEF-Template (`tt_analog_3x2_3v3.def`)
* **Symptom:**
  `Pin check / Boundary check: Fail: [Errno 2] No such file or directory: '../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def'`
* **Analyse:**
  Während der Ausführung von `precheck.py` innerhalb der `nix-shell` versuchte das Precheck-Skript aus `tt-support-tools`, das Template-DEF unter dem relativen Pfad `../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def` zu öffnen. Aufgrund der Arbeitsverzeichnisstruktur im Runner (`/home/runner/work/ttsky-mini-mosbius/ttsky-mini-mosbius/tt/precheck`) schlug der relative Dateizugriff mit `FileNotFoundError` fehl.

---

### Ursache 4: Kaskadierender Fehler beim Analog Pin Check
* **Symptom:**
  `Analog pin check: Fail:`
* **Analyse:**
  Der Analog-Pin-Check vergleicht die Pin-Positionen im GDS/LEF mit den Vorgaben aus der Template-DEF-Datei. Da das Laden der Datei `tt_analog_3x2_3v3.def` fehlgeschlagen war (Ursache 3), brach der Analog-Pin-Check ab.

---

## 3. Maßnahmen zur Behebung (Remediation Steps)

1. **Neugenerierung des GDS- & LEF-Layouts für IHP SG13G2:**
   - Das Layout muss mit dem IHP SG13G2 PDK (`sg13g2.tech` für Magic VLSI) neu kompiliert/exportiert werden, sodass alle Komponenten die korrekten IHP-Layer (z. B. Met1=67/20, PR Boundary=189/4) nutzen.
2. **Aktualisierung der Support-Tools & Template-DEF-Pfade:**
   - Sicherstellen, dass das Tag `TinyTapeout/tt-gds-action@ttihp26b` in allen Workflows (`.github/workflows/gds.yaml` und `docs.yaml`) verwendet wird und die Pfade im Tool-Repository `tt-support-tools` korrekt aufgelöst werden.
3. **Lokale Verifikation vor dem Commit:**
   - Ausführen von `make check` und `python3 py/verify_cicd_config.py` zur statischen Verifikation der CI/CD-Konfiguration.
