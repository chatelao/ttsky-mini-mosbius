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
  - Update `.github/workflows/gds.yaml` and `docs.yaml` to reference IHP SG13G2 action templates / PDK configuration (`pdk: ihp-sg13g2`).
  - Update all action steps (`custom_gds`, `precheck`, `viewer`, `docs`) to mandate explicit `@ttihp26b` release tags.
  - Configure GitHub Pages deployment source (`GitHub Actions`) and mandate explicit OIDC token permissions (`pages: write`, `id-token: write`) on the `viewer` job to prevent deployment HTTP 404 errors.
  - Ensure CI triggers properly on push and pull requests to catch breaking changes immediately.
- [x] **1.2 Update Metadata & Pinout Definition**
  - Update `info.yaml` to conform to TinyTapeout IHP shuttle pinout and voltage requirements (1.2V $V_{DPWR}$, 3.3V $V_{APWR}$).
- [x] **1.3 Establish Automated Verification Stubs**
  - Integrate static CI/CD workflow parameter checks (`py/verify_cicd_config.py`) and Python unit test suites (`py/test_verify_cicd_config.py`) into `make check` alongside Verilog synthesis and lint checks.

---

## Phase 2: Schematic Capture & Primitive Device Model Re-binding

> **Objective:** Transition circuit schematics and simulation testbenches from SkyWater 130nm primitives to IHP SG13G2 models.

- [ ] **2.1 Re-bind Primitive Devices in Xschem (`xschem/`)**
  - [ ] **2.1.1 Re-bind NMOS differential pair schematic (`xschem/diff_n.sch`)**
    - Replace `sky130_fd_pr__nfet_g5v0d10v5` symbol references with `sg13g2_pr__nfet33` (or equivalent SG13G2 3.3V NMOS primitive).
    - Update transistor width/length parameters for SG13G2 process rules.
  - [ ] **2.1.2 Re-bind PMOS differential pair schematic (`xschem/diff_p.sch`)**
    - Replace `sky130_fd_pr__pfet_g5v0d10v5` symbol references with `sg13g2_pr__pfet33` (or equivalent SG13G2 3.3V PMOS primitive).
    - Adjust PMOS aspect ratios ($W/L$) for target transconductance matching.
  - [ ] **2.1.3 Re-bind NMOS current mirror schematic (`xschem/mirror_n.sch`)**
    - Transition current mirror primitives to `sg13g2_pr__nfet33`.
    - Set device dimensions to preserve mirror ratio and headroom.
  - [ ] **2.1.4 Re-bind PMOS current mirror schematic (`xschem/mirror_p.sch`)**
    - Transition current mirror primitives to `sg13g2_pr__pfet33`.
    - Adjust device sizing for desired bias currents under SG13G2 model parameters.
  - [ ] **2.1.5 Re-bind operational transconductance amplifier (`xschem/ota_n.sch`)**
    - Re-bind internal diff pair and mirror transistors to SG13G2 3.3V primitives.
    - Scale device geometries to maintain open-loop gain and bandwidth targets.
  - [ ] **2.1.6 Re-bind programmable NMOS array block (`xschem/nmos_prog.sch`)**
    - Replace SkyWater 130nm NFET primitives with `sg13g2_pr__nfet33`.
    - Verify array device pin connections and parameters.
  - [ ] **2.1.7 Re-bind programmable PMOS array block (`xschem/pmos_prog.sch`)**
    - Replace SkyWater 130nm PFET primitives with `sg13g2_pr__pfet33`.
    - Update symbol device properties and instance names.
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

- [x] **3.1 Update Verilog Standard Cell Definitions**
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
