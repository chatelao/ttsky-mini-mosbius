# Baseline Documentation: tnt's Mini-MOSbius for SKY130 TinyTapeout

## 1. Overview & Purpose

**tnt's variant of SKY130 mini-MOSbius** is an analog/mixed-signal integrated circuit design submitted for TinyTapeout (TT) shuttles using the SkyWater 130nm CMOS technology node (`sky130A`).

Inspired by the original **MOSbius** project (Peter Kinget et al.), which provides flexible, reconfigurable arrays of analog switches and basic MOS transistor primitives/building blocks, this project adapts Andrew Kang's mini-MOSbius architecture with custom digital control logic and a complete custom physical layout by Sylvain Munaut (246tnt).

The primary goal of the chip is to provide programmable analog building blocks (differential pairs, current mirrors, OTAs, configurable PMOS/NMOS arrays) interconnected via an Analog Switch Matrix (ASW) controlled by a serial shift-register chain.

---

## 2. System Architecture & Top-Level Interconnects

### 2.1 Power Domains & Voltage Rails
The design operates across multiple power domains:
* **`VDPWR` (1.8V):** Core digital supply voltage powering the shift registers, control logic, buffers, and digital standard cells (`sky130_fd_sc_hd`).
* **`VAPWR` (3.3V):** High-voltage supply powering the analog switch matrix and analog transistor blocks (e.g., 5.0V/3.3V rated high-voltage FETs `sky130_fd_pr__nfet_g5v0d10v5` and `sky130_fd_pr__pfet_g5v0d10v5`).
* **`VGND` (0V):** Common ground reference.

### 2.2 Top-Level Module (`tt_um_tnt_mosbius`)
* **Digital I/O Ports:**
  * `ui_in[0]` (`data_in`): Serial data input stream for configuration.
  * `ui_in[1]` (`enable`): Active-high enable signal for updating control registers.
  * `uo_out[0]` (`data_out`): Serial data output stream (chain output for daisy-chaining/verifying configuration).
  * `clk`, `rst_n`: Digital clock and active-low reset signals.
* **Analog Pins (`ua`):**
  * `ua[0]`: `Reference Bias` (`ibias`)
  * `ua[1]`: `Bus 1A`
  * `ua[2]`: `Bus 3A`
  * `ua[3]`: `Bus 5A`
  * `ua[4]`: `Bus 2B`
  * `ua[5]`: `Bus 4B`
* **Internal Analog Busses:**
  * `bus_A[6:1]` and `bus_B[6:1]`: 6-wire internal analog routing busses connecting switches and sub-blocks.

---

## 3. Analog Blocks & Sub-Circuits

The analog subsystem (`mosbius`) incorporates various configurable transistor primitives and building blocks designed in Xschem and Magic:

1. **Analog Switch Matrix (ASW):**
   * Transmission gate / analog switches powered by 3.3V (`VAPWR`) allowing reconfigurable interconnections between internal analog busses (`bus_A`, `bus_B`) and device terminals.
   * Short switches (`cfg_bus_short`) and power connection switches (`cfg_bus_pwr`).
2. **Differential Pairs:**
   * **NMOS Differential Pair (`dev_nmos_dp` / `diff_n`):** Configurable input/output switches, adjustable tail currents (`ctrl_dpn_tail`), and tail source select (`ctrl_dpn_source`).
   * **PMOS Differential Pair (`dev_pmos_dp` / `diff_p`):** Programmable inputs/outputs and tail bias configurations.
3. **Current Mirrors:**
   * **NMOS Current Mirror (`dev_nmos_cm` / `mirror_n`) & PMOS Current Mirror (`dev_pmos_cm` / `mirror_p`):** Configurable mirror ratios and routing matrix nodes.
4. **Operational Transconductance Amplifier (OTA):**
   * **NMOS OTA (`dev_nmos_ota` / `ota_n`):** 2-stage operational amplifier block with configurable input/output modes, tail currents (`ctrl_otan_tail`), and operating modes (`ctrl_otan_mode`).
5. **Programmable Transistors:**
   * **Dual NMOS (`dev_nmos_dual` / `nmos_prog`) & Dual PMOS (`dev_pmos_dual` / `pmos_prog`):** Discrete transistor arrays with configurable channel width (`ctrl_*_width`), source bias (`ctrl_*_source`), and terminal routing (Drain, Gate, Source).

---

## 4. Digital Control Infrastructure

### 4.1 Shift Register Chain (`ctrl_top` & `ctrl_block`)
The digital control logic manages a 192-bit control bus (`ctrl[191:0]`):
* **Control Chain Architecture:**
  * Built using custom standard-cell blocks (`ctrl_block`) instantiated in series.
  * Inputs are buffered and filtered using `sky130_fd_sc_hd__clkbuf` and `sky130_fd_sc_hd__diode_2`.
  * **26 ASW Column Control Blocks:** Each controlling 6 switch bits (`ctrl_out[6*i+:6]`).
  * **Device Control Blocks:** Controlling analog device configurations (OTA bias, differential pair tail currents, mirror selection, and programmable FET widths).
  * Shift register outputs are masked using AND gates controlled by `l_enable` before being applied to analog switch gates.

