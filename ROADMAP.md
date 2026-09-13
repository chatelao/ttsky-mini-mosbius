# Migration Roadmap: Porting Mini-MOSbius from SKY130 to IHP SG13G2

This roadmap outlines the phased execution plan for migrating Sylvain Munaut's (246tnt) variant of **Mini-MOSbius** from SkyWater 130nm (`sky130A`) to the **IHP SG13G2 130nm BiCMOS** (`sg13g2`) process for TinyTapeout shuttles.

The top priority is establishing and maintaining a functioning **CI/CD pipeline as early as possible** to ensure continuous integration, automated builds, and prevention of design/tooling "drift".

---

## Migration Overview & Key Priorities

1. **Continuous Integration First:** Update GitHub Actions workflows (`.github/workflows/`) to target SG13G2 immediately so that every incremental change is verified by automated CI runs.
2. **Voltage Domain Adaptation:** Shift digital core power ($V_{DPWR}$) from 1.8V to 1.2V while maintaining analog power ($V_{APWR}$) at 3.3V, introducing 1.2V to 3.3V level shifters (`tt_lvl_shift`).
3. **Primitive & Cell Re-binding:** Transition primitive models from `sky130_fd_pr` to `sg13g2_pr` and digital logic from `sky130_fd_sc_hd` to `sg13g2_stdcell`.
4. **Procedural Layout Scripting:** Update Python layout generator scripts (`py/common.py`, `gen_asw_ctrl.py`, `gen_dev_ctrl.py`) for IHP grid/pitch dimensions and decap cell definitions.

---

## Phase 1: CI/CD Pipeline Infrastructure & Target Setup (High Priority)

> **Objective:** Ensure automated build and check actions run early and continuously on all commits to prevent design drift.

- [x] **1.1 Update GitHub Workflows for IHP Target**
  - Update `.github/workflows/gds.yaml` and `docs.yaml` to reference IHP SG13G2 action templates / PDK configuration (`pdk: ihp-sg13g2`, `@ttihp26b` action tags).
  - Configure GitHub Pages deployment source to "GitHub Actions" and declare explicit token authorization scopes (`permissions: pages: write`, `permissions: id-token: write`).
  - Ensure CI triggers properly on push and pull requests to catch breaking changes immediately.
- [x] **1.2 Update Metadata & Pinout Definition**
  - Update `info.yaml` to conform to TinyTapeout IHP shuttle pinout and voltage requirements (1.2V $V_{DPWR}$, 3.3V $V_{APWR}$).
- [x] **1.3 Establish Automated Verification Stubs**
  - Add basic Makefile lint and synthesis check targets to be executed in CI.
  - Implement static CI/CD workflow parameter verification (`py/verify_cicd_config.py`) and unit test suite (`py/test_verify_cicd_config.py`).

---

## Phase 2: Schematic Capture & Primitive Device Model Re-binding

> **Objective:** Transition circuit schematics and simulation testbenches from SkyWater 130nm primitives to IHP SG13G2 models.

- [ ] **2.1 Re-bind Primitive Devices in Xschem (`xschem/`)**
  - Replace `sky130_fd_pr__nfet_g5v0d10v5` and `pfet_g5v0d10v5` with `sg13g2_pr__nfet33` and `pfet33` in all sub-block schematics (`diff_n.sch`, `diff_p.sch`, `mirror_n.sch`, `mirror_p.sch`, `ota_n.sch`, `nmos_prog.sch`, `pmos_prog.sch`).
  - Scale device W/L dimensions to achieve parity in $R_{on}$, transconductance, and drive current.
- [ ] **2.2 Analog Switch & Level Shifter Adaptation**
  - Update 3.3V transmission gate switches (`tt_asw_3v3.sch`) for `nfet33`/`pfet33`.
  - Re-design/re-bind level shifters (`tt_lvl_shift`) for 1.2V (digital) to 3.3V (analog) signal translation.
- [ ] **2.3 Top-Level Analog Schematic Entry (`xschem/mosbius.sch`)**
  - Re-wire top-level analog block hierarchy with updated SG13G2 symbols.
