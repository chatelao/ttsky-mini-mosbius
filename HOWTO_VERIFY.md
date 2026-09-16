# Verification Guide for Mini-MOSbius (IHP SG13G2)

This document provides a step-by-step guide for verifying intermediate and final design results across the analog/digital workflow using **Xschem**, **Magic VLSI**, **Netgen**, **KLayout**, and project Python verification scripts.

---

## 1. Prerequisites & Environment Setup

Before performing schematic simulation, layout extraction, LVS, or DRC verification, verify that your environment has the required tools and PDK path set up:

- **PDK**: IHP SG13G2 (`ihp-sg13g2`)
- **Tools**:
  - **Xschem**: Schematic capture & SPICE netlisting
  - **Ngspice**: Analog SPICE circuit simulation
  - **Magic VLSI**: Layout editing, extraction, DRC, GDS/LEF generation
  - **Netgen**: Layout Versus Schematic (LVS) comparison
  - **KLayout**: GDSII viewer, layer inspection, and signoff DRC
  - **Yosys**: Verilog logic elaboration & synthesis
  - **Python 3**: For GDS layer remapping (`py/fix_gds.py`) and CI configuration checks (`py/verify_cicd_config.py`)

Ensure `PDK_ROOT` environment variable is defined (e.g. `export PDK_ROOT=/path/to/pdk_root`).

### 1.1 Installing and Loading the IHP SG13G2 PDK

To perform local simulation, extraction, LVS, or DRC verification, follow these steps to clone, install, and load the IHP Open PDK (`ihp-sg13g2`):

1. **Clone the IHP Open PDK repository:**
   ```bash
   # Clone the open-source IHP PDK repository into your chosen PDK root directory
   export PDK_ROOT=${HOME}/pdk
   mkdir -p ${PDK_ROOT}
   git clone https://github.com/IHP-GmbH/IHP-Open-PDK.git ${PDK_ROOT}/IHP-Open-PDK
   ```

2. **Set up environment variables:**
   Add the following exports to your shell environment or session script:
   ```bash
   export PDK_ROOT=${HOME}/pdk
   export PDK=ihp-sg13g2
   # If installed in IHP-Open-PDK subdirectory, create a symlink or point directly:
   ln -sfn ${PDK_ROOT}/IHP-Open-PDK/ihp-sg13g2 ${PDK_ROOT}/ihp-sg13g2
   ```

3. **Loading PDK configuration into EDA Tools:**

   - **Magic VLSI:** Point Magic to the PDK technology startup script:
     ```bash
     export MAGIC_RC=${PDK_ROOT}/ihp-sg13g2/libs.tech/magic/ihp-sg13g2.magicrc
     magic -rcfile ${MAGIC_RC}
     ```
   - **Xschem:** Include the IHP symbol library in `xschemrc` or export symbol search path:
     ```bash
     export XSCHEM_SHARE_DIR=${PDK_ROOT}/ihp-sg13g2/libs.tech/xschem
     ```
   - **Netgen (LVS):** Load Netgen setup configuration file:
     ```bash
     netgen -batch lvs ... ${PDK_ROOT}/ihp-sg13g2/libs.tech/netgen/sg13g2_setup.tcl
     ```
   - **KLayout:** Load KLayout technology files and DRC rule scripts:
     ```bash
     klayout -b -r ${PDK_ROOT}/ihp-sg13g2/libs.tech/klayout/drc/sg13g2_drc.lydrc ...
     ```

---

## 2. Schematic Verification & Simulation with Xschem

Xschem is used for captured sub-blocks, top-level schematics, and testbenches in `xschem/`.

### 2.1 Opening and Inspecting Schematics

To launch Xschem with IHP SG13G2 primitive symbols (`sg13g2_pr`):

```bash
cd xschem
xschem mosbius.sch &
```

Key schematic files in `xschem/`:
- `mosbius.sch` / `mosbius.sym`: Top-level analog block schematic and symbol.
- `diff_n.sch`, `diff_p.sch`, `ota_n.sch`, `mirror_n.sch`, `mirror_p.sch`: Micro-blocks and sub-circuit schematics.
- `nmos_prog.sch`, `pmos_prog.sch`: Programmable device cells.
- `tt_asw_3v3.sch`: 3.3V Analog switch cell.

### 2.2 Running Testbench Simulations