### 4.2 Automated Layout & Decap Generation (`py/`)
A key architectural feature of this project is the scripted layout generation for digital control blocks:
* `common.py`: Provides Python abstractions for cell placement (`Grid`), routing (`Router`), track grid definition, and via generation for Magic scripts.
* `gen_asw_ctrl.py`: Generates Magic layout scripts and procedural decoupling capacitor (`decap`) Verilog instantiations (`ctrl_asw.decap.v`) for ASW column controllers.
* `gen_dev_ctrl.py`: Generates decap and layout scripts for device controllers (`ctrl_dev_*.decap.v`).

---

## 5. EDA Tools & Technology Stack

The project relies on open-source Electronic Design Automation (EDA) tools and the SkyWater 130nm PDK:

| Category | Tool / Resource | Description |
|---|---|---|
| **PDK** | SkyWater 130nm (`sky130A`) | Open-source PDK, using `sky130_fd_sc_hd` (High Density standard cells) and `sky130_fd_pr` (primitive 5V/3.3V transistors). |
| **Schematic Capture** | **Xschem** | Used for schematic capture of analog blocks, testbenches, and top-level analog integration (`xschem/*.sch`). |
| **Layout Design** | **Magic VLSI** | Used for manual layout, GDS extraction, DRC checks, and hierarchical assembly (`mag/*.mag`). |
| **Synthesis & Netlist** | **Yosys** | Synthesizes and elaborates Verilog control logic into standard cells for LVS verification (`src/Makefile`). |
| **LVS Verification** | **Netgen** | Performs Layout vs. Schematic (LVS) comparison comparing extracted SPICE/Verilog against synthesized netlists (`tcl/lvs.tcl`). |
| **GDS / LEF Generation**| **Tcl & Python Scripts** | Custom scripts (`fix_gds.py`, `update_gds_lef.tcl`) to fix GDS cell references, import/export LEF, and run automated DRC. |

---

## 6. Directory Structure & Key Files

```
.
├── README.md                 # Primary project overview
├── info.yaml                 # TinyTapeout pinout & project metadata
├── docs/                     # Project documentation & original proposal
│   ├── info.md
│   └── Mini_Mosbius_Proposal_Kang_Andrew_v2.pdf
├── src/                      # Verilog RTL source files
│   ├── project.v             # Top-level wrapper (tt_um_tnt_mosbius)
│   ├── ctrl_top.v            # Top-level digital control logic
│   ├── ctrl_block.v          # Modular shift register unit block
│   ├── stdcells.v            # Standard cell verilog declarations
│   └── Makefile              # Elaborates & synthesizes verilog for LVS
├── py/                       # Python layout and decap generators
│   ├── common.py             # Grid placement & routing helper library
│   ├── gen_asw_ctrl.py       # Generator for ASW column control layout/decaps
│   ├── gen_dev_ctrl.py       # Generator for device control layout/decaps
│   └── fix_gds.py            # GDS post-processing script
├── mag/                      # Magic layout files (.mag)
│   ├── tt_um_tnt_mosbius.mag # Top-level layout
│   ├── asw_matrix.mag        # Analog switch matrix layout
│   ├── dev_*.mag             # Analog device layouts (differential pairs, mirrors, OTAs)
│   └── Makefile              # Layout build tasks
├── xschem/                   # Xschem schematics (.sch) & symbols (.sym)
│   ├── mosbius.sch           # Top-level analog schematic
│   ├── diff_n.sch, diff_p.sch# Differential pair schematics
│   ├── mirror_n.sch, mirror_p.sch # Current mirror schematics
│   ├── ota_n.sch             # OTA schematic
│   └── tb_*.sch              # Simulation testbenches
├── tcl/                      # Tool automation scripts
│   ├── magic_drc.tcl         # Full DRC execution script
│   ├── magic_extract_lvs.tcl # LVS SPICE extraction script
│   ├── magic_extract_pex.tcl # Parasitic extraction script
│   └── lvs.tcl               # Netgen LVS execution script
├── gds/                      # Final GDSII output (`tt_um_tnt_mosbius.gds`)
└── lef/                      # Final LEF output (`tt_um_tnt_mosbius.lef`)
```

---

## 7. Build, Synthesis, and Verification Workflows

### 7.1 Digital Logic Synthesis & Decap Generation
Decap files and synthesized control netlists are generated using Python scripts and Yosys:
```bash
cd src
make clean all
```
* Runs `gen_asw_ctrl.py` and `gen_dev_ctrl.py` to produce `.decap.v` files.
* Executes Yosys to generate `ctrl_top.synth.v`.

### 7.2 Design Rule Checking (DRC)
Full Euclidean DRC is run in Magic:
```bash
magic -noc -dnull tcl/magic_drc.tcl tt_um_tnt_mosbius
```

### 7.3 Extraction & Layout vs. Schematic (LVS)
LVS is executed by extracting the SPICE netlist from Magic layout and comparing it against the Verilog + SPICE schematics via Netgen:
```bash
# Extract SPICE from layout
magic -noc -dnull tcl/magic_extract_lvs.tcl tt_um_tnt_mosbius

# Perform LVS with Netgen
netgen -batch source tcl/lvs.tcl
```
