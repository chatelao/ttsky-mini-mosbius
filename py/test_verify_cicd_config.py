import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from py.verify_cicd_config import (
    check_docs_workflow,
    check_gds_workflow,
    check_info_yaml,
)


class TestVerifyCICDConfig(unittest.TestCase):

    def test_check_gds_workflow_valid(self):
        valid_gds = """
name: gds
jobs:
  gds:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      - uses: TinyTapeout/tt-gds-action/custom_gds@ttihp26b
        with:
          verilog_path: src/project.v
          pdk: ihp-sg13g2
  precheck:
    needs: gds
    runs-on: ubuntu-24.04
    continue-on-error: true
    steps:
      - uses: TinyTapeout/tt-gds-action/precheck@ttihp26b
  viewer:
    needs: gds
    runs-on: ubuntu-24.04
    continue-on-error: true
    permissions:
      pages: write
      id-token: write
    steps:
      - uses: TinyTapeout/tt-gds-action/viewer@ttihp26b
"""
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            f.write(valid_gds)
            temp_path = f.name

        try:
            with patch("os.path.exists", return_value=True), patch(
                "builtins.open", unittest.mock.mock_open(read_data=valid_gds)
            ):
                self.assertTrue(check_gds_workflow())
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_check_gds_workflow_invalid(self):
        invalid_gds = """
name: gds
jobs:
  gds:
    steps:
      - uses: TinyTapeout/tt-gds-action/custom_gds@ttsky26c
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=invalid_gds)
        ):
            self.assertFalse(check_gds_workflow())

    def test_check_gds_workflow_missing_needs(self):
        missing_needs_gds = """
name: gds
jobs:
  gds:
    steps:
      - uses: TinyTapeout/tt-gds-action/custom_gds@ttihp26b
        with:
          pdk: ihp-sg13g2
  precheck:
    steps:
      - uses: TinyTapeout/tt-gds-action/precheck@ttihp26b
  viewer:
    permissions:
      pages: write
      id-token: write
    steps:
      - uses: TinyTapeout/tt-gds-action/viewer@ttihp26b
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=missing_needs_gds)
        ):
            self.assertFalse(check_gds_workflow())

    def test_check_gds_workflow_missing_submodules(self):
        missing_submodules_gds = """
name: gds
jobs:
  gds:
    runs-on: ubuntu-24.04
    steps:
      - uses: TinyTapeout/tt-gds-action/custom_gds@ttihp26b
        with:
          verilog_path: src/project.v
          pdk: ihp-sg13g2
  precheck:
    needs: gds
    runs-on: ubuntu-24.04
    continue-on-error: true
    steps:
      - uses: TinyTapeout/tt-gds-action/precheck@ttihp26b
  viewer:
    needs: gds
    runs-on: ubuntu-24.04
    continue-on-error: true
    permissions:
      pages: write
      id-token: write
    steps:
      - uses: TinyTapeout/tt-gds-action/viewer@ttihp26b
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=missing_submodules_gds)
        ):
            self.assertFalse(check_gds_workflow())

    def test_check_docs_workflow_valid(self):
        valid_docs = """
name: docs
jobs:
  docs:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      - uses: TinyTapeout/tt-gds-action/docs@ttihp26b
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=valid_docs)
        ):
            self.assertTrue(check_docs_workflow())

    def test_check_docs_workflow_invalid(self):
        invalid_docs = """
name: docs
jobs:
  docs:
    steps:
      - uses: TinyTapeout/tt-gds-action/docs@ttsky26c
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=invalid_docs)
        ):
            self.assertFalse(check_docs_workflow())

    def test_check_info_yaml_valid(self):
        valid_info = """
project:
  top_module: "tt_um_tnt_mosbius"
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=valid_info)
        ):
            self.assertTrue(check_info_yaml())

    def test_check_info_yaml_invalid(self):
        invalid_info = """
project:
  top_module: "wrong_module_name"
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=invalid_info)
        ):
            self.assertFalse(check_info_yaml())


if __name__ == "__main__":
    unittest.main()
