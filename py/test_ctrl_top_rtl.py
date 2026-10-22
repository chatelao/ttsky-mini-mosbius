#!/usr/bin/env python3
"""
Unit tests for Mini-MOSbius control top RTL structure, 192-bit control bitstream,
and procedural decap layout generators for IHP SG13G2.
"""

import os
import re
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from py.common import COL_PITCH, ROW_PITCH, Grid


class TestCtrlTopRTL(unittest.TestCase):

    def setUp(self):
        self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.ctrl_top_path = os.path.join(self.repo_root, "src", "ctrl_top.v")

    def test_bitstream_length(self):
        """Verify that ctrl_top.v output bus is 192 bits and matches ctrl_block N parameters."""
        self.assertTrue(os.path.exists(self.ctrl_top_path), f"File not found: {self.ctrl_top_path}")

        with open(self.ctrl_top_path, "r") as f:
            content = f.read()

        # Check 192-bit ctrl_out declaration [191:0]
        out_match = re.search(r"output\s+wire\s+\[191:0\]\s+ctrl_out", content)
        self.assertIsNotNone(out_match, "ctrl_out output port declaration [191:0] not found in ctrl_top.v")

        # ASW generator loop count
        asw_loop_match = re.search(r"for\s*\(\s*i\s*=\s*0;\s*i\s*<\s*(\d+);\s*i\s*=\s*i\s*\+\s*1\s*\)", content)
        self.assertIsNotNone(asw_loop_match, "ASW column generator loop not found in ctrl_top.v")
        asw_count = int(asw_loop_match.group(1))

        # ASW block N parameter inside generate loop
        asw_n_match = re.search(r"blk_I\s*\(\s*\n.*?\.\s*N\s*\(\s*(\d+)\s*\)", content, re.DOTALL)
        if not asw_n_match:
            asw_n_match = re.search(r"\.\s*N\s*\(\s*(\d+)\s*\)\s*\n\s*\)\s*blk_I", content)
        self.assertIsNotNone(asw_n_match, "ASW block .N parameter not found")
        asw_n = int(asw_n_match.group(1))

        asw_total_bits = asw_count * asw_n
        self.assertEqual(asw_total_bits, 156, f"Expected 156 ASW control bits, got {asw_total_bits}")

        # Find all device control block instantiations and their .N parameters
        # e.g. ctrl_block #(\n...\n.N (6)\n) blk_pmos_dual_I (
        dev_n_matches = re.findall(r"ctrl_block\s*#\s*\(\s*\n.*?\.\s*N\s*\(\s*(\d+)\s*\)\s*\n\s*\)\s*blk_(?!I\b)[a-z0-9_]+_I", content, re.DOTALL)
        dev_n_values = [int(val) for val in dev_n_matches]
        dev_total_bits = sum(dev_n_values)
        self.assertEqual(dev_total_bits, 36, f"Expected 36 device control bits, got {dev_total_bits} ({dev_n_values})")

        total_bitstream_bits = asw_total_bits + dev_total_bits
        self.assertEqual(
            total_bitstream_bits,
            192,
            f"Expected total bitstream length of 192 bits, calculated {total_bitstream_bits}"
        )

    def test_procedural_decap_generators(self):
        """Verify that py/gen_asw_ctrl.py and py/gen_dev_ctrl.py generate valid SG13G2 decaps."""
        asw_script = os.path.join(self.repo_root, "py", "gen_asw_ctrl.py")
        dev_script = os.path.join(self.repo_root, "py", "gen_dev_ctrl.py")

        res_asw = subprocess.run(
            [sys.executable, asw_script, "decap"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        self.assertIn("sg13g2_decap_", res_asw.stdout)
        self.assertIn(".VDPWR (VDPWR)", res_asw.stdout)
        self.assertIn(".VGND (VGND)", res_asw.stdout)

        res_dev = subprocess.run(
            [sys.executable, dev_script, "decap", "first", "1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        self.assertIn("sg13g2_decap_", res_dev.stdout)
        self.assertIn(".VDPWR (VDPWR)", res_dev.stdout)

    def test_common_grid_parameters(self):
        """Verify standard cell grid parameters for IHP SG13G2 in py/common.py."""
        self.assertEqual(ROW_PITCH, 3780, "IHP SG13G2 ROW_PITCH should be 3780 nm")
        self.assertEqual(COL_PITCH, 480, "IHP SG13G2 COL_PITCH should be 480 nm")

        # Test Grid decap generation with VDPWR / VGND
        g = Grid(10, 2)
        g.add_cell("decap_test", g.FILL[4], (0, 0), 0)
        decap_lines = "\n".join(g.gen_decap())
        self.assertIn("sg13g2_decap_4", decap_lines)
        self.assertIn(".VDPWR (VDPWR)", decap_lines)
        self.assertIn(".VGND (VGND)", decap_lines)


if __name__ == "__main__":
    unittest.main()
