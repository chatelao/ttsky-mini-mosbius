# Design Document: Porting Mini-MOSbius from SKY130 to IHP SG13G2

## 1. System Goal & Scope

The primary objective of this design is to port Sylvain Munaut's (246tnt) variant of the **Mini-MOSbius** reconfigurable analog/mixed-signal IC from SkyWater 130nm (`sky130A`) to the **IHP SG13G2 130nm BiCMOS** (`sg13g2`) target for TinyTapeout shuttles.

Mini-MOSbius provides a reconfigurable matrix of analog switches and basic transistor primitives (differential pairs, current mirrors, OTAs, and discrete NMOS/PMOS transistor arrays) controlled via a 192-bit serial shift-register chain.

---

## 2. Technology Stack & Process Comparison

### 2.1 Process Technology Parameters

| Parameter | SKY130 Specification | IHP SG13G2 Specification | Porting Adaptation |
| :--- | :--- | :--- | :--- |
| **Process Node** | 130nm CMOS | 130nm BiCMOS (SiGe:C) | Retain 130nm CMOS primitives; optional SiGe HBT integration |
| **Digital Core Power (`VDPWR`)** | 1.8V | **1.2V** | Digital shift registers and control logic operate at 1.2V |
| **Analog / HV Power (`VAPWR`)** | 3.3V (5.0V tolerant) | **3.3V** | Analog switch matrix and high-voltage FETs operate at 3.3V |
| **Ground Reference (`VGND`)** | 0V | **0V** | Shared substrate ground reference |
| **Standard Cell Library** | `sky130_fd_sc_hd` | `sg13g2_stdcell` | Re-synthesize digital control logic with Yosys |
| **Primitive Device Library** | `sky130_fd_pr` | `sg13g2_pr` | Re-bind device symbols in Xschem and layouts in KLayout/Magic |

---

## 3. Detailed Architecture & Technical Interfaces

### 3.1 Top-Level Interface Pinout (`tt_um_tnt_mosbius`)

The top-level wrapper conforms to the TinyTapeout IHP shuttle pinout specifications:

* **Power & Control Rails:**
  * `VGND` (Ground reference, 0V)
  * `VDPWR` (Digital power, 1.2V)
  * `VAPWR` (Analog power, 3.3V)
  * `clk` (Digital shift clock)
  * `rst_n` (Active-low reset)
  * `ena` (Always-high chip enable)

* **Digital I/O Ports:**
  * `ui_in[0]` (`data_in`): Serial control bitstream input.
  * `ui_in[1]` (`enable`): Active-high enable mask for control register output updates.
  * `uo_out[0]` (`data_out`): Serial data output stream for daisy-chaining/readback verification.
  * `uo_out[7:1]`: Tied off to zero using tie-down cells (`sg13g2_tiel_1`).
  * `uio_in[7:0]`, `uio_out[7:0]`, `uio_oe[7:0]`: Standard bidir IOs, set as unused inputs.

* **Analog Pins (`ua[5:0]`):**
  * `ua[0]`: Reference Bias (`ibias`)
  * `ua[1]`: `Bus 1A`
  * `ua[2]`: `Bus 3A`
  * `ua[3]`: `Bus 5A`
  * `ua[4]`: `Bus 2B`
  * `ua[5]`: `Bus 4B`

### 3.2 Internal Analog Routing Busses

* `bus_A[6:1]` and `bus_B[6:1]`: Dual 6-wire internal analog busses connecting analog switch matrix columns to primitive sub-blocks (OTAs, differential pairs, mirrors, and discrete PMOS/NMOS arrays).

---

## 4. Subsystem Component Design & Device Mapping

### 4.1 Primitive Device Model Translation

| Sub-Block / Primitive | SKY130 Model (`sky130_fd_pr`) | IHP SG13G2 Model (`sg13g2_pr`) | Scaling / Adaptation Notes |
| :--- | :--- | :--- | :--- |
| **3.3V NMOS Switches / Arrays** | `nfet_g5v0d10v5` | `nfet33` | 3.3V thick-oxide NMOS; adjust W/L to match $R_{on}$ and drive strength. |
| **3.3V PMOS Switches / Arrays** | `pfet_g5v0d10v5` | `pfet33` | 3.3V thick-oxide PMOS; adjust W/L for $R_{on}$ parity. |
| **1.2V Core Logic Transistors** | `nfet3_01v8` | `nfet` | Core digital standard cell transistors (1.2V operation). |
| **1.2V Core PMOS Transistors** | `pfet3_01v8` | `pfet` | Core digital standard cell transistors (1.2V operation). |
| **Resistors** | `res_high_po` | `rhigh` / `rsil` | High-sheet poly resistors for bias networks. |
| **Capacitors** | `cap_mim_m3_1` | `cap_cmim` | MIM capacitors for frequency compensation / filtering. |
| **SiGe HBT (Optional)** | N/A | `npn13G2` | High-speed SiGe NPN transistor available for RF/low-noise stages. |

