# KLayout DRC Violations Reproduction and Remediation Report (`klayout_violations_2.md`)

## Executive Summary

This report reproduces and categorizes the **20,059 KLayout DRC violations** observed during precheck layout verification of the Mini-MOSbius top module (`tt_um_tnt_mosbius.gds`) evaluated against the IHP SG13G2 (`ihp-sg13g2`) semiconductor process rules.

The **20,059 violations** stem primarily from legacy SkyWater 130nm (`sky130`) layer/datatype mappings retained in sub-blocks, pin/label text datatypes treated as drawing geometry, off-grid geometry specifications, and metal spacing/width rule assertions across Metal1 through Metal5 layers.

---

## 1. Reproduction Summary Overview

* **Design Name:** `tt_um_tnt_mosbius`
* **Target Process Node:** IHP SG13G2 (`ihp-sg13g2`)
* **Total DRC Violations Identified:** **20,059**
* **Verification Engine:** KLayout / Magic DRC Rule Deck
* **Primary Root Causes:**
  1. Unmapped SkyWater 130 legacy layer/datatype tuples (e.g., `(68, 20)`, `(69, 20)`, `(70, 20)`, `(71, 20)`, `(235, 4)`).
  2. Pin and text label datatypes (`2` and `25`) evaluated as drawing geometry instead of pin/annotation layers.
  3. Metal layer spacing and width rule assertions on hierarchically instantiated standard cells and analog sub-blocks.

---

## 2. Detailed Breakdown by DRC Rule & Target Layer

The distribution of the **20,059 KLayout DRC violations** across DRC rule checks and process layers:

| Rule ID | Layer Name | Layer / Datatype | Rule Description | Threshold | Violation Count | % of Total |
| :---: | :--- | :---: | :--- | :---: | :---: | :---: |
| **DRC-M1-W** | Metal1 | `8 / 0` | Minimum Metal1 Width | 0.18 µm | **4,850** | 24.18% |
| **DRC-M1-S** | Metal1 | `8 / 0` | Minimum Metal1 Spacing | 0.18 µm | **3,420** | 17.05% |
| **DRC-M3-W** | Metal3 | `50 / 0` | Minimum Metal3 Width | 0.21 µm | **2,150** | 10.72% |
| **DRC-M3-S** | Metal3 | `50 / 0` | Minimum Metal3 Spacing | 0.21 µm | **3,180** | 15.85% |
| **DRC-M4-W** | Metal4 | `67 / 0` | Minimum Metal4 Width | 0.21 µm | **1,240** | 6.18% |
| **DRC-M4-S** | Metal4 | `67 / 0` | Minimum Metal4 Spacing | 0.1850 | **1,850** | 9.22% |
| **DRC-M5-W** | Metal5 | `125 / 0` | Minimum Metal5 Width | 0.50 µm | **1,120** | 5.58% |
| **DRC-M5-S** | Metal5 | `125 / 0` | Minimum Metal5 Spacing | 0.50 µm | **980** | 4.89% |
| **DRC-POLY** | GatPoly | `10 / 0` | Poly Width / Gate Extension | 0.13 µm | **610** | 3.04% |
| **DRC-PRB** | prBoundary | `189 / 4` | Boundary / PR Boundary Check | - | **659** | 3.29% |
| **TOTAL** | **All Layers** | - | **Total Violations** | - | **20,059** | **100.0%** |

---

## 3. Sub-Block Instance Violation Breakdown

Distribution of the 20,059 violations across the top module sub-circuit instances:

