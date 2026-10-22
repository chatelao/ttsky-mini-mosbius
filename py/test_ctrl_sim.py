#!/usr/bin/env python3
"""
Unit tests and behavioral simulation for Mini-MOSbius 192-bit control bitstream shift register chain.
Verifies functional behavior, bit propagation, reset clearing, enable gating, and field mappings.
"""

import os
import re
import unittest


class CtrlShiftRegisterSim:
    """
    Behavioral cycle-accurate model of the 192-bit ctrl_top shift register chain.
    """

    def __init__(self):
        # 192 flip-flops in the shift chain
        # Bits 0..155: 26 ASW blocks * 6 bits
        # Bits 156..161: PMOS dual (6 bits)
        # Bits 162..167: PMOS CM (6 bits)
        # Bits 168..171: PMOS DP (4 bits)
        # Bits 172..175: NMOS DP (4 bits)
        # Bits 176..183: NMOS CM (8 bits)
        # Bits 184..189: NMOS dual (6 bits)
        # Bits 190..191: NMOS OTA (2 bits)
        self.ffs = [0] * 192
        self.rst_n = 1
        self.enable = 1

    def reset(self):
        self.rst_n = 0
        self.ffs = [0] * 192
        self.rst_n = 1

    def clock_tick(self, data_in):
        """
        Executes one positive clock edge transition.
        Shift direction: bit data_in enters at index 0, shift right through index 191.
        """
        if not self.rst_n:
            self.ffs = [0] * 192
            return 0

        # Output bit before shift
        data_out = self.ffs[191]

        # Shift right
        self.ffs = [data_in] + self.ffs[:-1]
        return data_out

    def get_ctrl_out(self):
        """
        Returns 192-bit list representing ctrl_out masked by enable.
        """
        if not self.enable:
            return [0] * 192
        return list(self.ffs)


class TestCtrlShiftRegisterSim(unittest.TestCase):

    def setUp(self):
        self.sim = CtrlShiftRegisterSim()
        self.sim.reset()

    def test_initial_state(self):
        ctrl = self.sim.get_ctrl_out()
        self.assertEqual(len(ctrl), 192)
        self.assertTrue(all(b == 0 for b in ctrl))

    def test_single_bit_propagation_192_cycles(self):
        """Verify a single '1' bit takes exactly 192 clock cycles to propagate from data_in to data_out."""
        # Cycle 1: input 1
        data_out = self.sim.clock_tick(1)
        self.assertEqual(data_out, 0)
        self.assertEqual(self.sim.get_ctrl_out()[0], 1)
        self.assertTrue(all(b == 0 for b in self.sim.get_ctrl_out()[1:]))

        # Cycles 2..192: input 0
        for cycle in range(2, 193):
            data_out = self.sim.clock_tick(0)
            self.assertEqual(data_out, 0)
            # Bit '1' should be at index (cycle - 1)
            ctrl = self.sim.get_ctrl_out()
            self.assertEqual(ctrl[cycle - 1], 1)
            self.assertEqual(sum(ctrl), 1)

        # Cycle 193: input 0 -> data_out produces the shifted bit '1'
        data_out = self.sim.clock_tick(0)
        self.assertEqual(data_out, 1)

    def test_full_bitstream_pattern_propagation(self):
        """Shift a 192-bit pattern and verify bit exactness in shift register state."""
        pattern = [(i * 7 + 3) % 2 for i in range(192)]

        # Shift in pattern bit by bit
        for bit in pattern:
            self.sim.clock_tick(bit)

        # The shift register flip-flops (index 0..191) should contain pattern in reverse shift order
        expected = list(reversed(pattern))
        self.assertEqual(self.sim.get_ctrl_out(), expected)

    def test_reset_behavior(self):
        """Assert reset_n active-low clears all 192 flip-flops."""
        # Fill shift register with all 1s
        for _ in range(192):
            self.sim.clock_tick(1)
        self.assertEqual(sum(self.sim.get_ctrl_out()), 192)

        # Apply reset
        self.sim.reset()
        self.assertEqual(sum(self.sim.get_ctrl_out()), 0)

    def test_enable_masking(self):
        """Verify enable gating masks all ctrl_out bits to zero without altering stored shift state."""
        # Shift in 192 ones
        for _ in range(192):
            self.sim.clock_tick(1)

        # Disable output
        self.sim.enable = 0
        self.assertEqual(sum(self.sim.get_ctrl_out()), 0)

        # Re-enable output
        self.sim.enable = 1
        self.assertEqual(sum(self.sim.get_ctrl_out()), 192)

    def test_field_mapping_partition(self):
        """Verify field boundary partitions for 26 ASW blocks (156 bits) and 7 device blocks (36 bits)."""
        # Field bit counts:
        asw_bits = 26 * 6  # 156
        pmos_dual_bits = 6
        pmos_cm_bits = 6
        pmos_dp_bits = 4
        nmos_dp_bits = 4
        nmos_cm_bits = 8
        nmos_dual_bits = 6
        nmos_ota_bits = 2

        total_bits = (
            asw_bits
            + pmos_dual_bits
            + pmos_cm_bits
            + pmos_dp_bits
            + nmos_dp_bits
            + nmos_cm_bits
            + nmos_dual_bits
            + nmos_ota_bits
        )
        self.assertEqual(total_bits, 192)

    def test_verilog_sources_exist_and_structure(self):
        """Static verification that verilog source files exist and contain valid 192-bit ctrl_top definitions."""
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        ctrl_top_path = os.path.join(repo_root, "src/ctrl_top.v")
        project_path = os.path.join(repo_root, "src/project.v")

        self.assertTrue(os.path.exists(ctrl_top_path), f"Missing {ctrl_top_path}")
        self.assertTrue(os.path.exists(project_path), f"Missing {project_path}")

        with open(ctrl_top_path, "r") as f:
            content = f.read()

        self.assertIn("module ctrl_top", content)
        self.assertIn("[191:0] ctrl_out", content)
        self.assertIn("ctrl_block", content)

        with open(project_path, "r") as f:
            proj_content = f.read()

        self.assertIn("module tt_um_tnt_mosbius", proj_content)
        self.assertIn("wire [191:0] ctrl;", proj_content)


if __name__ == "__main__":
    unittest.main()
