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