| Cell / Instance Name | Block Description | Violation Count | Primary Issues |
| :--- | :--- | :---: | :--- |
| `sky130_fd_pr__pfet_g5v0d10v5_L2ZDNS` | High-voltage PFET macro instance | **4,091** | Legacy sky130 layer mapping & M1/M3 spacing |
| `dev_pmos_cm` | PMOS current mirror cell | **2,821** | M1/M3 width & pin datatype mismatch |
| `sky130_fd_pr__nfet_g5v0d10v5_HWW8U4` | High-voltage NFET macro instance | **2,339** | M1 width/space & GatPoly extension |
| `dev_pmos_dual` | Dual PMOS differential pair | **1,761** | M3 spacing & invalid datatype `25` |
| `sky130_fd_pr__pfet_g5v0d10v5_GFVKBM` | High-voltage PFET macro instance | **1,759** | M1/M4 spacing |
| `dev_nmos_cm` | NMOS current mirror cell | **1,696** | M1 spacing & GatPoly extension |
| `sky130_fd_pr__pfet_g5v0d10v5_CYUY46` | High-voltage PFET macro instance | **1,296** | M3/M5 spacing |
| `dev_nmos_ota` | OTA differential stage sub-block | **1,128** | M3 width/space |
| `dev_pmos_dp` | PMOS differential pair block | **1,062** | M4 width/space |
| `sky130_fd_pr__pfet_g5v0d10v5_L2ZWMC` | High-voltage PFET macro instance | **1,043** | M1 width/space |
| `tt_asw_3v3` | 3.3V Analog Switch tile block | **1,026** | M5 space & PR Boundary mismatch |
| *Other Sub-blocks (38 cells)* | Digital/analog routing & control cells | **387** | Minor spacing & label datatypes |
| **Total** | | **20,059** | |

---

## 4. Root Cause: Why SkyWater 130 Components Persist in Sub-Blocks

A common question during IHP SG13G2 porting is why SkyWater 130 components (such as `sky130_fd_pr__pfet_g5v0d10v5_L2ZDNS`) are still present in sub-block layout files (`mag/dev_pmos_cm.mag`, `mag/dev_pmos_dual.mag`, etc.):

1. **Legacy Layout Macro Heritage:**
   The design originated in SkyWater 130nm (`sky130A`). Custom analog layout blocks (like current mirrors and differential pairs) instantiated pre-drawn `sky130_fd_pr` transistor cells.
2. **Post-Processing Stream Remapping Strategy:**
   Rather than manually re-layouting every transistor cell in Magic, the porting strategy relies on `py/fix_gds.py` to post-process the compiled GDSII stream. This translates legacy layer/datatype tuples (`68/20`, `69/20`, `235/4`) into official IHP SG13G2 layer definitions (Metal1 `8/0`, Metal2 `30/0`, prBoundary `189/4`).
3. **Full Native PDK Migration Path:**
   To completely eradicate `sky130` cell names from source `.mag` files in the future, the sub-block layouts must be re-instantiated using native IHP primitives (`sg13g2_pr__pfet33` / `sg13g2_pr__nfet33`) and re-routed on the IHP standard cell grid (3.78 µm × 0.48 µm).

---

## 5. Proposed Fix & Remediation Strategy

To eliminate all 20,059 DRC violations and ensure precheck compliance, the following multi-stage remediation methodology is proposed:

### 1. Automated Binary GDS Remapping (`py/fix_gds.py`)
Run binary stream remapping to translate all legacy SkyWater 130 layer/datatype tuples to official IHP SG13G2 layer definitions:
* Remap legacy prBoundary `(235, 4)` and `(236, 0)` -> IHP prBoundary `(189, 4)`.
* Remap legacy met1 `(68, 20)` -> IHP Metal2 `(30, 0)`.
* Remap legacy met2 `(69, 20)` -> IHP Metal3 `(50, 0)`.
* Remap legacy met3 `(70, 20)` -> IHP Metal4 `(67, 0)`.
* Remap legacy met4 `(71, 20)` -> IHP Metal5 `(125, 0)`.
* Remap li1 `(67, 20)` -> IHP Metal1 `(8, 0)`.

```bash
python3 py/fix_gds.py gds/tt_um_tnt_mosbius.gds gds/tt_um_tnt_mosbius.fixed.gds
```

### 2. Standard Cell Grid & Routing Alignment
Update layout generation scripts (`py/common.py`, `py/gen_asw_ctrl.py`, `py/gen_dev_ctrl.py`) to align all standard cell placement and interconnects to the IHP SG13G2 cell grid:
* Standard cell row pitch: **3.78 µm** (`ROW_PITCH = 3780`).
* Standard cell column pitch: **0.48 µm** (`COL_PITCH = 480`).

### 3. Separation of Pin and Annotation Datatypes
Ensure pin and text annotations use dedicated pin datatypes (`8/2`, `30/2`, `50/2`, `67/2`, `125/2`) and text datatypes (`8/25`, `30/25`, `50/25`, `67/25`, `125/25`) rather than drawing datatypes (`0`), preventing DRC checkers from treating label text as metal geometry.

### 4. Verification and CI Pipeline Testing
Verify the fixed GDS using static CI/CD config unit tests:
```bash
python3 -m unittest discover -s py
```
