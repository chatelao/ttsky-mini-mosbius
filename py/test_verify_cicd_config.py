import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from py.verify_cicd_config import (
    check_def_template_config,
    check_docs_build_and_asset_config,
    check_docs_workflow,
    check_eda_toolchain_and_container_config,
    check_gds_lef_artifacts,
    check_gds_workflow,
    check_git_submodule_and_checkout_config,
    check_info_yaml,
    check_info_yaml_schema_compatibility,
    check_klayout_drc_and_geometry_config,
    check_lef_pin_and_boundary_config,
    check_pages_api_config,
    check_pages_deployment_and_oidc_config,
    check_pdk_drc_rule_compatibility,
    check_precheck_def_and_pin_config,
    check_precheck_execution_and_reporting_config,
    check_stdcell_declarations,
    check_top_module_step_config,
    check_upstream_pdk_action_tags,
    check_viewer_artifact_and_staging_config,
    check_viewer_and_docs_deployment_config,
    check_workflow_execution_summary_config,
    check_workflow_trigger_events_config,
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
          top_module: ${{ steps.top_module.outputs.TOP_MODULE }}
          gds_path: gds/${{ steps.top_module.outputs.TOP_MODULE }}.gds
          lef_path: lef/${{ steps.top_module.outputs.TOP_MODULE }}.lef
          verilog_path: src/project.v
          pdk: ihp-sg13g2
  precheck:
    needs: gds
    runs-on: ubuntu-24.04
    continue-on-error: true
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
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
          gds_path: gds/${{ steps.top_module.outputs.TOP_MODULE }}.gds
          lef_path: lef/${{ steps.top_module.outputs.TOP_MODULE }}.lef
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

    def test_check_gds_workflow_missing_gds_path(self):
        missing_gds_path = """
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
          lef_path: lef/${{ steps.top_module.outputs.TOP_MODULE }}.lef
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
            "builtins.open", unittest.mock.mock_open(read_data=missing_gds_path)
        ):
            self.assertFalse(check_gds_workflow())

    def test_check_gds_workflow_missing_lef_path(self):
        missing_lef_path = """
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
          gds_path: gds/${{ steps.top_module.outputs.TOP_MODULE }}.gds
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
            "builtins.open", unittest.mock.mock_open(read_data=missing_lef_path)
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
  uses_vapwr: true
  tiles: "3x2"
  analog_pins: 6
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

    def test_check_info_yaml_missing_fields(self):
        missing_info = """
project:
  top_module: "tt_um_tnt_mosbius"
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=missing_info)
        ):
            self.assertFalse(check_info_yaml())

    def test_check_gds_lef_artifacts_valid(self):
        with patch("os.path.exists", return_value=True), patch(
            "os.path.getsize", return_value=1024
        ), patch(
            "py.verify_cicd_config.parse_gds_layers", return_value={(189, 4), (8, 0), (30, 0), (50, 0), (67, 0), (125, 0)}
        ), patch(
            "builtins.open",
            unittest.mock.mock_open(read_data='project:\n  top_module: "tt_um_tnt_mosbius"'),
        ):
            self.assertTrue(check_gds_lef_artifacts())

    def test_check_gds_lef_artifacts_unmapped_legacy_layer(self):
        with patch("os.path.exists", return_value=True), patch(
            "os.path.getsize", return_value=1024
        ), patch(
            "py.verify_cicd_config.parse_gds_layers", return_value={(189, 4), (68, 20)}
        ), patch(
            "builtins.open",
            unittest.mock.mock_open(read_data='project:\n  top_module: "tt_um_tnt_mosbius"'),
        ):
            self.assertFalse(check_gds_lef_artifacts())

    def test_check_gds_lef_artifacts_missing_prboundary(self):
        with patch("os.path.exists", return_value=True), patch(
            "os.path.getsize", return_value=1024
        ), patch(
            "py.verify_cicd_config.parse_gds_layers", return_value={(235, 4)}
        ), patch(
            "builtins.open",
            unittest.mock.mock_open(read_data='project:\n  top_module: "tt_um_tnt_mosbius"'),
        ):
            self.assertFalse(check_gds_lef_artifacts())

    def test_check_gds_lef_artifacts_missing(self):
        with patch("os.path.exists", return_value=False):
            self.assertFalse(check_gds_lef_artifacts())

    def test_check_gds_lef_artifacts_empty(self):
        with patch("os.path.exists", return_value=True), patch(
            "os.path.getsize", return_value=0
        ), patch(
            "builtins.open",
            unittest.mock.mock_open(read_data='project:\n  top_module: "tt_um_tnt_mosbius"'),
        ):
            self.assertFalse(check_gds_lef_artifacts())

    def test_check_pages_api_config_valid(self):
        valid_gds = """
name: gds
jobs:
  viewer:
    permissions:
      pages: write
      id-token: write
    steps:
      - uses: TinyTapeout/tt-gds-action/viewer@ttihp26b
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=valid_gds)
        ):
            self.assertTrue(check_pages_api_config())

    def test_check_pages_api_config_invalid(self):
        invalid_gds = """
name: gds
jobs:
  viewer:
    steps:
      - uses: TinyTapeout/tt-gds-action/viewer@ttsky26c
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=invalid_gds)
        ):
            self.assertFalse(check_pages_api_config())

    def test_check_precheck_def_and_pin_config_valid(self):
        valid_info = """
