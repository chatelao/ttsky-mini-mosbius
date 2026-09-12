# Map of Tools and Basic Components from SKY (SkyWater 130nm) to IHP (SG13G2 130nm)

This document provides a comprehensive mapping guide for porting the **Mini-MOSbius** project (and open-source IC designs in general) from the **SkyWater 130nm (SKY130)** PDK to the **IHP SG13G2 130nm** PDK (IHP Open PDK).

---

## 1. Process Technology Overview

| Feature / Parameter | SkyWater 130nm (`sky130`) | IHP 130nm (`sg13g2`) | Notes / Migration Impact |
| :--- | :--- | :--- | :--- |
| **Node / Feature Size** | 130nm CMOS | 130nm BiCMOS (SiGe:C) | IHP includes high-speed SiGe HBTs |
| **Core Logic Voltage ($V_{DD}$ / $V_{DPWR}$)** | 1.8V | 1.2V | Standard digital logic runs at 1.2V in IHP vs 1.8V in SKY130 |
| **Analog / IO Voltage ($V_{APWR}$)** | 3.3V / 5.0V ($5.0\text{V}$ extended) | 3.3V | IHP 3.3V HV MOS devices (`sg13g2_pr__nfet33`, `pfet33`) |
| **Metal Layers** | 5 Metal Layers (Li, M1–M4 or M1–M5) | 5 Metal Layers (M1–M5 + TopMetal1/2) | Layer stack and rules differ in layout tools (`li` in sky130 vs `met1`–`met5` in IHP) |
| **PDK Repository / License** | Apache 2.0 (`google/skywater-pdk`) | Apache 2.0 (`IHP-Open-PDK`) | Fully open-source PDKs |

---

## 2. Toolchain and EDA Suite Mapping

| EDA Function | SKY130 Tooling / Environment | IHP SG13G2 Tooling / Environment | Migration / Porting Strategy |
| :--- | :--- | :--- | :--- |
| **Schematic Capture** | Xschem (with `sky130_fd_pr` symbols) | Xschem (with `sg13g2_pr` symbols) | Replace primitive symbols and property parameters in `.sch` files |
| **Circuit Simulation** | Ngspice (using `sky130.lib.spice` models) | Ngspice (using `corner.spice` / `sg13g2.lib`) | Update SPICE model includes and model names |
| **Layout Design / Viewing** | Magic VLSI / KLayout | KLayout / Magic VLSI | KLayout is primary for IHP PDK setup; Magic tech files exist for DRC/LVS |
| **Design Rule Checking (DRC)** | Magic DRC / KLayout DRC (`sky130A.lydrc`) | KLayout DRC (`sg13g2.lydrc`) / Magic DRC | Adapt DRC scripts for IHP layout design rules |
| **Layout vs. Schematic (LVS)** | Netgen / KLayout LVS | Netgen / KLayout LVS (`sg13g2.lylvs`) | Re-extract layout using IHP extraction rules and run Netgen |
| **Parasitic Extraction (PEX)** | Magic `extract` / Magic PEX | KLayout PEX / Magic PEX | Extract parasitic capacitance & resistance using SG13G2 tech files |
| **Verilog Synthesis** | Yosys (target `sky130_fd_sc_hd`) | Yosys (target `sg13g2_stdcell`) | Re-synthesize digital RTL (`ctrl_top.v`, `ctrl_block.v`) |
| **Place & Route (PnR)** | OpenROAD / Custom Python (`py/*.py`) | OpenROAD / Custom Python (`py/*.py`) | Update cell pitch (`COL_PITCH`, `ROW_PITCH`), via definitions, and layer stacks |

---

## 3. Power Supplies and Voltage Domains

| Domain / Signal | SKY130 Domain | IHP SG13G2 Domain | Porting Considerations |
| :--- | :--- | :--- | :--- |
| **Ground Rail (`VGND`)** | 0V | 0V | Substrate ground |
| **Digital Power (`VDPWR`)** | 1.8V | 1.2V | Standard cells and digital control logic operate at 1.2V |
| **Analog Power (`VAPWR`)** | 3.3V (or 5.0V tolerant) | 3.3V | Analog switches and high-voltage circuit blocks operate at 3.3V |
| **Level Shifters** | 1.8V to 3.3V Level Shifters (`tt_lvl_shift`) | 1.2V to 3.3V Level Shifters | Required to bridge digital control (1.2V) to analog switches (3.3V) |

