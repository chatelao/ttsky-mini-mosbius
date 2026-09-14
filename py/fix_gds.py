#!/usr/bin/env python3
"""
GDS post-processing and layer remapping script for IHP SG13G2.
Remaps legacy SkyWater 130 layer definitions (e.g., prBoundary 235/4)
to IHP SG13G2 layer definitions (e.g., prBoundary 189/4).
"""

import os
import struct
import sys

# SkyWater 130 -> IHP SG13G2 GDS layer mapping table
LAYER_MAP = {
    (235, 4): (189, 4),  # Sky130 prBoundary.boundary -> IHP SG13G2 prBoundary (189/4)
    (236, 0): (189, 4),  # Sky130 bound -> IHP SG13G2 prBoundary (189/4)
    (64, 20): (31, 0),   # Sky130 nwell -> IHP nwell (31/0)
    (64, 16): (31, 2),   # Sky130 nwell pin -> IHP nwell pin (31/2)
    (65, 20): (1, 0),    # Sky130 diff -> IHP Activ (1/0)
    (65, 44): (1, 25),   # Sky130 diff text -> IHP Activ text (1/25)
    (66, 20): (10, 0),   # Sky130 poly -> IHP GatPoly (10/0)
    (66, 15): (10, 2),   # Sky130 poly pin -> IHP GatPoly pin (10/2)
    (66, 44): (10, 25),  # Sky130 poly text -> IHP GatPoly text (10/25)
    (67, 20): (67, 20),  # Sky130 li1 -> IHP Metal1 (67/20)
    (67, 16): (67, 20),  # Sky130 li1 pin -> IHP Metal1 (67/20)
    (67, 44): (67, 25),  # Sky130 li1 text -> IHP Metal1 text (67/25)
    (68, 20): (69, 20),  # Sky130 met1 -> IHP Metal2 (69/20)
    (68, 16): (69, 20),  # Sky130 met1 pin -> IHP Metal2 (69/20)
    (68, 44): (69, 25),  # Sky130 met1 text -> IHP Metal2 text (69/25)
    (68, 5): (69, 2),    # Sky130 met1 pin -> IHP Metal2 pin (69/2)
    (69, 20): (70, 20),  # Sky130 met2 -> IHP Metal3 (70/20)
    (69, 44): (70, 25),  # Sky130 met2 text -> IHP Metal3 text (70/25)
    (70, 20): (71, 20),  # Sky130 met3 -> IHP Metal4 (71/20)
    (70, 16): (71, 20),  # Sky130 met3 pin -> IHP Metal4 (71/20)
    (70, 44): (71, 25),  # Sky130 met3 text -> IHP Metal4 text (71/25)
    (70, 5): (71, 2),    # Sky130 met3 pin -> IHP Metal4 pin (71/2)
    (71, 20): (72, 20),  # Sky130 met4 -> IHP Metal5 (72/20)
    (71, 16): (72, 20),  # Sky130 met4 pin -> IHP Metal5 (72/20)
    (71, 5): (72, 2),    # Sky130 met4 pin -> IHP Metal5 pin (72/2)
}


def remap_gds_stream(fn_gds_in, fn_gds_out, layer_map=LAYER_MAP):
    """Pure-Python binary GDSII stream parser and layer remapper."""
    with open(fn_gds_in, "rb") as f_in:
        data = f_in.read()

    out = bytearray()
    idx = 0
    length_data = len(data)
    curr_element_type = None

    while idx < length_data:
        if idx + 4 > length_data:
            break
        rec_len, rec_type = struct.unpack(">HH", data[idx : idx + 4])
        if rec_len < 4:
            break
        rec_data = data[idx + 4 : idx + rec_len]

        rec_id = rec_type >> 8

        new_rec_data = rec_data

        if rec_id in (0x08, 0x09, 0x0C, 0x2F):  # BOUNDARY, PATH, TEXT, BOX
            curr_element_type = rec_id
            curr_layer = None
            elem_start = len(out)
        elif rec_id == 0x0D and curr_element_type is not None:  # LAYER
            curr_layer = struct.unpack(">h", rec_data)[0]
        elif rec_id in (0x0E, 0x16, 0x30) and curr_element_type is not None:  # DATATYPE / TEXTTYPE / BOXTYPE
            curr_dt = struct.unpack(">h", rec_data)[0]
            if curr_layer is not None and (curr_layer, curr_dt) in layer_map:
                new_l, new_d = layer_map[(curr_layer, curr_dt)]
                new_rec_data = struct.pack(">h", new_d)
                l_bytes = struct.pack(">h", new_l)
                for p in range(len(out) - 6, elem_start - 1, -1):
                    if out[p : p + 4] == b"\x00\x06\x0d\x02":
                        out[p + 4 : p + 6] = l_bytes
                        break
        elif rec_id == 0x11:  # ENDEL
            curr_element_type = None

        out.extend(struct.pack(">HH", rec_len, rec_type))
        out.extend(new_rec_data)
        idx += rec_len

    with open(fn_gds_out, "wb") as f_out:
        f_out.write(out)


def main(argv0, fn_gds_in, fn_gds_out):
    remap_gds_stream(fn_gds_in, fn_gds_out)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input.gds> <output.gds>")
        sys.exit(1)
    main(*sys.argv)