project:
  tiles: "3x2"
  analog_pins: 2

pinout:
  ua[0]: "Ref"
  ua[1]: "Bus"
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=valid_info)
        ):
            self.assertTrue(check_precheck_def_and_pin_config())

    def test_check_precheck_def_and_pin_config_mismatch(self):
        invalid_info = """
project:
  tiles: "3x2"
  analog_pins: 6

pinout:
  ua[0]: "Ref"
  ua[1]: "Bus"
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=invalid_info)
        ):
            self.assertFalse(check_precheck_def_and_pin_config())

    def test_check_precheck_def_and_pin_config_missing_tiles(self):
        invalid_info = """
project:
  analog_pins: 0
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=invalid_info)
        ):
            self.assertFalse(check_precheck_def_and_pin_config())

    def test_check_def_template_config_valid(self):
        valid_info = """
project:
  language: "Analog"
  tiles: "3x2"
  uses_vapwr: true
"""
        valid_docs = """
## How it works
Description here.

## How to test
Testing instructions here.
"""
        def mock_open_file(filepath, mode="r"):
            if "info.yaml" in filepath:
                return unittest.mock.mock_open(read_data=valid_info)()
            else:
                return unittest.mock.mock_open(read_data=valid_docs)()

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", side_effect=mock_open_file
        ):
            self.assertTrue(check_def_template_config())

    def test_check_def_template_config_missing_language(self):
        invalid_info = """
project:
  tiles: "3x2"
  uses_vapwr: true
"""
        valid_docs = """
## How it works
## How to test
"""
        def mock_open_file(filepath, mode="r"):
            if "info.yaml" in filepath:
                return unittest.mock.mock_open(read_data=invalid_info)()
            else:
                return unittest.mock.mock_open(read_data=valid_docs)()

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", side_effect=mock_open_file
        ):
            self.assertFalse(check_def_template_config())

    def test_check_lef_pin_and_boundary_config_valid(self):
        valid_lef = """
MACRO tt_um_tnt_mosbius
  SIZE 493.120 BY 225.760 ;
  PIN clk
  END clk
  PIN ena
  END ena
  PIN rst_n
  END rst_n
  PIN ua[0]
  END ua[0]
  PIN ua[1]
  END ua[1]
  PIN ua[2]
  END ua[2]
  PIN ua[3]
  END ua[3]
  PIN ua[4]
  END ua[4]
  PIN ua[5]
  END ua[5]
END tt_um_tnt_mosbius
"""
        def mock_open_file(filepath, mode="r"):
            if "info.yaml" in filepath:
                return unittest.mock.mock_open(read_data='project:\n  top_module: "tt_um_tnt_mosbius"')()
            else:
                return unittest.mock.mock_open(read_data=valid_lef)()

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", side_effect=mock_open_file
        ):
            self.assertTrue(check_lef_pin_and_boundary_config())

    def test_check_lef_pin_and_boundary_config_missing_pin(self):
        invalid_lef = """
MACRO tt_um_tnt_mosbius
  SIZE 493.120 BY 225.760 ;
  PIN clk
  END clk
END tt_um_tnt_mosbius
"""
        def mock_open_file(filepath, mode="r"):
            if "info.yaml" in filepath:
                return unittest.mock.mock_open(read_data='project:\n  top_module: "tt_um_tnt_mosbius"')()
            else:
                return unittest.mock.mock_open(read_data=invalid_lef)()

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", side_effect=mock_open_file
        ):
            self.assertFalse(check_lef_pin_and_boundary_config())

    def test_check_top_module_step_config_valid(self):
        valid_gds = """
jobs:
  gds:
    steps:
      - name: Read top module name
        id: top_module
        run: |
          echo TOP_MODULE=`yq '.project.top_module' info.yaml` | tee $GITHUB_OUTPUT
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=valid_gds)
        ):
            self.assertTrue(check_top_module_step_config())

    def test_check_top_module_step_config_invalid(self):
        invalid_gds = """
