# Audit-Bericht: Precheck-Fehlgeschlagen (`ADUIT_PRECHECK_FAIL.md`)

## Executive Summary
Dieser Bericht analysiert die Ursachen für das Fehlschlagen des **Tiny Tapeout Precheck**-Jobs in der GitHub Actions Pipeline (Workflow Job Run `a18ab1e1-065b-5e56-8406-f88ca5b77d1c` / GitHub Action Run `34826069721` sowie spätere Läufe).

Obwohl die Action-Version korrekt auf `@ttihp26b` für die **IHP SG13G2** PDK-Technologie eingestellt war, schlug der Precheck bei KLayout SG13G2 DRC mit **20.439 DRC-Verletzungen** fehl. Die Hauptursache liegt in den fundamentalen physischen Layout- und Geometrieregel-Unterschieden zwischen **SkyWater 130nm (`sky130A`)** und **IHP SG13G2 (`sg13g2`)**.

---

## 1. Übersicht der Precheck-Ergebnisse

Die folgende Tabelle fasst die Ergebnisse des Precheck-Laufs aus den CI/CD-Protokollen zusammen:

| Überprüfung (Check) | Status | Fehlermeldung / Details |
| :--- | :---: | :--- |
| **KLayout pin label overlapping drawing** | ✅ Pass | Keine Überlappungsfehler gefunden |
| **KLayout SG13G2 DRC** | ❌ Fail | `Klayout sg13g2 failed with 20439 DRC violations` |
| **KLayout zero area** | ✅ Pass | Keine Null-Flächen-Objekte vorhanden |
| **KLayout Checks** | ✅ Pass | `prBoundary` Layer `189/4` korrekt vorhanden |
| **Pin check** | ❌ Fail | `[Errno 2] No such file or directory: '../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def'` (vor Symlink-Fix) |
| **Boundary check** | ❌ Fail | `[Errno 2] No such file or directory: '../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def'` (vor Symlink-Fix) |
| **Layer check** | ❌ Fail | `Invalid layers in GDS: {(125, 2), (125, 25), (1, 25)}` (vor `fix_gds.py` Layer-Fix) |
| **Cell name check** | ✅ Pass | Top-Modulname `tt_um_tnt_mosbius` stimmt überein |
| **Analog pin check** | ❌ Fail | Folgefehler wegen fehlender DEF-Template-Datei |
| **Verilog syntax check** | ✅ Pass | SystemVerilog Parsing via Yosys erfolgreich |

---

## 2. Detaillierte Ursachenanalyse der KLayout SG13G2 DRC-Verletzungen

### Ursache 1: Physische Geometrie- & Pitch-Differenzen (SkyWater 130 vs. IHP SG13G2)
* **Standard-Zellen Row-Height & Pitch:**
  - SkyWater 130 HD (`sky130_fd_sc_hd`): Zeilenhöhe beträgt **2,72 µm** bei einer Site-Breite von **0,46 µm**.
  - IHP SG13G2 Standardzelle (`sg13g2_stdcell`): Zeilenhöhe beträgt **3,78 µm** bei einer Site-Breite von **0,48 µm**.
  - **Konsequenz:** Die physischen Platzierungen in `mag/*.mag` wurden für das 2,72 µm Raster von SkyWater 130 berechnet. Standardzellen und Overlap-Geometrien passen physisch nicht in das 3,78 µm IHP SG13G2 Standardzell-Raster.

* **Metal-Stack & DRC-Abstandsregeln:**
  - **Metal1 / Metal2 / Metal3 Minimum Width & Spacing:** IHP SG13G2 fordert spezifische Mindestbreiten, Enclosure-Regeln und Mindestabstände für `Metal1` (Layer 8/0), `Metal2` (Layer 30/0), `Metal3` (Layer 50/0), `Metal4` (Layer 67/0) und `Metal5` (Layer 125/0).
  - **Via-Enclosure & Contacts:** Die Overhang- und Enclosure-Anforderungen für `cont`, `via1`, `via2`, `via3`, `via4` unterscheiden sich deutlich von den `viali`, `m2c`, `m3c` Regeln in SkyWater 130.
  - **Well & Substrate Taps:** NWell-Abstände (Layer 31/0) und Substratkontakte (`sg13g2_tap_1`) folgen in IHP SG13G2 anderen Latch-up- und DRC-Isolationsregeln.

