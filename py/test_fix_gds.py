import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from py.fix_gds import LAYER_MAP, main, remap_gds_stream
from py.verify_cicd_config import parse_gds_layers


def create_mock_gds_file(filepath, elements):
    """Creates a mock binary GDSII file with given elements.
    elements is a list of tuples: (elem_type, layer, datatype)
    elem_type: 0x08 (BOUNDARY), 0x09 (PATH), 0x0C (TEXT), 0x2F (BOX)
    """
    data = bytearray()
    # HEADER record (0x0002)
    data.extend(struct.pack(">HH", 6, 0x0002))
    data.extend(struct.pack(">h", 600))  # GDS version 6.00

    # BGNLIB record (0x0102)
    data.extend(struct.pack(">HH", 28, 0x0102))
    data.extend(b"\x00" * 24)

    # LIBNAME record (0x0206)
    libname = b"TESTLIB\x00"
    data.extend(struct.pack(">HH", 4 + len(libname), 0x0206))
    data.extend(libname)

    # BGNSTR record (0x0502)
    data.extend(struct.pack(">HH", 28, 0x0502))
    data.extend(b"\x00" * 24)

    # STRNAME record (0x0606)
    strname = b"TOP\x00"
    data.extend(struct.pack(">HH", 4 + len(strname), 0x0606))
    data.extend(strname)

    for elem_type, layer, datatype in elements:
        # Element start (BOUNDARY=0x0800, PATH=0x0900, TEXT=0x0C00, BOX=0x2F00)
        data.extend(struct.pack(">HH", 4, elem_type << 8))

        # LAYER record (0x0D02)
        data.extend(struct.pack(">HH", 6, 0x0D02))
        data.extend(struct.pack(">h", layer))

        # DATATYPE / TEXTTYPE / BOXTYPE record (0x0E02 / 0x1602 / 0x3002)
        if elem_type == 0x0C:
            dt_rec = 0x1602
        elif elem_type == 0x2F:
            dt_rec = 0x3002
        else:
            dt_rec = 0x0E02
        data.extend(struct.pack(">HH", 6, dt_rec))
        data.extend(struct.pack(">h", datatype))

        # ENDEL record (0x1100)
        data.extend(struct.pack(">HH", 4, 0x1100))

    # ENDSTR record (0x0700)
    data.extend(struct.pack(">HH", 4, 0x0700))
    # ENDLIB record (0x0400)
    data.extend(struct.pack(">HH", 4, 0x0400))

    with open(filepath, "wb") as f:
        f.write(data)


class TestFixGDS(unittest.TestCase):

    def test_layer_map_entries(self):
        # Verify key layer mappings from SkyWater 130 to IHP SG13G2
        self.assertEqual(LAYER_MAP.get((235, 4)), (189, 4))  # prBoundary
        self.assertEqual(LAYER_MAP.get((68, 20)), (30, 0))   # met1 -> Metal2
        self.assertEqual(LAYER_MAP.get((67, 20)), (8, 0))    # li1 -> Metal1
        self.assertEqual(LAYER_MAP.get((69, 20)), (50, 0))   # met2 -> Metal3
        self.assertEqual(LAYER_MAP.get((70, 20)), (67, 0))   # met3 -> Metal4
        self.assertEqual(LAYER_MAP.get((71, 20)), (125, 0))  # met4 -> Metal5

    def test_remap_gds_stream(self):
        with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".gds") as f_in, \
             tempfile.NamedTemporaryFile("wb", delete=False, suffix=".gds") as f_out:
            in_path = f_in.name
            out_path = f_out.name

        try:
            # Create mock GDS with SkyWater 130 layers
            elements = [
                (0x08, 235, 4),   # prBoundary (235, 4) -> (189, 4)
                (0x08, 68, 20),   # met1 (68, 20) -> (30, 0)
                (0x08, 67, 20),   # li1 (67, 20) -> (8, 0)
                (0x08, 100, 0),   # Unmapped layer (100, 0) -> (100, 0)
            ]
            create_mock_gds_file(in_path, elements)

            in_layers = parse_gds_layers(in_path)
            self.assertIn((235, 4), in_layers)
            self.assertIn((68, 20), in_layers)
            self.assertIn((67, 20), in_layers)
            self.assertIn((100, 0), in_layers)

            # Perform remapping
            remap_gds_stream(in_path, out_path)

            out_layers = parse_gds_layers(out_path)
            self.assertNotIn((235, 4), out_layers)
            self.assertNotIn((68, 20), out_layers)
            self.assertNotIn((67, 20), out_layers)

            self.assertIn((189, 4), out_layers)
            self.assertIn((30, 0), out_layers)
            self.assertIn((8, 0), out_layers)
            self.assertIn((100, 0), out_layers)
        finally:
            if os.path.exists(in_path):
                os.remove(in_path)
            if os.path.exists(out_path):
                os.remove(out_path)

    def test_main_cli(self):
        with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".gds") as f_in, \
             tempfile.NamedTemporaryFile("wb", delete=False, suffix=".gds") as f_out:
            in_path = f_in.name
            out_path = f_out.name

        try:
            elements = [(0x08, 235, 4)]
            create_mock_gds_file(in_path, elements)

            main("fix_gds.py", in_path, out_path)

            out_layers = parse_gds_layers(out_path)
            self.assertIn((189, 4), out_layers)
        finally:
            if os.path.exists(in_path):
                os.remove(in_path)
            if os.path.exists(out_path):
                os.remove(out_path)


if __name__ == "__main__":
    unittest.main()