jobs:
  gds:
    steps:
      - name: Other step
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=invalid_gds)
        ):
            self.assertFalse(check_top_module_step_config())

    def test_check_viewer_and_docs_deployment_config_valid(self):
        valid_gds = """
jobs:
  viewer:
    runs-on: ubuntu-24.04
    permissions:
      pages: write
      id-token: write
    steps:
      - uses: TinyTapeout/tt-gds-action/viewer@ttihp26b
"""
        valid_docs = """
jobs:
  docs:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      - uses: TinyTapeout/tt-gds-action/docs@ttihp26b
"""
        def mock_open_file(filepath, mode="r"):
            if "gds.yaml" in filepath:
                return unittest.mock.mock_open(read_data=valid_gds)()
            else:
                return unittest.mock.mock_open(read_data=valid_docs)()

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", side_effect=mock_open_file
        ):
            self.assertTrue(check_viewer_and_docs_deployment_config())

    def test_check_viewer_and_docs_deployment_config_invalid(self):
        invalid_gds = """
jobs:
  viewer:
    steps:
      - uses: TinyTapeout/tt-gds-action/viewer@ttsky26c
"""
        invalid_docs = """
jobs:
  docs:
    steps:
      - uses: TinyTapeout/tt-gds-action/docs@ttsky26c
"""
        def mock_open_file(filepath, mode="r"):
            if "gds.yaml" in filepath:
                return unittest.mock.mock_open(read_data=invalid_gds)()
            else:
                return unittest.mock.mock_open(read_data=invalid_docs)()

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", side_effect=mock_open_file
        ):
            self.assertFalse(check_viewer_and_docs_deployment_config())

    def test_check_docs_build_and_asset_config_valid(self):
        valid_info = "title:\nauthor:\ndescription:\npinout:\n"
        valid_docs = "## How it works\n## How to test\n"
        valid_workflow = "TinyTapeout/tt-gds-action/docs@ttihp26b"

        def mock_open_file(filepath, mode="r"):
            if "info.yaml" in filepath:
                return unittest.mock.mock_open(read_data=valid_info)()
            elif "info.md" in filepath:
                return unittest.mock.mock_open(read_data=valid_docs)()
            else:
                return unittest.mock.mock_open(read_data=valid_workflow)()

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", side_effect=mock_open_file
        ):
            self.assertTrue(check_docs_build_and_asset_config())

    def test_check_docs_build_and_asset_config_invalid(self):
        invalid_info = "title:\n"
        invalid_docs = "Missing sections\n"
        invalid_workflow = "TinyTapeout/tt-gds-action/docs@ttsky26c"

        def mock_open_file(filepath, mode="r"):
            if "info.yaml" in filepath:
                return unittest.mock.mock_open(read_data=invalid_info)()
            elif "info.md" in filepath:
                return unittest.mock.mock_open(read_data=invalid_docs)()
            else:
                return unittest.mock.mock_open(read_data=invalid_workflow)()

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", side_effect=mock_open_file
        ):
            self.assertFalse(check_docs_build_and_asset_config())

    def test_check_lef_pin_and_boundary_config_invalid_size(self):
        invalid_lef = """
MACRO tt_um_tnt_mosbius
  SIZE 0.0 BY 0.0 ;
  PIN clk
  END clk
  PIN ena
  END ena
  PIN rst_n
  END rst_n
  PIN ua[0]
  END ua[0]
  PIN ua[1]
  END ua[1]
  PIN ua[2]
  END ua[2]
  PIN ua[3]
  END ua[3]
  PIN ua[4]
  END ua[4]
  PIN ua[5]
  END ua[5]
END tt_um_tnt_mosbius
"""
        def mock_open_file(filepath, mode="r"):
            if "info.yaml" in filepath:
                return unittest.mock.mock_open(read_data='project:\n  top_module: "tt_um_tnt_mosbius"')()
            else:
                return unittest.mock.mock_open(read_data=invalid_lef)()

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", side_effect=mock_open_file
        ):
            self.assertFalse(check_lef_pin_and_boundary_config())

    def test_check_viewer_artifact_and_staging_config_valid(self):
        valid_gds_wf = """
jobs:
  viewer:
    needs: gds
    steps:
      - uses: TinyTapeout/tt-gds-action/viewer@ttihp26b
"""
        def mock_open_file(filepath, mode="r"):
            if "info.yaml" in filepath:
                return unittest.mock.mock_open(read_data='project:\n  top_module: "tt_um_tnt_mosbius"')()
            else:
                return unittest.mock.mock_open(read_data=valid_gds_wf)()

        with patch("os.path.exists", return_value=True), patch(
            "os.path.getsize", return_value=1024
        ), patch(
            "builtins.open", side_effect=mock_open_file
        ):
            self.assertTrue(check_viewer_artifact_and_staging_config())

    def test_check_viewer_artifact_and_staging_config_missing_viewer_job(self):
        invalid_gds_wf = """
jobs:
  gds:
    steps: []
"""
        def mock_open_file(filepath, mode="r"):
            if "info.yaml" in filepath:
                return unittest.mock.mock_open(read_data='project:\n  top_module: "tt_um_tnt_mosbius"')()
            else:
                return unittest.mock.mock_open(read_data=invalid_gds_wf)()

        with patch("os.path.exists", return_value=True), patch(
            "os.path.getsize", return_value=1024
        ), patch(
            "builtins.open", side_effect=mock_open_file
        ):
            self.assertFalse(check_viewer_artifact_and_staging_config())

    def test_check_pages_deployment_and_oidc_config_valid(self):
        valid_gds_wf = """
jobs:
  viewer:
    runs-on: ubuntu-24.04
    permissions:
      pages: write
      id-token: write
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=valid_gds_wf)
        ):
            self.assertTrue(check_pages_deployment_and_oidc_config())

    def test_check_pages_deployment_and_oidc_config_missing_permissions(self):
        invalid_gds_wf = """
