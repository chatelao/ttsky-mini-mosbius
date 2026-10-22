/*
 * BlackBox for IHP SG13G2 standard cells so we can run the file through
 * yosys for elaboration
 *
 * Copyright (c) 2025 Sylvain Munaut
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none


(* blackbox *)
module sg13g2_buf_2 (
    output wire X,
    input  wire A,
    input  wire VDPWR,
    input  wire VGND
);
endmodule

(* blackbox *)
module sg13g2_buf_4 (
    output wire X,
    input  wire A,
    input  wire VDPWR,
    input  wire VGND
);
endmodule

(* blackbox *)
module sg13g2_buf_8 (
    output wire X,
    input  wire A,
    input  wire VDPWR,
    input  wire VGND
);
endmodule

(* blackbox *)
module sg13g2_buf_16 (
    output wire X,
    input  wire A,
    input  wire VDPWR,
    input  wire VGND
);
endmodule

(* blackbox *)
module sg13g2_dlybuf_1 (
    output wire X,
    input  wire A,
    input  wire VDPWR,
    input  wire VGND
);
endmodule

(* blackbox *)
module sg13g2_and2_1 (
    output wire X,
    input  wire A,
    input  wire B,
    input  wire VDPWR,
    input  wire VGND
);
endmodule

(* blackbox *)
module sg13g2_and2_2 (
    output wire X,
    input  wire A,
    input  wire B,
    input  wire VDPWR,
    input  wire VGND
);
endmodule

(* blackbox *)
module sg13g2_inv_1 (
    output wire Y,
    input  wire A,
    input  wire VDPWR,
    input  wire VGND
);
endmodule

(* blackbox *)
module sg13g2_inv_2 (
    output wire Y,
    input  wire A,
    input  wire VDPWR,
    input  wire VGND
);
endmodule

(* blackbox *)
module sg13g2_dfrpc_1 (
    output wire Q,
    input  wire CLK,
    input  wire RESET_B,
    input  wire D,
    input  wire VDPWR,
    input  wire VGND
);
endmodule

(* blackbox *)
module sg13g2_antenna_1 (
    inout  wire DIODE,
    input  wire VDPWR,
    input  wire VGND
);
endmodule

(* blackbox *)
module sg13g2_decap_4 (
    input  wire VDPWR,
    input  wire VGND
);
endmodule

(* blackbox *)
module sg13g2_decap_8 (
    input  wire VDPWR,
    input  wire VGND
);
endmodule

(* blackbox *)
module sg13g2_tiel_1 (
    output wire X,
    input  wire VDPWR,
    input  wire VGND
);
endmodule

(* blackbox *)
module sg13g2_tieh_1 (
    output wire X,
    input  wire VDPWR,
    input  wire VGND
);
endmodule

(* blackbox *)
module mosbius (
	input wire VGND,
	input wire VDPWR,
	input wire VAPWR,
	inout wire [6:1] bus_A,
	inout wire [6:1] bus_B,
	inout wire ibias,
	input wire [2:0] cfga_otan_inp,
	input wire [5:0] cfga_otan_outp,
	input wire [5:0] cfga_mirn_a,
	input wire [5:0] cfga_mirp_a,
	input wire [2:0] cfga_dpn_inp,
	input wire [5:0] cfga_dpn_outp,
	input wire [2:0] cfga_dpp_inp,
	input wire [5:0] cfga_dpp_outp,
	input wire [5:0] cfga_nfeta_d,
	input wire [5:0] cfga_nfeta_g,
	input wire [5:0] cfga_nfeta_s,
	input wire [5:0] cfga_pfeta_d,
	input wire [5:0] cfga_pfeta_g,
	input wire [5:0] cfga_pfeta_s,
	input wire [2:0] cfgb_otan_inm,
	input wire [5:0] cfgb_otan_outm,
	input wire [5:0] cfgb_mirn_b,
	input wire [5:0] cfgb_mirp_b,
	input wire [2:0] cfgb_dpn_inm,
	input wire [5:0] cfgb_dpn_outm,
	input wire [2:0] cfgb_dpp_inm,
	input wire [5:0] cfgb_dpp_outm,
	input wire [5:0] cfgb_nfetb_d,
	input wire [5:0] cfgb_nfetb_g,
	input wire [5:0] cfgb_nfetb_s,
	input wire [5:0] cfgb_pfetb_d,
	input wire [5:0] cfgb_pfetb_g,
	input wire [5:0] cfgb_pfetb_s,
	input wire [5:0] cfg_bus_pwr,
	input wire [5:0] cfg_bus_short,
	input wire [1:0] ctrl_otan_tail,
	input wire [1:0] ctrl_otan_mode,
	input wire [1:0] ctrl_mirp_a,
	input wire [1:0] ctrl_mirn_a,
	input wire [1:0] ctrl_mirp_b,
	input wire [1:0] ctrl_mirn_b,
	input wire [1:0] ctrl_dpp_tail,
	input wire [1:0] ctrl_dpn_tail,
	input wire ctrl_dpp_source,
	input wire ctrl_dpn_source,
	input wire ctrl_pfeta_source,
	input wire ctrl_nfeta_source,
	input wire [1:0] ctrl_pfeta_width,
	input wire [1:0] ctrl_nfeta_width,
	input wire ctrl_pfetb_source,
	input wire ctrl_nfetb_source,
	input wire [1:0] ctrl_pfetb_width,
	input wire [1:0] ctrl_nfetb_width
);
endmodule
