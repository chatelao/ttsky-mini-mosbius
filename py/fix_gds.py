#!/usr/bin/env python3
"""
GDS post-processing and layer remapping script for IHP SG13G2.
Remaps legacy SkyWater 130 layer definitions and previous incorrect layer maps
to official IHP SG13G2 layer definitions (e.g., prBoundary 189/4, Metal1 8/0,
Metal2 30/0, Metal3 50/0, Metal4 67/0, Metal5 125/0).
"""

import os
import struct
import sys

# SkyWater 130 / Legacy GDS -> IHP SG13G2 GDS layer mapping table
LAYER_MAP = {
    # prBoundary
    (235, 4): (189, 4),
    (236, 0): (189, 4),
    (81, 4): (189, 4),
    (81, 23): (189, 4),
    # NWell
    (64, 20): (31, 0),
    (64, 59): (31, 0),
    (64, 16): (31, 2),
    (64, 5): (31, 2),
    # Activ
    (65, 20): (1, 0),
    (65, 44): (1, 2),
    (65, 16): (1, 2),
    (65, 6): (1, 2),
    (65, 5): (1, 2),
    (65, 48): (1, 2),
    (1, 25): (1, 2),
    # GatPoly
    (66, 20): (10, 0),
    (66, 16): (10, 2),
    (66, 5): (10, 2),
    (66, 44): (10, 25),
    # li1 -> Metal1 (8)
    (67, 20): (8, 0),
    (67, 16): (8, 2),
    (67, 5): (8, 2),
    (67, 25): (8, 25),
    (67, 44): (8, 25),
    # met1 -> Metal2 (30)
    (68, 20): (30, 0),
    (68, 16): (30, 2),
    (68, 5): (30, 2),
    (68, 44): (30, 25),
    # met2 -> Metal3 (50)
    (69, 20): (50, 0),
    (69, 16): (50, 2),
    (69, 5): (50, 2),
    (69, 2): (50, 2),
    (69, 25): (50, 25),
    (69, 44): (50, 25),
    # met3 -> Metal4 (67)
    (70, 20): (67, 0),
    (70, 16): (67, 2),
    (70, 5): (67, 2),
    (70, 25): (67, 25),
    (70, 44): (67, 25),
    # met4 -> Metal5 (125) - precheck only allows (125, 0)
    (71, 20): (125, 0),
    (71, 16): (125, 0),
    (71, 5): (125, 0),
    (71, 2): (125, 0),
    (71, 25): (125, 0),
    (125, 2): (125, 0),
    (125, 25): (125, 0),
    # met5 -> Metal5
    (72, 20): (125, 0),
    (72, 2): (125, 0),
    (75, 20): (125, 0),
    (78, 44): (67, 25),
    (83, 44): (67, 25),
    (93, 44): (67, 25),
    (94, 20): (50, 0),
    (95, 20): (67, 0),
    (122, 16): (125, 0),
    (125, 20): (125, 0),
}


def remap_gds_stream(fn_gds_in, fn_gds_out, layer_map=LAYER_MAP):
    """Pure-Python binary GDSII stream parser and layer remapper."""
    with open(fn_gds_in, "rb") as f_in:
        data = f_in.read()

    out = bytearray()
    idx = 0
    length_data = len(data)

    def process_element(records):
        layer_idx = None
        dt_idx = None
        curr_l = None
        curr_d = 0

        for i, (r_id, r_type, r_len, r_data) in enumerate(records):
            if r_id == 0x0D:  # LAYER
                layer_idx = i
                curr_l = struct.unpack(">h", r_data)[0]
            elif r_id in (0x0E, 0x16, 0x30):  # DATATYPE / TEXTTYPE / BOXTYPE
                dt_idx = i
                curr_d = struct.unpack(">h", r_data)[0]

        if curr_l is not None and (curr_l, curr_d) in layer_map:
            new_l, new_d = layer_map[(curr_l, curr_d)]
            if layer_idx is not None:
                records[layer_idx] = (0x0D, records[layer_idx][1], 6, struct.pack(">h", new_l))
            if dt_idx is not None:
                records[dt_idx] = (records[dt_idx][0], records[dt_idx][1], 6, struct.pack(">h", new_d))

        for r_id, r_type, r_len, r_data in records:
            out.extend(struct.pack(">HH", r_len, r_type))
            out.extend(r_data)

    curr_elem = []
    in_elem = False

    while idx < length_data:
        if idx + 4 > length_data:
            break
        rec_len, rec_type = struct.unpack(">HH", data[idx : idx + 4])
        if rec_len < 4:
            break
        rec_data = data[idx + 4 : idx + rec_len]
        rec_id = rec_type >> 8

        if rec_id in (0x08, 0x09, 0x0C, 0x2F):  # BOUNDARY, PATH, TEXT, BOX
            if in_elem and curr_elem:
                process_element(curr_elem)
                curr_elem = []
            in_elem = True
            curr_elem.append((rec_id, rec_type, rec_len, rec_data))
        elif rec_id == 0x11:  # ENDEL
            if in_elem:
                curr_elem.append((rec_id, rec_type, rec_len, rec_data))
                process_element(curr_elem)
                curr_elem = []
                in_elem = False
            else:
                out.extend(struct.pack(">HH", rec_len, rec_type))
                out.extend(rec_data)
        else:
            if in_elem:
                curr_elem.append((rec_id, rec_type, rec_len, rec_data))
            else:
                out.extend(struct.pack(">HH", rec_len, rec_type))
                out.extend(rec_data)

        idx += rec_len

    if in_elem and curr_elem:
        process_element(curr_elem)

    with open(fn_gds_out, "wb") as f_out:
        f_out.write(out)


def main(argv0, fn_gds_in, fn_gds_out):
    remap_gds_stream(fn_gds_in, fn_gds_out)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input.gds> <output.gds>")
        sys.exit(1)
    main(*sys.argv)