jobs:
  viewer:
    runs-on: ubuntu-24.04
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=invalid_gds_wf)
        ):
            self.assertFalse(check_pages_deployment_and_oidc_config())

    def test_check_klayout_drc_and_geometry_config_valid(self):
        valid_drc = """
drc euclidean on
drc style "drc(full)"
drc check
"""
        valid_gds_wf = """
jobs:
  precheck:
    steps:
      - uses: TinyTapeout/tt-gds-action/precheck@ttihp26b
"""
        def mock_open_file(filepath, mode="r"):
            if "magic_drc.tcl" in filepath:
                return unittest.mock.mock_open(read_data=valid_drc)()
            else:
                return unittest.mock.mock_open(read_data=valid_gds_wf)()

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", side_effect=mock_open_file
        ):
            self.assertTrue(check_klayout_drc_and_geometry_config())

    def test_check_klayout_drc_and_geometry_config_invalid(self):
        invalid_drc = """
# Empty DRC script
"""
        invalid_gds_wf = """
jobs:
  precheck:
    steps:
      - uses: TinyTapeout/tt-gds-action/precheck@ttsky26c
"""
        def mock_open_file(filepath, mode="r"):
            if "magic_drc.tcl" in filepath:
                return unittest.mock.mock_open(read_data=invalid_drc)()
            else:
                return unittest.mock.mock_open(read_data=invalid_gds_wf)()

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", side_effect=mock_open_file
        ):
            self.assertFalse(check_klayout_drc_and_geometry_config())

    def test_check_eda_toolchain_and_container_config_valid(self):
        valid_gds = """
jobs:
  gds:
    runs-on: ubuntu-24.04
    steps:
      - uses: TinyTapeout/tt-gds-action/custom_gds@ttihp26b
        with:
          pdk: ihp-sg13g2
          verilog_path: src/project.v
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=valid_gds)
        ):
            self.assertTrue(check_eda_toolchain_and_container_config())

    def test_check_eda_toolchain_and_container_config_invalid(self):
        invalid_gds = """