---

## 4. Primitive Device Model Mapping

Below is the mapping for transistor primitives used in Mini-MOSbius schematic design (`xschem/*.sch`) and layout (`mag/*.mag`):

| Device Type | SKY130 Primitive Model (`sky130_fd_pr`) | IHP SG13G2 Primitive Model (`sg13g2_pr`) | Description / Notes |
| :--- | :--- | :--- | :--- |
| **5.0V / 3.3V NMOS** | `nfet_g5v0d10v5` | `nfet33` | 3.3V Thick Oxide NMOS Transistor |
| **5.0V / 3.3V PMOS** | `pfet_g5v0d10v5` | `pfet33` | 3.3V Thick Oxide PMOS Transistor |
| **3.3V 3-Terminal NMOS** | `nfet3_g5v0d10v5` | `nfet33` | Isolated bulk / 3-terminal variant |
| **3.3V 3-Terminal PMOS** | `pfet3_g5v0d10v5` | `pfet33` | Isolated bulk / 3-terminal variant |
| **1.8V / 1.2V Standard NMOS** | `nfet3_01v8` | `nfet` | Standard Core NMOS Transistor |
| **1.8V / 1.2V Standard PMOS** | `pfet3_01v8_hvt` / `pfet3_01v8` | `pfet` | Standard Core PMOS Transistor |
| **BiCMOS HBTs (Optional)** | N/A | `npn13G2` / `npn13G2v` | High-speed SiGe NPN Bipolar Transistors (available in IHP) |
| **Resistors** | `res_high_po` / `res_generic` | `rhigh` / `rsil` | High-sheet / Silicide Poly Resistors |
| **Capacitors** | `cap_mim_m3_1` / `cap_mim_m3_2` | `cap_cmim` | Metal-Insulator-Metal (MIM) Capacitors |

---

## 5. Digital Standard Cell Library Mapping

Digital control logic in `ctrl_top.v` and `ctrl_block.v` relies on standard cell primitives. The mapping between **SkyWater HD (`sky130_fd_sc_hd`)** and **IHP SG13G2 Standard Cell Library (`sg13g2_stdcell`)** is as follows:

| Standard Cell Function | SKY130 Cell (`sky130_fd_sc_hd__*`) | IHP SG13G2 Cell (`sg13g2_stdcell_*`) |
| :--- | :--- | :--- |
| **2-Input AND Gate** | `and2_2`, `and2_4` | `sg13g2_and2_1`, `sg13g2_and2_2` |
| **2-Input OR Gate** | `or2_1`, `or2_2` | `sg13g2_or2_1`, `sg13g2_or2_2` |
| **Inverter** | `inv_1`, `inv_2`, `inv_4` | `sg13g2_inv_1`, `sg13g2_inv_2` |
| **Clock Buffer** | `clkbuf_4`, `clkbuf_8`, `clkbuf_16` | `sg13g2_buf_2`, `sg13g2_buf_4`, `sg13g2_buf_8` |
| **Delay Buffer** | `clkdlybuf4s50_2` | `sg13g2_dlybuf_1` |
| **D-Flip-Flop with Reset** | `dfrtp_1` | `sg13g2_dfrpc_1` / `sg13g2_dfrq_1` |
| **Standard D-Flip-Flop** | `dfxtp_1`, `dfxtp_2` | `sg13g2_dfq_1` |
| **D-Flip-Flop with inverted Q** | `dfxbp_2` | `sg13g2_dfqb_1` |
| **4-to-1 Multiplexer** | `mux4_2` | `sg13g2_mux4_1` |
| **Constant / Tie Cells** | `conb_1` (`HI` / `LO`) | `sg13g2_tiel_1`, `sg13g2_tieh_1` |
| **Decoupling Capacitors** | `decap_3`, `decap_4`, `decap_6`, `decap_12` | `sg13g2_decap_4`, `sg13g2_decap_8` |
| **Fill Cells** | `fill_1`, `fill_2` | `sg13g2_fill_1`, `sg13g2_fill_2` |
| **Substrate / Well Taps** | `tapvpwrvgnd_1` | Integrated in cells or `sg13g2_tap_1` |
| **Antenna Protection Diode** | `diode_2` | `sg13g2_antenna_1` |