To verify DC/AC performance, transfer characteristics, or ring oscillator operating frequency:

1. Open a testbench schematic in Xschem:
   ```bash
   xschem tb_mosbius_dpn_dc.sch
   # Or other testbenches:
   # xschem tb_mosbius_nfeta_vgs.sch
   # xschem tb_mosbius_ota_stab.sch
   # xschem tb_mosbius_ringo.sch
   ```
2. Click **Netlist** (or press `Ctrl+N`) in Xschem to generate the SPICE netlist.
3. Click **Simulate** (or press `Ctrl+S`) to invoke `ngspice`.
4. Inspect waveforms in `ngspice` / `gaw`.

### 2.3 Generating SPICE Netlist for LVS

To export the top-level schematic SPICE netlist required for Netgen LVS:

1. Open `xschem/mosbius.sch` in Xschem.
2. Ensure top-level mode is active and click **Netlist**.
3. Verify that the output SPICE netlist is written to `xschem/simulation/mosbius.spice`.

---

## 3. Layout Extraction & DRC with Magic VLSI

Magic VLSI manages top-level and sub-block `.mag` layout files located in `mag/`.

### 3.1 Loading Layouts and Interactive DRC

To open Magic with the IHP SG13G2 technology setup:

```bash
cd mag
MAGIC_RC=${PDK_ROOT}/ihp-sg13g2/libs.tech/magic/ihp-sg13g2.magicrc
magic -rcfile ${MAGIC_RC} tt_um_tnt_mosbius.mag
```

In the Magic window:
- Press `d` or run `drc check` in the console to evaluate Design Rule Checks interactively.
- Run `drc why` to display error details for selected regions.

### 3.2 Running Batch DRC with Magic

To run full batch DRC across the top module using `tcl/magic_drc.tcl`:

```bash
cd mag
make drc
```
Or directly:
```bash
magic -rcfile ${PDK_ROOT}/ihp-sg13g2/libs.tech/magic/ihp-sg13g2.magicrc -noconsole -dnull ../tcl/magic_drc.tcl tt_um_tnt_mosbius
```

### 3.3 Extracting LVS and PEX Netlists

Magic extracts SPICE netlists from `.mag` files for LVS verification and parasitic extraction.

- **Extract LVS SPICE netlist**:
  ```bash
  cd mag
  make lvs.lvs.spice
  ```
  This executes `tcl/magic_extract_lvs.tcl`, generating `tt_um_tnt_mosbius.lvs.spice`.

- **Extract Parasitic Netlist (PEX)**:
  ```bash
  cd mag
  magic -rcfile ${PDK_ROOT}/ihp-sg13g2/libs.tech/magic/ihp-sg13g2.magicrc -noconsole -dnull ../tcl/magic_extract_pex.tcl tt_um_tnt_mosbius
  ```
  This creates `tt_um_tnt_mosbius.pex.spice` containing parasitic capacitances and resistances.

### 3.4 Exporting GDSII and LEF Layouts

To export GDSII and LEF layout files from Magic:

```bash
cd mag
make update_gds
```
This updates `gds/tt_um_tnt_mosbius.gds` and `lef/tt_um_tnt_mosbius.lef`.

---

## 4. Layout Versus Schematic (LVS) Verification with Netgen

Netgen performs structural equivalence checking between the extracted layout netlist and the schematic/synthesized netlist hierarchy.

### 4.1 Running LVS

To execute LVS verification:

```bash
cd mag
make lvs
```

Under the hood, `make lvs` runs Netgen using `tcl/lvs.tcl`:
```tcl
set layout [readnet spice tt_um_tnt_mosbius.lvs.spice]
set schem  [readnet verilog /dev/null]
readnet spice $::env(PDK_ROOT)/ihp-sg13g2/libs.ref/sg13g2_stdcell/spice/sg13g2_stdcell.spice $schem
readnet spice ../xschem/simulation/mosbius.spice $schem
readnet verilog ../src/ctrl_top.synth.v $schem
readnet verilog ../src/project.v $schem
lvs "$layout tt_um_tnt_mosbius" "$schem tt_um_tnt_mosbius" $::env(PDK_ROOT)/ihp-sg13g2/libs.tech/netgen/sg13g2_setup.tcl lvs.report -blackbox
```

### 4.2 Interpreting LVS Output (`lvs.report`)