jobs:
  gds:
    runs-on: ubuntu-22.04
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=invalid_gds)
        ):
            self.assertFalse(check_eda_toolchain_and_container_config())

    def test_check_precheck_execution_and_reporting_config_valid(self):
        valid_gds = """
jobs:
  precheck:
    needs: gds
    continue-on-error: true
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      - uses: TinyTapeout/tt-gds-action/precheck@ttihp26b
  viewer:
    steps: []
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=valid_gds)
        ):
            self.assertTrue(check_precheck_execution_and_reporting_config())

    def test_check_precheck_execution_and_reporting_config_invalid(self):
        invalid_gds = """
jobs:
  precheck:
    steps: []
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=invalid_gds)
        ):
            self.assertFalse(check_precheck_execution_and_reporting_config())

    def test_check_workflow_execution_summary_config_valid(self):
        valid_gds = """
jobs:
  gds:
    steps:
      - uses: TinyTapeout/tt-gds-action/custom_gds@ttihp26b
  precheck:
    steps:
      - uses: TinyTapeout/tt-gds-action/precheck@ttihp26b
  viewer:
    steps:
      - uses: TinyTapeout/tt-gds-action/viewer@ttihp26b
"""
        valid_docs = """
jobs:
  docs:
    steps:
      - uses: TinyTapeout/tt-gds-action/docs@ttihp26b
"""
        def mock_open_file(filepath, mode="r"):
            if "gds.yaml" in filepath:
                return unittest.mock.mock_open(read_data=valid_gds)()
            else:
                return unittest.mock.mock_open(read_data=valid_docs)()

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", side_effect=mock_open_file
        ):
            self.assertTrue(check_workflow_execution_summary_config())

    def test_check_workflow_execution_summary_config_invalid(self):
        invalid_gds = """
jobs:
  gds:
    steps: []
"""
        invalid_docs = """
jobs:
  docs:
    steps: []
"""
        def mock_open_file(filepath, mode="r"):
            if "gds.yaml" in filepath:
                return unittest.mock.mock_open(read_data=invalid_gds)()
            else:
                return unittest.mock.mock_open(read_data=invalid_docs)()

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", side_effect=mock_open_file
        ):
            self.assertFalse(check_workflow_execution_summary_config())

    def test_check_workflow_trigger_events_config_valid(self):
        valid_wf = """
on:
  push:
  pull_request:
  workflow_dispatch:
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=valid_wf)
        ):
            self.assertTrue(check_workflow_trigger_events_config())

    def test_check_workflow_trigger_events_config_invalid(self):
        invalid_wf = """
on:
  push:
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=invalid_wf)
        ):
            self.assertFalse(check_workflow_trigger_events_config())

    def test_check_git_submodule_and_checkout_config_valid(self):
        valid_wf = """
steps:
  - uses: actions/checkout@v4
    with:
      submodules: recursive
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=valid_wf)
        ):
            self.assertTrue(check_git_submodule_and_checkout_config())

    def test_check_git_submodule_and_checkout_config_invalid(self):
        invalid_wf = """
