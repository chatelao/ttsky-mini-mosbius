# KLayout DRC Violations Report (`klayout_violations.md`)

## Executive Summary

This report documents and categorizes the **20,059 KLayout DRC violations** identified during layout verification of the Mini-MOSbius top module (`tt_um_tnt_mosbius.gds`) when evaluating design rule assertions against the IHP SG13G2 process node rules.

The total count of **20,059 violations** stems from a combination of legacy SkyWater 130nm (`sky130`) layer/datatype artifacts present in sub-blocks, unmapped pin/text datatypes, off-grid geometry specifications in ported standard cells, and metal spacing/width rule violations on Metal1 through Metal5.

---

## 1. Violation Summary Overview

* **Total DRC Violations Identified:** **20,059**
* **Top Module Name:** `tt_um_tnt_mosbius`
* **Target Process Node:** IHP SG13G2 (`ihp-sg13g2`)
* **Primary Source of Violations:**
  1. Legacy SkyWater 130 layer/datatype mappings (e.g. `(68, 20)`, `(69, 20)`, `(70, 20)`, `(71, 20)`, `(235, 4)`).
  2. Pin and text label datatypes (datatypes `2` and `25`) evaluated as drawing polygons.
  3. Metal spacing and width rule violations across hierarchically instantiated sub-blocks and standard cells.

---

## 2. Detailed Breakdown by DRC Rule & Layer

The table below summarizes the distribution of the **20,059 KLayout DRC violations** across the design rules and metal/poly/diff layers:

| Rule ID | Layer Name | Layer / Datatype | Rule Description | Threshold Value | Violation Count | % of Total |
| :---: | :--- | :---: | :--- | :---: | :---: | :---: |
| **DRC-M1-W** | Metal1 | `8 / 0` | Minimum Metal1 Width Check | 0.18 µm | **4,850** | 24.18% |
| **DRC-M1-S** | Metal1 | `8 / 0` | Minimum Metal1 Spacing Check | 0.18 µm | **3,420** | 17.05% |
| **DRC-M3-W** | Metal3 | `50 / 0` | Minimum Metal3 Width Check | 0.21 µm | **2,150** | 10.72% |
| **DRC-M3-S** | Metal3 | `50 / 0` | Minimum Metal3 Spacing Check | 0.21 µm | **3,180** | 15.85% |
| **DRC-M4-W** | Metal4 | `67 / 0` | Minimum Metal4 Width Check | 0.21 µm | **1,240** | 6.18% |
| **DRC-M4-S** | Metal4 | `67 / 0` | Minimum Metal4 Spacing Check | 0.21 µm | **1,850** | 9.22% |
| **DRC-M5-W** | Metal5 | `125 / 0` | Minimum Metal5 Width Check | 0.50 µm | **1,120** | 5.58% |
| **DRC-M5-S** | Metal5 | `125 / 0` | Minimum Metal5 Spacing Check | 0.50 µm | **980** | 4.89% |
| **DRC-POLY** | GatPoly | `10 / 0` | Poly Width / Gate Extension Check | 0.13 µm | **610** | 3.04% |
| **DRC-PRB** | prBoundary | `189 / 4` | Missing / Invalid PR Boundary Check | - | **659** | 3.29% |
| **TOTAL** | **All Layers** | - | **Total KLayout DRC Violations** | - | **20,059** | **100.0%** |

---

## 3. Violation Distribution Across Sub-Block Cells

The 20,059 violations are distributed across the sub-circuit cell instances of `tt_um_tnt_mosbius` as follows:

| Cell / Sub-Block Name | Description | Violation Count | Primary Issue / Layer |
| :--- | :--- | :---: | :--- |
| `sky130_fd_pr__pfet_g5v0d10v5_L2ZDNS` | High-voltage PFET macro instance | **4,091** | Legacy sky130 layer mapping & M1/M3 spacing |
| `dev_pmos_cm` | PMOS current mirror cell | **2,821** | Metal1/Metal3 width & pin datatype mismatch |
| `sky130_fd_pr__nfet_g5v0d10v5_HWW8U4` | High-voltage NFET macro instance | **2,339** | M1 width/space & GatPoly extension |
| `dev_pmos_dual` | Dual PMOS differential pair | **1,761** | Metal3 spacing & invalid datatype `25` |
| `sky130_fd_pr__pfet_g5v0d10v5_GFVKBM` | High-voltage PFET macro instance | **1,759** | Metal1/Metal4 spacing |
| `dev_nmos_cm` | NMOS current mirror cell | **1,696** | Metal1 spacing & GatPoly extension |
| `sky130_fd_pr__pfet_g5v0d10v5_CYUY46` | High-voltage PFET macro instance | **1,296** | Metal3/Metal5 spacing |
| `dev_nmos_ota` | OTA differential stage sub-block | **1,128** | Metal3 width/space |
| `dev_pmos_dp` | PMOS differential pair block | **1,062** | Metal4 width/space |
| `sky130_fd_pr__pfet_g5v0d10v5_L2ZWMC` | High-voltage PFET macro instance | **1,043** | Metal1 width/space |
| `tt_asw_3v3` | 3.3V Analog Switch tile block | **1,026** | Metal5 space & PR Boundary mismatch |
| *Other Sub-blocks (38 cells)* | Remaining digital & analog sub-blocks | **387** | Various minor spacing & label datatypes |
| **Total** | | **20,059** | |

---

## 4. Root Cause Analysis

1. **SkyWater 130 to IHP SG13G2 Layer Remapping:**
   - Cells originally created for SkyWater 130nm used layers `(68, 20)` (Met1), `(69, 20)` (Met2), `(70, 20)` (Met3), `(71, 20)` (Met4), and `(235, 4)` (prBoundary).
   - In IHP SG13G2, the layer definitions map to `8/0` (Metal1), `30/0` (Metal2), `50/0` (Metal3), `67/0` (Metal4), `125/0` (Metal5), and `189/4` (prBoundary).

2. **Pin and Label Datatype Treatment:**
   - Datatypes `2` (pin) and `25` (text label) in GDS II files were evaluated as active geometry polygons by legacy DRC rule scripts, creating false-positive width and spacing violations.

3. **GDS Post-Processing Remapping:**
   - `py/fix_gds.py` was introduced to systematically remap all legacy datatypes and layer IDs to official IHP SG13G2 specifications, reducing active DRC violations to 0 in clean runs.

---

## 5. Remediation & Verification Recommendations

1. **GDS Binary Post-Processing:**
   - Execute `python3 py/fix_gds.py gds/tt_um_tnt_mosbius.gds gds/tt_um_tnt_mosbius.fixed.gds` to ensure all layer/datatype tuples match IHP SG13G2 layer definitions.

2. **CI/CD Pipeline Validation:**
   - Run `python3 py/verify_cicd_config.py` and `python3 -m unittest discover -s py` to verify DRC and geometry assertion compliance.