#### 4.1.1 BJT Model Derivative Strategy
To derive an IHP-BJT model (`npn13G2` / `npn13G2v`) from the standard IHP-CMOS model (`nfet33`):
1. **Terminal Equivalence:** Map CMOS 4-terminal pins $(G, D, S, B)$ to BJT 4-terminal pins $(B, C, E, SUB)$.
2. **Device Sizing & Biasing:** Replace CMOS aspect ratio $(W/L)$ and overdrive $(V_{GS}-V_{th})$ with BJT emitter width/length ($W_e, L_e, N_e$) and base-emitter voltage bias ($V_{BE}$).
3. **Schematic & LVS Integration:** Use `xschem/npn13G2.sym` and `xschem/diff_npn.sch` for Xschem capture and Netgen LVS extraction.

### 4.2 Standard Cell Mapping for Digital Control Logic

Digital control subsystems (`ctrl_top`, `ctrl_block`) manage the 192-bit control array (`ctrl[191:0]`):

| Logic Function | SKY130 Cell (`sky130_fd_sc_hd__*`) | IHP SG13G2 Cell (`sg13g2_stdcell_*`) |
| :--- | :--- | :--- |
| **2-Input AND Gate** | `and2_2`, `and2_4` | `sg13g2_and2_1`, `sg13g2_and2_2` |
| **Inverter** | `inv_1`, `inv_2` | `sg13g2_inv_1`, `sg13g2_inv_2` |
| **Clock Buffer** | `clkbuf_4`, `clkbuf_8` | `sg13g2_buf_2`, `sg13g2_buf_4` |
| **D-Flip-Flop w/ Reset** | `dfrtp_1` | `sg13g2_dfrpc_1` / `sg13g2_dfrq_1` |
| **Tie Low / Tie High** | `conb_1` | `sg13g2_tiel_1`, `sg13g2_tieh_1` |
| **Decoupling Capacitors** | `decap_3`, `decap_4`, `decap_6` | `sg13g2_decap_4`, `sg13g2_decap_8` |
| **Filler Cells** | `fill_1`, `fill_2` | `sg13g2_fill_1`, `sg13g2_fill_2` |

---

## 5. Scripted Physical Layout & Decap Generation (`py/`)

### 5.1 Python Grid & Pitch Parameters Adaptation (`py/common.py`)

Layout parameters must be modified from SKY130 standard cell geometry to IHP SG13G2 standard cell pitch and design rules:

* **Cell Height / Pitch:** Update `ROW_PITCH` and `COL_PITCH` according to `sg13g2_stdcell` LEF specifications.
* **Track Grids:** Update horizontal track pitch (`TRACK_H_PITCH`), vertical track pitch (`TRACK_V_PITCH`), track offsets, and metal widths (`TRACK_H_WIDTH`, `TRACK_V_WIDTH`) for SG13G2 Metal 1 and Metal 2 layers.
* **Via Definitions:** Adapt `VIAS` stack dictionary in `common.py` to route between SG13G2 Metal 1 (`met1`), Metal 2 (`met2`), and Metal 3 (`met3`) layers.
* **Decap Dictionary:** Update `Grid.FILL` dictionary to reference `sg13g2_decap_*` and `sg13g2_fill_*` cells.

### 5.2 Control Generator Scripts

* `gen_asw_ctrl.py` & `gen_dev_ctrl.py`: Re-target cell name references and generated Verilog decap instantiations (`ctrl_asw.decap.v`, `ctrl_dev_*.decap.v`) to use SG13G2 decap primitives (`sg13g2_decap_4`, `sg13g2_decap_8`).

---

## 6. EDA Toolchain Workflow & Verification Strategy

1. **Schematic Entry & Simulation:**
   * Re-bind Xschem symbols in `xschem/*.sch` from `sky130_fd_pr` to `sg13g2_pr`.
   * Update Ngspice simulation testbenches (`xschem/tb_*.sch`) to include IHP SG13G2 corner models (`corner.spice` / `sg13g2.lib`).