---

## 6. Mini-MOSbius Functional Component Mapping

Below is the component-level mapping for all core analog and digital blocks in the Mini-MOSbius architecture:

| Component Name | File (`xschem/` or `src/`) | SKY130 Implementation Details | IHP SG13G2 Target Implementation |
| :--- | :--- | :--- | :--- |
| **Top Module** | `src/project.v` (`tt_um_tnt_mosbius`) | 6 analog pins (`ua[5:0]`), 1.8V $V_{DPWR}$, 3.3V $V_{APWR}$ | Adapt pinout to Tiny Tapeout IHP shuttle format; 1.2V $V_{DPWR}$, 3.3V $V_{APWR}$ |
| **Digital Control Top** | `src/ctrl_top.v` | SPI/Shift-register bitstream interface (192 control bits) | Re-synthesize RTL targeting `sg13g2_stdcell` library |
| **Shift Register Block** | `src/ctrl_block.v` | Chains of D-Flip-Flops (`dfrtp_1`, `dfxtp_1`) | Synthesize using `sg13g2_dfrpc_1` / `sg13g2_dfq_1` |
| **Analog Core Assembly** | `xschem/mosbius.sch` | Core matrix of switches & programmable devices | Update schematic symbols from `sky130` to `sg13g2` |
| **5-Transistor OTA** | `xschem/ota_n.sch` | Built using `nfet_g5v0d10v5` and `pfet_g5v0d10v5` | Re-bind to `nfet33` and `pfet33` primitives |
| **NMOS Differential Pair** | `xschem/diff_n.sch` | Programmable tail current & differential pair (`nfet_g5v0d10v5`) | Re-bind to `nfet33` with equivalent W/L scaling |
| **PMOS Differential Pair** | `xschem/diff_p.sch` | Programmable tail current & differential pair (`pfet_g5v0d10v5`) | Re-bind to `pfet33` with equivalent W/L scaling |
| **NMOS Current Mirror** | `xschem/mirror_n.sch` | Cascode / programmable N-channel mirror array | Re-bind to `nfet33` primitives |
| **PMOS Current Mirror** | `xschem/mirror_p.sch` | Cascode / programmable P-channel mirror array | Re-bind to `pfet33` primitives |
| **Programmable NMOS** | `xschem/nmos_prog.sch` | Binary/Thermometer weighted 3.3V/5V NMOS arrays | Re-bind to `nfet33` primitives |
| **Programmable PMOS** | `xschem/pmos_prog.sch` | Binary/Thermometer weighted 3.3V/5V PMOS arrays | Re-bind to `pfet33` primitives |
| **Analog Switch (3.3V)** | `xschem/tt_asw_3v3.sch` | Transmission gate switch driven by level shifters | Implement using 3.3V `nfet33` / `pfet33` transmission gates |
| **Level Shifter** | `mag/tt_lvl_shift.mag` | 1.8V to 3.3V level shifter cell | 1.2V to 3.3V level shifter cell |
| **Switch Matrix Layout** | `mag/asw_matrix.mag` | Reconfigurable crossbar switch array layout | Re-layout using SG13G2 design rules and layer pitch |

---

## 7. TinyTapeout CI & GitHub Actions Workflow Setup

When deploying or building TinyTapeout GitHub Actions workflows for IHP SG13G2, the action tags, parameters, and metadata must reflect the IHP PDK toolchain:

