# Migration Concept: Porting Mini-MOSbius from SKY130 to IHP SG13G2

## 1. High-Level Vision & Objectives

The primary goal of this concept is to define the migration path for **tnt's variant of Mini-MOSbius** from the SkyWater 130nm CMOS technology (`sky130A`) to the **IHP SG13G2 130nm BiCMOS** technology (`sg13g2`) for TinyTapeout shuttles.

Mini-MOSbius provides a reconfigurable array of analog switches and basic MOS transistor primitives (differential pairs, current mirrors, OTAs, and programmable PMOS/NMOS arrays) controlled via a serial shift-register chain. Porting this design to IHP SG13G2 will enable higher performance analog blocks, integration with SiGe HBTs where advantageous, and compatibility with IHP TinyTapeout shuttles.

---

## 2. Power Domains & Voltage Architecture Translation

| Domain / Parameter | SKY130 Specification | IHP SG13G2 Specification | Migration Considerations |
| :--- | :--- | :--- | :--- |
| **Digital Power (`VDPWR`)** | 1.8V | **1.2V** | Core shift registers, buffers, and control logic run at 1.2V. |
| **Analog Power (`VAPWR`)** | 3.3V (5.0V tolerant) | **3.3V** | Analog switches and configurable MOS arrays operate at 3.3V. |
| **Ground Reference (`VGND`)** | 0V | **0V** | Shared substrate ground reference. |
| **Level Shifters** | 1.8V -> 3.3V (`tt_lvl_shift`) | **1.2V -> 3.3V** | Level shifters required to convert 1.2V digital switch enable signals to 3.3V analog switch gate control signals. |

---

## 3. Technology & Device Primitive Mapping

### 3.1 Analog Primitive Devices

| Circuit Primitive | SKY130 Model (`sky130_fd_pr`) | IHP SG13G2 Model (`sg13g2_pr`) | Target Adaptation Strategy |
| :--- | :--- | :--- | :--- |
| **3.3V NMOS Transistor** | `nfet_g5v0d10v5` | `nfet33` | Map all switches, OTA differential pairs, NMOS mirrors, and dual NMOS blocks to 3.3V thick-oxide NMOS (`nfet33`). |
| **3.3V PMOS Transistor** | `pfet_g5v0d10v5` | `pfet33` | Map OTA PMOS loads, PMOS mirrors, and dual PMOS blocks to 3.3V thick-oxide PMOS (`pfet33`). |
| **Core 1.2V NMOS** | `nfet3_01v8` | `nfet` | Standard digital/core level logic. |
| **Core 1.2V PMOS** | `pfet3_01v8` | `pfet` | Standard digital/core level logic. |
| **Resistors** | `res_high_po` | `rhigh` / `rsil` | Poly resistors for biasing/references. |
| **Capacitors** | `cap_mim_m3_1` | `cap_cmim` | Metal-Insulator-Metal (MIM) capacitors for compensation or decoupling. |
| **SiGe HBTs (Optional)** | N/A | `npn13G2` | Potential enhancement for high-frequency analog building blocks or low-noise gain stages. |

---

## 4. Digital Control Subsystem & Standard Cells

The digital control infrastructure managing the 192-bit control bitstream (`ctrl_top` and `ctrl_block`) will be re-synthesized using Yosys against the IHP SG13G2 standard cell library (`sg13g2_stdcell`):

| Function | SKY130 Library Cell (`sky130_fd_sc_hd__*`) | IHP SG13G2 Cell (`sg13g2_stdcell_*`) |
| :--- | :--- | :--- |
| **2-Input AND Gate** | `and2_2` | `sg13g2_and2_1` / `sg13g2_and2_2` |
| **Inverter** | `inv_1` / `inv_2` | `sg13g2_inv_1` / `sg13g2_inv_2` |
| **Clock Buffer** | `clkbuf_4` / `clkbuf_8` | `sg13g2_buf_2` / `sg13g2_buf_4` |
| **D Flip-Flop w/ Reset** | `dfrtp_1` | `sg13g2_dfrpc_1` / `sg13g2_dfrq_1` |
| **Decoupling Capacitors** | `decap_3`, `decap_4`, `decap_6` | `sg13g2_decap_4`, `sg13g2_decap_8` |
| **Filler Cells** | `fill_1`, `fill_2` | `sg13g2_fill_1`, `sg13g2_fill_2` |

---

## 5. Physical Layout & Scripting Adaptation Strategy

A major component of tnt's implementation is procedural placement and decap generation via Python (`py/` directory):
* **Grid & Pitch Adjustments (`py/common.py`):** Update cell height, column pitch (`COL_PITCH`, `ROW_PITCH`), track spacing, and via structures to conform to IHP SG13G2 DRC rules and standard cell pitch.
* **Decap Generation (`py/gen_asw_ctrl.py`, `py/gen_dev_ctrl.py`):** Modify decap instantiation scripts to output `sg13g2_decap_*` standard cells in the generated `.decap.v` files.
* **Layout Assembly:** Transition layout design flow from Magic VLSI / KLayout rules targeting SKY130 to KLayout / Magic VLSI scripts configured with `sg13g2.tech` / `sg13g2.lydrc`.

---

## 6. Verification & EDA Toolchain Alignment

1. **Schematics & Simulation:**
   * Re-bind Xschem symbols in `xschem/*.sch` from `sky130_fd_pr` to `sg13g2_pr`.
   * Update Ngspice simulation testbenches (`xschem/tb_*.sch`) to include IHP process models (`corner.spice` / `sg13g2.lib`).
2. **Synthesis & LVS Verification:**
   * Update Yosys build targets in `src/Makefile` to target `sg13g2_stdcell.v`.
   * Update Netgen LVS scripts (`tcl/lvs.tcl`) and KLayout LVS rule decks (`sg13g2.lylvs`) to perform Layout-vs-Schematic matching across the 1.2V and 3.3V domains.
3. **DRC & PEX:**
   * Perform DRC checks using KLayout DRC (`sg13g2.lydrc`) and Magic DRC scripts.
   * Extract parasitic capacitance and resistance using SG13G2 technology files for post-layout simulation.