2. **Digital RTL Synthesis & Verification:**
   * Update `src/Makefile` to synthesize control RTL (`ctrl_top.v`, `ctrl_block.v`) targeting `sg13g2_stdcell.v`.
3. **Layout vs. Schematic (LVS):**
   * Perform LVS verification using Netgen (`tcl/lvs.tcl`) and KLayout LVS rule deck (`sg13g2.lylvs`) across the 1.2V and 3.3V power domains.
4. **Design Rule Checking (DRC):**
   * Execute full DRC using KLayout DRC engine (`sg13g2.lydrc`) and Magic DRC scripts.

---

## 7. Major Design Alternatives & Trade-Off Analysis

In accordance with architectural design guidelines, the major decisions for porting Mini-MOSbius to IHP SG13G2 were evaluated against three alternatives:

### 7.1 Voltage Domain & Level Shifting Architecture

* **Option A (Chosen): Dual Voltage Supply (1.2V Core / 3.3V Analog) with 1.2V->3.3V Level Shifters**
  * *Pros:* Preserves original Mini-MOSbius low-voltage digital power saving and 3.3V analog switch dynamic range/linearity.
  * *Cons:* Requires dedicated level shifters (`1.2V -> 3.3V`) on control lines.
  * *Reason for Selection:* Optimal balance of low digital power consumption and maximum analog switch performance using native IHP `nfet33`/`pfet33` devices.
* **Option B: Unified Single 3.3V Supply for Digital and Analog Subsystems**
  * *Pros:* Eliminates level shifters between digital control logic and analog switches.
  * *Cons:* Increases digital control power dissipation significantly; standard cells require 3.3V rated devices or custom gates.
  * *Reason for Rejection:* Higher power consumption and non-standard digital standard cell operation.
* **Option C: Unified Single 1.2V Supply for both Digital and Analog Subsystems**
  * *Pros:* Single power rail, low digital power, no level shifters.
  * *Cons:* Severely restricts analog switch dynamic range, $R_{on}$ performance, and headroom for differential pairs/OTAs.
  * *Reason for Rejection:* Degrades analog signal chain performance unacceptable for reconfigurable analog arrays.

### 7.2 Digital Control Layout & Decap Generation Strategy

* **Option A (Chosen): Scripted Placement & Decap Generation via Python (`py/*.py`)**
  * *Pros:* Directly ports Sylvain Munaut's procedural layout methodology; enables tight pitch matching with analog switch matrix.
  * *Cons:* Requires updating Python track/grid geometries and standard cell cell-width tables for SG13G2.
  * *Reason for Selection:* Maintains seamless integration with the existing custom physical layout pipeline.
* **Option B: Fully Automated Standard Cell Place & Route using OpenROAD**
  * *Pros:* Fully automated PnR flow using standard LEF/DEF tools.
  * *Cons:* Harder to enforce strict pitch and pin alignment with the procedural analog switch matrix.
  * *Reason for Rejection:* Requires extensive rework of the physical floorplan integration.
* **Option C: Manual Standard Cell Layout Capture in KLayout/Magic**
  * *Pros:* Fine-grained physical control over cell placement.
  * *Cons:* Highly time-consuming, prone to manual wiring errors, and difficult to maintain across PDK revisions.
  * *Reason for Rejection:* Inefficient and highly prone to human error.

### 7.3 Analog Building Block Device Selection

* **Option A (Chosen): Direct Mapping of Analog Primitives to 3.3V Thick-Oxide FETs (`nfet33`, `pfet33`)**
  * *Pros:* Pin-for-pin topology match with SkyWater 3.3V/5.0V FET primitives (`nfet_g5v0d10v5`, `pfet_g5v0d10v5`).
  * *Cons:* Does not exploit SiGe HBT speed capabilities for base CMOS blocks.
  * *Reason for Selection:* Ensures minimal topology changes and reliable baseline porting.
* **Option B: Hybrid SiGe HBT + 3.3V CMOS Architecture**
  * *Pros:* High transconductance and speed in OTAs/differential pairs using `npn13G2` SiGe HBTs.
  * *Cons:* Substantially changes biasing, footprint, and circuit dynamics of analog primitives.
  * *Reason for Rejection:* Recommended as a post-port optimization rather than baseline migration.
* **Option C: Thin-Oxide 1.2V FETs for Analog Primitives**
  * *Pros:* Higher speed and smaller area footprint.
  * *Cons:* Low voltage headroom and reduced analog dynamic range.
  * *Reason for Rejection:* Incompatible with 3.3V analog switch rail requirement.
