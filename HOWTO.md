# Manual & Local Compilation Guide for Mini-MOSbius

This document provides step-by-step instructions for manually compiling, generating artifacts, and running physical verification locally using the existing repository scripts and tools.

---

## Prerequisites & Tools

To run all manual compilation and verification steps, the following toolchain components are required:

- **Python 3** (with standard library `unittest`, `py_compile`, etc.)
- **Yosys** (Open Synthesis Suite)
- **Magic VLSI** (Layout editing, extraction, DRC, and GDS/LEF export)
- **Netgen** (LVS tool)
- **IHP SG13G2 / SkyWater 130 PDK Setup** (`PDK_ROOT` environment variable configured if running full Magic/Netgen LVS/DRC)

---

## Step 1: Generate Decap Verilog Stubs

The control block layout generation scripts in `py/` define layout placements and can output decap Verilog stubs required for synthesis elaboration.

You can generate these decap files individually or via `make`:

```bash
# Change to the src directory
cd src

# Generate decap stubs using python scripts in py/
python3 ../py/gen_asw_ctrl.py decap > ctrl_asw.decap.v
python3 ../py/gen_dev_ctrl.py decap first 1 > ctrl_dev_f.decap.v
python3 ../py/gen_dev_ctrl.py decap pass 1 > ctrl_dev_p.decap.v
python3 ../py/gen_dev_ctrl.py decap begin 1 > ctrl_dev_b1.decap.v
python3 ../py/gen_dev_ctrl.py decap end 1 > ctrl_dev_e1.decap.v
python3 ../py/gen_dev_ctrl.py decap begin 2 > ctrl_dev_b2.decap.v
python3 ../py/gen_dev_ctrl.py decap mid 2 > ctrl_dev_m2.decap.v
python3 ../py/gen_dev_ctrl.py decap end 2 > ctrl_dev_e2.decap.v

# Return to root directory
cd ..
```

---

## Step 2: Elaborate & Synthesize Digital Control Blocks

Yosys is used to elaborate the top control logic (`ctrl_top.v`) into a clean gate-level netlist without attributes (`ctrl_top.synth.v`).

Run Yosys directly or using `make -C src all`:

```bash
# Direct Yosys invocation
yosys -p "read_verilog src/ctrl_top.v; hierarchy -top ctrl_top -check; write_verilog -noattr src/ctrl_top.synth.v"
```

Or using Makefile:
```bash
make -C src all
```

---

## Step 3: Layout Generation, GDS & LEF Export with Magic VLSI

Magic VLSI loads the top-level layout macro (`mag/tt_um_tnt_mosbius.mag`) and exports GDSII and LEF artifacts.

To export GDS and LEF files using Magic:

```bash
cd mag
PROJECT_NAME=tt_um_tnt_mosbius
MAGIC_RC=${PDK_ROOT}/sky130A/libs.tech/magic/sky130A.magicrc

# Run Magic in batch mode to export GDS and LEF
magic -rcfile ${MAGIC_RC} -noconsole -dnull ../tcl/update_gds_lef.tcl ${PROJECT_NAME}

cd ..
```

Or using the `mag` directory Makefile target:
```bash
make -C mag update_gds
```

This creates/updates `gds/tt_um_tnt_mosbius.gds` and `lef/tt_um_tnt_mosbius.lef`.

---

## Step 4: Post-Process GDS for IHP SG13G2 Layer Remapping

The Python script `py/fix_gds.py` post-processes GDSII files to remap legacy or intermediate layer definitions to the official IHP SG13G2 layer map (such as `prBoundary` layer 189/4, Metal1 8/0, Metal2 30/0, Metal3 50/0, Metal4 67/0, Metal5 125/0).

To run layer remapping on a GDS file:

```bash
python3 py/fix_gds.py gds/tt_um_tnt_mosbius.gds gds/tt_um_tnt_mosbius.gds
```

---

## Step 5: Physical & CI Verification (DRC, LVS, and Static Checks)

### 1. Static CI/CD Verification & Unit Tests
Run Python syntax check, unit tests, and CI configuration verification:

```bash
# Run all top-level check tasks
make check
```

Or run individual verification components:
```bash
# CI/CD verification script
python3 py/verify_cicd_config.py

# Python unit test discovery
PYTHONPATH=. python3 -m unittest discover -s py
```

### 2. Magic DRC (Design Rule Check)
Run Magic DRC on the top module:

```bash
cd mag
make drc
cd ..
```

### 3. Netgen LVS (Layout Versus Schematic)
Extract LVS SPICE netlist from Magic layout and compare against schematics using Netgen:

```bash
cd mag
make lvs.lvs.spice
make lvs
cd ..
```

---

## Quick Reference Workflow Commands

| Action | Command |
| :--- | :--- |
| **Complete Verification Pass** | `make check` |
| **Generate Decap Stubs & Synth** | `make -C src all` |
| **Lint Python Scripts** | `make lint` |
| **Export GDS & LEF from Magic** | `make -C mag update_gds` |
| **Run DRC** | `make -C mag drc` |
| **Run LVS** | `make -C mag lvs` |
| **Clean Generated Stubs & Synth** | `make clean` |