- [ ] **2.4 Ngspice Simulation & Testbench Verification**
  - Update Ngspice model includes in `xschem/tb_*.sch` to reference IHP SG13G2 corner models (`corner.spice` / `sg13g2.lib`).
  - Run transient and DC operating point simulations on OTAs, mirrors, and switch matrix paths.

---

## Phase 3: Digital Logic Re-Synthesis & Cell Mapping

> **Objective:** Re-target digital shift register control infrastructure (`ctrl_top.v`, `ctrl_block.v`) to IHP standard cells.

- [ ] **3.1 Update Verilog Standard Cell Definitions**
  - Update `src/stdcells.v` to declare `sg13g2_stdcell_*` primitives (`sg13g2_and2_1`, `sg13g2_inv_1`, `sg13g2_buf_2`, `sg13g2_dfrpc_1`, `sg13g2_tiel_1`, etc.).
- [ ] **3.2 Synthesis Toolchain Adaptation (`src/Makefile`)**
  - Update Yosys synthesis scripts in `src/Makefile` to target `sg13g2_stdcell.v` target library.
- [ ] **3.3 Functional RTL Simulation**
  - Run Verilog simulation of 192-bit control bitstream shift register chain under 1.2V timing/lib parameters.

---

## Phase 4: Procedural Layout Generator Adaptation (`py/`)

> **Objective:** Adapt Python layout placement and decap generation scripts for SG13G2 geometries.

- [ ] **4.1 Update Grid & Pitch Parameters (`py/common.py`)**
  - Update `ROW_PITCH` and `COL_PITCH` according to `sg13g2_stdcell` LEF specifications.
  - Update horizontal (`TRACK_H_*`) and vertical (`TRACK_V_*`) track pitch, offsets, and widths for SG13G2 Metal 1 and Metal 2 layers.
  - Update `VIAS` stack dictionary for SG13G2 `met1`, `met2`, and `met3` contacts.
- [ ] **4.2 Decap & Filler Instantiation Update (`py/gen_asw_ctrl.py`, `py/gen_dev_ctrl.py`)**
  - Re-target cell references to `sg13g2_decap_4`, `sg13g2_decap_8`, `sg13g2_fill_1`, and `sg13g2_fill_2`.
  - Regenerate `.decap.v` files for ASW column controllers (`ctrl_asw.decap.v`) and device controllers (`ctrl_dev_*.decap.v`).
- [ ] **4.3 GDS Post-Processing (`py/fix_gds.py`)**
  - Adapt GDS cell structure fixup script for SG13G2 layer mapping conventions.

---

## Phase 5: Physical Layout Assembly & Physical Verification

> **Objective:** Generate full GDS/LEF layout, verify DRC/LVS compliance, and extract parasitic models.

- [ ] **5.1 Layout Migration in KLayout / Magic VLSI (`mag/`)**
  - Re-layout analog switch matrix (`asw_matrix.mag`) and sub-blocks using SG13G2 design rules.
  - Assemble top-level design (`tt_um_tnt_mosbius.mag`).
- [ ] **5.2 Design Rule Checking (DRC)**
  - Execute DRC checks using KLayout DRC (`sg13g2.lydrc`) and Magic DRC (`tcl/magic_drc.tcl`).
  - Resolve all spacing, width, and enclosure violations.
- [ ] **5.3 Layout vs. Schematic (LVS)**
  - Extract SPICE netlist from layout using Magic/KLayout LVS scripts.
  - Run Netgen LVS (`tcl/lvs.tcl` / `sg13g2.lylvs`) across 1.2V digital and 3.3V analog domains until zero mismatches remain.
- [ ] **5.4 Parasitic Extraction (PEX) & Final Sign-Off**
  - Perform PEX using SG13G2 tech files (`tcl/magic_extract_pex.tcl`).
  - Perform post-layout simulation to confirm analog dynamic range and switch $R_{on}$.
  - Generate clean GDS (`gds/tt_um_tnt_mosbius.gds`) and LEF (`lef/tt_um_tnt_mosbius.lef`).
  - Confirm green status on CI/CD pipeline!