After running `make lvs`, inspect `mag/lvs.report`:

- **Success result**:
  Look for `Circuits match uniquely.` and no property errors:
  ```text
  Final result: Circuits match uniquely.
  ```
- **Mismatch troubleshooting**:
  - Check for mismatched instance counts (e.g., standard cells vs schematic devices).
  - Check for unmatched pin names between Verilog module declarations and layout labels.
  - Verify property values (device W/L, resistor/capacitor values).

---

## 5. Post-Processing GDSII Layer Remapping

Because sub-blocks may contain legacy or intermediate layer formats, `py/fix_gds.py` performs binary stream layer remapping to conform to official IHP SG13G2 layer standards:

```bash
python3 py/fix_gds.py gds/tt_um_tnt_mosbius.gds gds/tt_um_tnt_mosbius.gds
```

Layer Mappings Applied:
- `prBoundary`: Remapped to layer `189/4`.
- Metal Layers: Standardized to Metal1 `8/0`, Metal2 `30/0`, Metal3 `50/0`, Metal4 `67/0`, Metal5 `125/0`.
- Strips invalid/legacy datatypes (e.g. datatype 25/2).

---

## 6. GDSII Geometry & DRC Inspection with KLayout

KLayout is used for visual layout inspection, boundary verification, and signoff DRC checks on the stream GDSII file.

### 6.1 Interactive GDS Visual Inspection

To inspect the generated GDSII visually:

```bash
klayout gds/tt_um_tnt_mosbius.gds
```

Verification Checklist in KLayout:
1. **Tile Boundary & Pin Alignment**: Confirm layout boundaries match `tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def` bounds.
2. **Layer Map**: Ensure Metal1-Metal5 layers render correctly without missing geometries.
3. **Power Grids**: Verify `VDPWR`, `VAPWR`, and `VGND` power routing rings and tap coverage.

### 6.2 Running KLayout DRC Check

To execute DRC using KLayout batch mode with SG13G2 DRC rules:

```bash
klayout -b -r ${PDK_ROOT}/ihp-sg13g2/libs.tech/klayout/drc/sg13g2_drc.lydrc \
        -rd input=gds/tt_um_tnt_mosbius.gds \
        -rd report=klayout_drc.lyrdb
```

Review DRC results:
- Open `klayout_drc.lyrdb` in KLayout's Marker Browser (`Tools` -> `Marker Browser`).
- Refer to `klayout_violations_2.md` for known macro-level or tile boundary rule exceptions.

---

## 7. Automated Static Checks and Unit Tests

To verify overall pipeline consistency, synthesize decap stubs, and run static CI checks:

```bash
make check
```

This runs:
1. Decap Verilog generation and logic elaboration via Yosys.
2. `python3 py/verify_cicd_config.py` (verifying DEF templates, pin maps, YAML schema, GDS artifacts, workflow steps).
3. Python unit tests (`python3 -m unittest discover -s py`).

---

## Summary Matrix of Verification Steps

| Step | Tool | Command / File | Target / Artifact |
|---|---|---|---|
| **Schematic Netlist** | Xschem | `xschem/mosbius.sch` -> Netlist | `xschem/simulation/mosbius.spice` |
| **Logic Synthesis** | Yosys | `make -C src all` | `src/ctrl_top.synth.v` |
| **Interactive DRC** | Magic | `cd mag && magic -rcfile $MAGIC_RC tt_um_tnt_mosbius.mag` | Interactive feedback |
| **Batch DRC** | Magic | `make -C mag drc` | Terminal output |
| **LVS Extraction** | Magic | `make -C mag lvs.lvs.spice` | `mag/tt_um_tnt_mosbius.lvs.spice` |
| **LVS Check** | Netgen | `make -C mag lvs` | `mag/lvs.report` |
| **GDS Export** | Magic | `make -C mag update_gds` | `gds/tt_um_tnt_mosbius.gds` |
| **Layer Remapping** | Python | `python3 py/fix_gds.py gds/tt_um_tnt_mosbius.gds ...` | Remapped `gds/tt_um_tnt_mosbius.gds` |
| **Signoff DRC** | KLayout | `klayout -b -r ... -rd input=gds/tt_um_tnt_mosbius.gds` | `klayout_drc.lyrdb` |
| **Static CI Verification**| Python | `make check` | Unit tests & CI checks pass |