| Configuration Item | SKY130 Setting | IHP SG13G2 Setting | File Location |
| :--- | :--- | :--- | :--- |
| **Action Tag** | `@ttsky26c` | `@ttihp26b` | `.github/workflows/gds.yaml`, `docs.yaml` |
| **PDK Parameter** | `sky130A` | `ihp-sg13g2` | `.github/workflows/gds.yaml` (`pdk: ihp-sg13g2`) |
| **Project Title** | "... (SKY130)" | "... (IHP SG13G2)" | `info.yaml` (`project.title`) |
| **Top-Level Description** | "... Skywater TinyTapeout" | "... IHP SG13G2 TinyTapeout" | `info.yaml` (`project.description`) |
| **Digital Power (`VDPWR`)** | 1.8V | 1.2V | `info.yaml` (comments & pin specs) |
| **Analog Power (`VAPWR`)** | 3.3V | 3.3V (`uses_vapwr: true`) | `info.yaml` |

---

## 8. Scripted Placement & Decap Generator Adaptation (`py/`)

The Python layout helper scripts in `py/` procedurally generate standard cell layout placements and decap Verilog stubs (`ctrl_asw.decap.v`, `ctrl_dev_*.decap.v`):

### 8.1 Grid Parameters and Layers (`py/common.py`)

| Parameter / Data Structure | SKY130 Definition | IHP SG13G2 Adaptation Target | Notes |
| :--- | :--- | :--- | :--- |
| **`ROW_PITCH`** | 2720 nm (2.72 $\mu$m) | Matches `sg13g2_stdcell` height (3.78 $\mu$m or standard cell pitch) | Standard cell row height |
| **`COL_PITCH`** | 460 nm (0.46 $\mu$m) | Matches `sg13g2_stdcell` site width (0.48 $\mu$m) | Standard cell site width |
| **`LAYERS` Stack** | `li` (local interconnect), `met1`, `met2` | `met1` (Metal 1), `met2`, `met3` | IHP SG13G2 layer stack does not use `li` |
| **Via Stack (`VIAS`)** | `viali`, `m2c` | `via1`, `via2`, `via3` | Use SG13G2 via definitions |
| **`Grid.FILL` Dictionary** | `sky130_fd_sc_hd__fill_*` / `decap_*` | `sg13g2_fill_*` / `sg13g2_decap_*` | Map widths to SG13G2 cell widths |
| **`Grid.TAP` Cell** | `sky130_fd_sc_hd__tapvpwrvgnd_1` | Integrated / `sg13g2_tap_1` | Substrate tap cell reference |
| **`CELLS` Master Table** | `sky130_fd_sc_hd__*` | `sg13g2_stdcell_*` | Update cell names and width metrics |

### 8.2 Decap Verilog Generation (`py/gen_asw_ctrl.py` & `py/gen_dev_ctrl.py`)

* **Power Pin Names:** Standard cell power pins in `sky130` use `.VPWR (VDPWR)`, `.VGND (VGND)`, `.VPB (VDPWR)`, `.VNB (VGND)`. In `sg13g2_stdcell`, power pins may use `VDD`/`VSS` or `VDPWR`/`VGND` depending on standard cell library netlist conventions.
* **Decap Instantiations:** Update decap cell selection from `sky130_fd_sc_hd__decap_3/4/6/8/12` to `sg13g2_decap_4` or `sg13g2_decap_8`.

---

## 9. Verification and Build Automation Adaptations

| Automation Task | File Location | SKY130 Command / Syntax | IHP SG13G2 Target Command / Syntax |
| :--- | :--- | :--- | :--- |
| **Verilog Elaboration** | `src/Makefile`, `src/stdcells.v` | Synthesizes using `sky130_fd_sc_hd` blackboxes | Synthesizes using `sg13g2_stdcell` blackboxes / models |
| **LVS Verification** | `tcl/lvs.tcl` | Reads `sky130_fd_sc_hd.spice` & `sky130A_setup.tcl` | Reads `sg13g2_stdcell.spice` & `sg13g2_setup.tcl` |
| **DRC Scripting** | `tcl/magic_drc.tcl` | Uses `sky130A` Magic tech file / rules | Uses `sg13g2.tech` / KLayout `sg13g2.lydrc` |
| **Parasitic Extraction** | `tcl/magic_extract_pex.tcl` | SkyWater 130 PEX rules | IHP SG13G2 PEX rules / KLayout PEX |
| **Simulation Corners** | `xschem/tb_*.sch` | `sky130.lib.spice` (`corner.sym`) | `corner.spice` / `sg13g2.lib` |
