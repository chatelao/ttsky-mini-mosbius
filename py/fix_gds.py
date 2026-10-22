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
    (235, 4): (189, 4),   # Sky130 prBoundary.boundary -> IHP SG13G2 prBoundary (189/4)
    (236, 0): (189, 4),   # Sky130 bound -> IHP SG13G2 prBoundary (189/4)
    (81, 4): (189, 4),
    (81, 23): (189, 4),
    (64, 20): (31, 0),    # Sky130 nwell -> IHP nwell (31/0)
    (64, 16): (31, 2),    # Sky130 nwell pin -> IHP nwell pin (31/2)
    (64, 5): (31, 2),
    (64, 59): (31, 0),
    (65, 20): (1, 0),     # Sky130 diff -> IHP Activ (1/0)
    (65, 44): (1, 25),    # Sky130 diff text -> IHP Activ text (1/25)
    (1, 25): (1, 25),
    (66, 20): (10, 0),    # Sky130 poly -> IHP GatPoly (10/0)
    (66, 15): (10, 2),    # Sky130 poly pin -> IHP GatPoly pin (10/2)
    (66, 44): (10, 25),   # Sky130 poly text -> IHP GatPoly text (10/25)
    (67, 20): (8, 0),     # Sky130 li1 -> IHP Metal1 (8/0)
    (67, 16): (8, 2),     # Sky130 li1 pin -> IHP Metal1 pin (8/2)
    (67, 5): (8, 2),      # Sky130 li1 pin -> IHP Metal1 pin (8/2)
    (67, 25): (8, 25),    # Sky130 li1 text -> IHP Metal1 text (8/25)
    (67, 44): (8, 25),    # Sky130 li1 text -> IHP Metal1 text (8/25)
    (68, 20): (30, 0),    # Sky130 met1 -> IHP Metal2 (30/0)
    (68, 16): (30, 2),    # Sky130 met1 pin -> IHP Metal2 pin (30/2)
    (68, 44): (30, 25),   # Sky130 met1 text -> IHP Metal2 text (30/25)
    (68, 5): (30, 2),     # Sky130 met1 pin -> IHP Metal2 pin (30/2)
    (69, 20): (50, 0),    # Sky130 met2 -> IHP Metal3 (50/0)
    (69, 25): (50, 25),   # Sky130 met2 text -> IHP Metal3 text (50/25)
    (69, 44): (50, 25),   # Sky130 met2 text -> IHP Metal3 text (50/25)
    (69, 2): (50, 2),     # Sky130 met2 pin -> IHP Metal3 pin (50/2)
    (70, 20): (67, 0),    # Sky130 met3 -> IHP Metal4 (67/0)
    (70, 16): (67, 2),    # Sky130 met3 pin -> IHP Metal4 pin (67/2)
    (70, 44): (67, 25),   # Sky130 met3 text -> IHP Metal4 text (67/25)
    (70, 25): (67, 25),
    (70, 5): (67, 2),     # Sky130 met3 pin -> IHP Metal4 pin (67/2)
    (71, 20): (125, 0),   # Sky130 met4 -> IHP Metal5 (125/0)
    (71, 16): (125, 2),   # Sky130 met4 pin -> IHP Metal5 pin (125/2)
    (71, 25): (125, 25),
    (71, 5): (125, 2),    # Sky130 met4 pin -> IHP Metal5 pin (125/2)
    (71, 2): (125, 2),
    (72, 20): (125, 0),
    (72, 2): (125, 2),
    (75, 20): (125, 0),
    (78, 44): (67, 25),
    (83, 44): (67, 25),
    (93, 44): (67, 25),
    (94, 20): (50, 0),
    (95, 20): (67, 0),
    (122, 16): (125, 2),
    (125, 20): (125, 0),
}


def remap_gds_stream(fn_gds_in, fn_gds_out, layer_map=LAYER_MAP):
    """Pure-Python binary GDSII stream parser and layer remapper."""
    if not os.path.exists(fn_gds_in):
        raise FileNotFoundError(f"GDS input file does not exist: {fn_gds_in}")

    file_size = os.path.getsize(fn_gds_in)
    if file_size == 0:
        raise ValueError(f"GDS input file is empty: {fn_gds_in}")

    with open(fn_gds_in, "rb") as f_in:
        data = f_in.read()

    length_data = len(data)
    if length_data < 6:
        raise ValueError(f"Invalid GDS header length ({length_data} bytes): {fn_gds_in}")

    # Validate GDS HEADER record (rec_len >= 6, rec_type 0x0002)
    header_len, header_type = struct.unpack(">HH", data[:4])
    if header_type != 0x0002 or header_len < 6:
        raise ValueError(f"Invalid GDSII magic record header in file {fn_gds_in}: len={header_len}, type=0x{header_type:04x}")

    out = bytearray()
    idx = 0
    curr_element_type = None
    record_count = 0

    while idx < length_data:
        if idx + 4 > length_data:
            raise ValueError(f"Truncated GDS record header at byte offset {idx} in {fn_gds_in}")
        rec_len, rec_type = struct.unpack(">HH", data[idx : idx + 4])
        if rec_len < 4:
            raise ValueError(f"Invalid GDS record length {rec_len} at byte offset {idx} in {fn_gds_in}")
        if idx + rec_len > length_data:
            raise ValueError(f"GDS record exceeds file length ({idx + rec_len} > {length_data}) in {fn_gds_in}")

        rec_data = data[idx + 4 : idx + rec_len]
        record_count += 1

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

    if record_count == 0 or len(out) == 0:
        raise ValueError(f"Failed to extract valid GDS records from {fn_gds_in}")

    with open(fn_gds_out, "wb") as f_out:
        f_out.write(out)

    if not os.path.exists(fn_gds_out) or os.path.getsize(fn_gds_out) == 0:
        raise RuntimeError(f"GDS remapped output file was not properly written or is empty: {fn_gds_out}")


def main(argv0, fn_gds_in, fn_gds_out):
    remap_gds_stream(fn_gds_in, fn_gds_out)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input.gds> <output.gds>")
        sys.exit(1)
    main(*sys.argv)