steps:
  - uses: actions/checkout@v3
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=invalid_wf)
        ):
            self.assertFalse(check_git_submodule_and_checkout_config())

    def test_check_stdcell_declarations_valid(self):
        valid_stdcells = "module sg13g2_buf_2 (output wire X); endmodule"
        valid_rtl = "module ctrl_block; sg13g2_buf_4 buf_I(); endmodule"

        def mock_open_file(filepath, mode="r"):
            if "stdcells.v" in filepath:
                return unittest.mock.mock_open(read_data=valid_stdcells)()
            else:
                return unittest.mock.mock_open(read_data=valid_rtl)()

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", side_effect=mock_open_file
        ):
            self.assertTrue(check_stdcell_declarations())

    def test_check_stdcell_declarations_invalid(self):
        invalid_stdcells = "module sky130_fd_sc_hd__clkbuf_4; endmodule"

        def mock_open_file(filepath, mode="r"):
            return unittest.mock.mock_open(read_data=invalid_stdcells)()

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", side_effect=mock_open_file
        ):
            self.assertFalse(check_stdcell_declarations())

    def test_check_common_py_stdcells(self):
        valid_common = "TAP = Cell('sg13g2_tap_1', 1)"
        invalid_common = "TAP = Cell('sky130_fd_sc_hd__tapvpwrvgnd_1', 1)"

        def mock_open_file_valid(filepath, mode="r"):
            if "stdcells.v" in filepath:
                return unittest.mock.mock_open(read_data="sg13g2_")()
            elif "common.py" in filepath:
                return unittest.mock.mock_open(read_data=valid_common)()
            else:
                return unittest.mock.mock_open(read_data="valid")()

        def mock_open_file_invalid(filepath, mode="r"):
            if "common.py" in filepath:
                return unittest.mock.mock_open(read_data=invalid_common)()
            elif "stdcells.v" in filepath:
                return unittest.mock.mock_open(read_data="sg13g2_")()
            else:
                return unittest.mock.mock_open(read_data="valid")()

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", side_effect=mock_open_file_valid
        ):
            self.assertTrue(check_stdcell_declarations())

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", side_effect=mock_open_file_invalid
        ):
            self.assertFalse(check_stdcell_declarations())

    def test_check_upstream_pdk_action_tags_valid(self):
        valid_wf = "TinyTapeout/tt-gds-action/custom_gds@ttihp26b"
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=valid_wf)
        ):
            self.assertTrue(check_upstream_pdk_action_tags())

    def test_check_upstream_pdk_action_tags_invalid(self):
        invalid_wf = "TinyTapeout/tt-gds-action/custom_gds@ttsky26c"
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=invalid_wf)
        ):
            self.assertFalse(check_upstream_pdk_action_tags())

    def test_check_info_yaml_schema_compatibility_valid(self):
        valid_info = """
project:
  top_module: "tt_um_tnt_mosbius"
  language: "Analog"
  tiles: "3x2"
  uses_vapwr: true
  analog_pins: 6

pinout:
  ua[0]: "Ref"
  ua[1]: "Bus"
  ua[2]: "In"
  ua[3]: "Out"
  ua[4]: "Bias"
  ua[5]: "Sense"
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=valid_info)
        ):
            self.assertTrue(check_info_yaml_schema_compatibility())

    def test_check_info_yaml_schema_compatibility_invalid(self):
        invalid_info = """
project:
  top_module: "wrong_module"
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=invalid_info)
        ):
            self.assertFalse(check_info_yaml_schema_compatibility())

    def test_check_pdk_drc_rule_compatibility_valid(self):
        valid_drc = """
drc euclidean on
drc style "drc(full)"
drc check
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=valid_drc)
        ):
            self.assertTrue(check_pdk_drc_rule_compatibility())

    def test_check_pdk_drc_rule_compatibility_invalid(self):
        invalid_drc = """
# Missing DRC directives
"""
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", unittest.mock.mock_open(read_data=invalid_drc)
        ):
            self.assertFalse(check_pdk_drc_rule_compatibility())


if __name__ == "__main__":
    unittest.main()
