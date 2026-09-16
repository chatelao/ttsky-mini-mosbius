# Producible Files & Process Steps Catalogue (`CATALOGUE.md`)

This catalogue lists all process steps, tool actions, and files produced by this repository for lab/TinyTapeout shuttle manufacturing, along with the precheck verification status and specific failure reasons for each artifact.

---

## Process Steps & Produced Files Table

| Step # | Process / Workflow Step | Tool / Action | Produced File(s) | File Description | Precheck Verification Status | Failing Precheck Check / Exact Error Reason |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **1** | **Project Configuration & Metadata Definition** | Manual / `info.yaml` | `info.yaml` | TinyTapeout project metadata (top module, tile count `3x2`, analog pins `6`, power domains `uses_vapwr: true`, pinout mapping) | ❌ **Fail** | **Precheck DEF/pin config check:** Mismatch when `analog_pins` count or `ua[...]` definitions do not align with 3x2 DEF template or missing `language: Analog`. |
| **2** | **Digital Logic RTL Synthesis & Decap Generation** | Yosys & Python (`py/gen_asw_ctrl.py`, `py/gen_dev_ctrl.py`) | `src/ctrl_asw.decap.v`<br>`src/ctrl_dev_*.decap.v`<br>`src/ctrl_top.synth.v` | Synthesized digital control netlists and decoupling capacitor stubs | ❌ **Fail** | **Standard Cell Declarations Check:** Fails if Verilog source/decap files contain legacy SkyWater `sky130_fd_sc_hd` standard cell references instead of IHP `sg13g2_*` cells. |
| **3** | **Layout Design & GDS Extraction** | Magic VLSI (`mag/tt_um_tnt_mosbius.mag`, `tcl/update_gds_lef.tcl`) | `gds/tt_um_tnt_mosbius.gds` | Primary binary GDSII physical layout stream for foundry mask manufacturing | ❌ **Fail** | 1. **KLayout PR Boundary Check:** `prBoundary.boundary (189/4) layer not found in tt_um_tnt_mosbius.gds` (contains legacy SkyWater `(235, 4)` instead).<br>2. **Layer Check:** `Invalid layers in GDS: {(68, 20), (69, 20), (70, 20), (71, 20), (235, 4), ...}` (SkyWater 130 layers present instead of IHP SG13G2 layers). |
| **4** | **LEF Macro Abstract Generation** | Magic VLSI (`tcl/update_gds_lef.tcl`) | `lef/tt_um_tnt_mosbius.lef` | Abstract Library Exchange Format (LEF) file defining macro size, tile area, and pin geometries | ❌ **Fail** | **LEF Pin & Boundary Check:** Fails if macro size is invalid (`0.0 x 0.0`) or missing required PIN declarations (`ua[0]`..`ua[5]`, `clk`, `ena`, `rst_n`). |
| **5** | **Precheck Tile Template Resolution** | GitHub Actions (`precheck@ttihp26b`) | `tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def` | Submodule DEF template file establishing 3x2 analog tile boundaries and pin placement rules | ❌ **Fail** | **Pin Check / Boundary Check / Analog Pin Check:** `[Errno 2] No such file or directory: '../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def'`. Relative path resolution failed in `tt/precheck` subdirectory due to missing tech directory copies (`tt/tech` and `tt/precheck/tech`). |
| **6** | **Documentation & Preview Generation** | GitHub Actions (`docs@ttihp26b`, `viewer@ttihp26b`) | `docs/info.md`<br>`docs/index.html`<br>`docs/gds.png` | Project documentation, 3D render preview, and datasheet pages for lab website | ❌ **Fail** | **Docs Build & Asset Config Check:** Fails if `docs/info.md` is missing `## How it works` or `## How to test` sections, or if workflow uses legacy action tags (`ttsky26c` instead of `@ttihp26b`). |

---

## Detailed Check Summary

1. **`gds/tt_um_tnt_mosbius.gds`**:
   - **KLayout PR Boundary Check:** ❌ Failed (`prBoundary (189/4)` layer missing; legacy `(235, 4)` present).
   - **Layer Check:** ❌ Failed (Invalid SkyWater 130 layers `(68,20)`, `(69,20)`, `(70,20)`, `(71,20)`, `(235,4)`, etc.).
   - **KLayout SG13G2 DRC:** ✅ Passed.
   - **KLayout Zero Area Check:** ✅ Passed.
   - **Cell Name Check:** ✅ Passed (`tt_um_tnt_mosbius`).

2. **`tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def`**:
   - **Pin Check:** ❌ Failed (`FileNotFoundError: '../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def'`).
   - **Boundary Check:** ❌ Failed (`FileNotFoundError: '../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def'`).
   - **Analog Pin Check:** ❌ Failed (Cascading failure from missing DEF template path resolution).

3. **`lef/tt_um_tnt_mosbius.lef`**:
   - **LEF Pin & Boundary Check:** ❌ Failed when macro size or pin definitions are missing or unmapped.

4. **`info.yaml`**:
   - **Precheck DEF/Pin Config:** ❌ Failed if `tiles: "3x2"`, `analog_pins: 6`, `uses_vapwr: true`, or `language: Analog` settings are missing or inconsistent.

5. **`docs/info.md`**:
   - **Docs Build Check:** ❌ Failed if required markdown headers (`## How it works`, `## How to test`) are missing.