### Ursache 2: Einschränkung von Binärem Layer-Remapping (`py/fix_gds.py`)
* **Arbeitsweise des Remapping-Skripts:**
  `py/fix_gds.py` ist ein reiner GDSII-Stream-Remapper. Es ändert lediglich die **Layer- und Datatype-Header-Bytes** in den GDSII-Einträgen (z. B. Umbenennung von Layer 67/20 in Layer 8/0).
* **Warum Remapping DRC-Fehler nicht beheben kann:**
  - Binäres Remapping **skaliert, verschiebt, verbreitert oder resized keine Polygon-Koordinaten**.
  - Sämtliche Rechteck-Koordinaten (`XY`-Einträge) verbleiben exakt auf den ursprünglichen SkyWater 130 Dimensionswerten.
  - Wenn das KLayout SG13G2 DRC-Deck (`sg13g2.lydrc`) auf dem remapped GDS ausgeführt wird, werden die unberührten SkyWater-Polygone gegen die IHP SG13G2 Entwurfsregeln geprüft. Dies führt zu **20.439 DRC-Verletzungen** (Spacings, Overlaps, Enclosures, Grid-Violations).

---

## 3. Toolchain-Einschränkungen & Empfohlener Lösungsweg (Remediation Strategy)

### 3.1 Umgebungs- & Toolchain-Restriktionen im Sandbox-Runner
Für ein DRC-cleanes Layout auf IHP SG13G2 wird eine vollständige EDA-Toolchain benötigt:
1. **Magic VLSI / KLayout** mit geladenem IHP SG13G2 PDK (`sg13g2.tech`).
2. **Yosys Synthesis Toolchain** zur Synthese des digitalen Steuerungsteils (`src/ctrl_top.v`, `src/ctrl_block.v`) für `sg13g2_stdcell`.
3. **Procedural Layout Script Execution (`py/common.py`, `py/gen_*_ctrl.py`)**: Skripte müssen mit IHP `ROW_PITCH` (3,78 µm) und IHP Cell Widths ausgeführt werden.

Da EDA-Tools wie Magic VLSI, Yosys und KLayout im aktuellen Sandbox-CI-Environment nicht vorinstalliert sind, muss die Neugenerierung in einer vorbereiteten PDK-Arbeitsumgebung durchgeführt werden.

### 3.2 Schritte für die vollständige DRC-Clean Migration

1. **Synthese & RTL-Anpassung:**
   - RTL mit Yosys unter Nutzung der IHP SG13G2 Liberty/Standard-Cell-Library (`sg13g2_stdcell.lib`) neu synthetisieren.
2. **Procedural Placement Anpassung (`py/common.py`):**
   - `ROW_PITCH` von 2,72 µm auf **3,78 µm** anpassen.
   - `COL_PITCH` von 0,46 µm auf **0,48 µm** anpassen.
   - Standardzell-Definitionen auf `sg13g2_stdcell_*` und `sg13g2_decap_*` aktualisieren.
3. **Magic / KLayout Layout-Regenerierung:**
   - Layout in Magic VLSI unter Verwendung von `sg13g2.tech` neu aufbauen oder KLayout Python API zur automatisierten DRC-cleanen Platzierung nutzen.
4. **DRC- & LVS-Verifikation:**
   - KLayout DRC (`sg13g2.lydrc`) lokal ausführen und 0 Fehler verifizieren.
   - Netgen LVS mit `sg13g2_setup.tcl` durchführen.
5. **GDS & LEF Export:**
   - Neues DRC-cleanes GDSII und LEF nach `gds/tt_um_tnt_mosbius.gds` bzw. `lef/tt_um_tnt_mosbius.lef` exportieren.
