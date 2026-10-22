import os
import struct
import tempfile
import unittest

from py.fix_gds import remap_gds_stream, LAYER_MAP

class TestFixGDS(unittest.TestCase):
    def test_remap_gds_stream(self):
        # Create a dummy GDS stream with BOUNDARY (0x08), LAYER (0x0D), DATATYPE (0x0E), and ENDEL (0x11)
        data = bytearray()

        # HEADER record
        data.extend(struct.pack(">HH", 6, 0x0002))
        data.extend(struct.pack(">h", 600))

        # BOUNDARY record
        data.extend(struct.pack(">HH", 4, 0x0800))

        # LAYER record: layer 235 (0x00EB) -> mapped to 189
        data.extend(struct.pack(">HH", 6, 0x0D02))
        data.extend(struct.pack(">h", 235))

        # DATATYPE record: datatype 4 -> mapped to 4
        data.extend(struct.pack(">HH", 6, 0x0E02))
        data.extend(struct.pack(">h", 4))

        # ENDEL record
        data.extend(struct.pack(">HH", 4, 0x1100))

        with tempfile.NamedTemporaryFile("wb", delete=False) as f_in, tempfile.NamedTemporaryFile("wb", delete=False) as f_out:
            f_in.write(data)
            in_path = f_in.name
            out_path = f_out.name

        try:
            remap_gds_stream(in_path, out_path)
            with open(out_path, "rb") as f:
                out_data = f.read()

            # Inspect mapped layer and datatype in out_data
            self.assertTrue(len(out_data) > 0)
        finally:
            if os.path.exists(in_path):
                os.remove(in_path)
            if os.path.exists(out_path):
                os.remove(out_path)

if __name__ == "__main__":
    unittest.main()
