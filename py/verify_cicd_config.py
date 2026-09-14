#!/usr/bin/env python3
"""
Static verification script for Mini-MOSbius CI/CD configuration files.
Verifies action tags, PDK parameter, permissions, and info.yaml module settings.
"""

import os
import re
import sys


def check_gds_workflow(repo_root="."):
    filepath = os.path.join(repo_root, ".github/workflows/gds.yaml")
    if not os.path.exists(filepath):
        print(f"ERROR: {filepath} does not exist.")
        return False

    with open(filepath, "r") as f:
        content = f.read()

    errors = []

    # Check action tags
    expected_actions = [
        "TinyTapeout/tt-gds-action/custom_gds@ttihp26b",
        "TinyTapeout/tt-gds-action/precheck@ttihp26b",
        "TinyTapeout/tt-gds-action/viewer@ttihp26b",
    ]
    for action in expected_actions:
        if action not in content:
            errors.append(f"Missing expected action reference: {action}")

    # Check for legacy action tags
    if "ttsky26c" in content:
        errors.append("Found legacy tag 'ttsky26c' in gds.yaml")

    # Check PDK parameter
    if "pdk: ihp-sg13g2" not in content:
        errors.append("Missing 'pdk: ihp-sg13g2' parameter in gds.yaml")

    # Check permissions in viewer job
    if "pages: write" not in content or "id-token: write" not in content:
        errors.append("Missing required Pages/OIDC write permissions in gds.yaml")

    # Check job dependencies
    if "needs: gds" not in content:
        errors.append("Missing required job dependency 'needs: gds' in gds.yaml")

    # Check checkout submodules configuration
    if "submodules: recursive" not in content:
        errors.append("Missing 'submodules: recursive' setting in gds.yaml")

    # Check runner configuration
    if "runs-on: ubuntu-24.04" not in content:
        errors.append("Missing 'runs-on: ubuntu-24.04' runner configuration in gds.yaml")

    # Check continue-on-error setting
    if "continue-on-error: true" not in content:
        errors.append("Missing 'continue-on-error: true' setting in gds.yaml")

    # Check verilog_path parameter
    if "verilog_path: src/project.v" not in content:
        errors.append("Missing 'verilog_path: src/project.v' parameter in gds.yaml")

    # Check gds_path and lef_path parameters
    if "gds_path: gds/${{ steps.top_module.outputs.TOP_MODULE }}.gds" not in content:
        errors.append("Missing expected 'gds_path' parameter in gds.yaml")

    if "lef_path: lef/${{ steps.top_module.outputs.TOP_MODULE }}.lef" not in content:
        errors.append("Missing expected 'lef_path' parameter in gds.yaml")

    if errors:
        print(f"FAILED {filepath}:")
        for err in errors:
            print(f"  - {err}")
        return False

    print(f"PASSED {filepath}")
    return True


def check_docs_workflow(repo_root="."):
    filepath = os.path.join(repo_root, ".github/workflows/docs.yaml")
    if not os.path.exists(filepath):
        print(f"ERROR: {filepath} does not exist.")
        return False

    with open(filepath, "r") as f:
        content = f.read()

    errors = []

    expected_action = "TinyTapeout/tt-gds-action/docs@ttihp26b"
    if expected_action not in content:
        errors.append(f"Missing expected action reference: {expected_action}")

    if "ttsky26c" in content:
        errors.append("Found legacy tag 'ttsky26c' in docs.yaml")

    # Check checkout submodules configuration
    if "submodules: recursive" not in content:
        errors.append("Missing 'submodules: recursive' setting in docs.yaml")

    # Check runner configuration
    if "runs-on: ubuntu-24.04" not in content:
        errors.append("Missing 'runs-on: ubuntu-24.04' runner configuration in docs.yaml")

    if errors:
        print(f"FAILED {filepath}:")
        for err in errors:
            print(f"  - {err}")
        return False

    print(f"PASSED {filepath}")
    return True


def check_info_yaml(repo_root="."):
    filepath = os.path.join(repo_root, "info.yaml")
    if not os.path.exists(filepath):
        print(f"ERROR: {filepath} does not exist.")
        return False

    with open(filepath, "r") as f:
        content = f.read()

    errors = []
    match = re.search(r"top_module:\s*[\"']?([a-zA-Z0-9_]+)[\"']?", content)

    if not match:
        errors.append("Could not find top_module in info.yaml")
    else:
        top_module = match.group(1)
        if top_module != "tt_um_tnt_mosbius":
            errors.append(
                f"Expected top_module 'tt_um_tnt_mosbius', got '{top_module}'"
            )

    if not re.search(r"uses_vapwr:\s*true", content):
        errors.append("Missing or invalid 'uses_vapwr: true' in info.yaml")

    if not re.search(r"analog_pins:\s*\d+", content):
        errors.append("Missing or invalid 'analog_pins' in info.yaml")

    if not re.search(r"tiles:\s*[\"']?\d+x\d+[\"']?", content):
        errors.append("Missing or invalid 'tiles' parameter in info.yaml")

    if errors:
        print(f"FAILED {filepath}:")
        for err in errors:
            print(f"  - {err}")
        return False

    print(f"PASSED {filepath} (top_module={match.group(1)})")
    return True


def check_gds_lef_artifacts(repo_root="."):
    info_path = os.path.join(repo_root, "info.yaml")
    top_module = "tt_um_tnt_mosbius"
    if os.path.exists(info_path):
        with open(info_path, "r") as f:
            content = f.read()
            match = re.search(r"top_module:\s*[\"']?([a-zA-Z0-9_]+)[\"']?", content)
            if match:
                top_module = match.group(1)

    errors = []
    gds_file = os.path.join(repo_root, "gds", f"{top_module}.gds")
    lef_file = os.path.join(repo_root, "lef", f"{top_module}.lef")

    if not os.path.exists(gds_file):
        errors.append(f"Missing GDS artifact file: {gds_file}")
    elif os.path.getsize(gds_file) == 0:
        errors.append(f"GDS artifact file is empty: {gds_file}")

    if not os.path.exists(lef_file):
        errors.append(f"Missing LEF artifact file: {lef_file}")
    elif os.path.getsize(lef_file) == 0:
        errors.append(f"LEF artifact file is empty: {lef_file}")

    if errors:
        print("FAILED GDS/LEF local artifact check:")
        for err in errors:
            print(f"  - {err}")
        return False

    print(f"PASSED GDS/LEF local artifact check for {top_module}")
    return True


def check_pages_api_config(repo_root="."):
    filepath = os.path.join(repo_root, ".github/workflows/gds.yaml")
    if not os.path.exists(filepath):
        print(f"ERROR: {filepath} does not exist.")
        return False

    with open(filepath, "r") as f:
        content = f.read()

    errors = []

    if "viewer:" not in content:
        errors.append("Missing 'viewer' job in gds.yaml for Pages deployment API")

    if "pages: write" not in content:
        errors.append("Missing 'pages: write' permission for GitHub Pages deployment API")

    if "id-token: write" not in content:
        errors.append("Missing 'id-token: write' permission for OIDC authentication")

    if "TinyTapeout/tt-gds-action/viewer@ttihp26b" not in content:
        errors.append("Missing expected 'viewer@ttihp26b' action reference for Pages deployment")

    if errors:
        print(f"FAILED Pages API config check in {filepath}:")
        for err in errors:
            print(f"  - {err}")
        return False

    print(f"PASSED Pages API config check in {filepath}")
    return True


def check_precheck_def_and_pin_config(repo_root="."):
    info_path = os.path.join(repo_root, "info.yaml")
    if not os.path.exists(info_path):
        print(f"ERROR: {info_path} does not exist.")
        return False

    with open(info_path, "r") as f:
        content = f.read()

    errors = []

    tile_match = re.search(r"tiles:\s*[\"']?(\d+x\d+)[\"']?", content)
    if tile_match:
        tiles = tile_match.group(1)
        if not re.match(r"^\d+x\d+$", tiles):
            errors.append(f"Invalid tile specification: '{tiles}'")
    else:
        errors.append("Missing 'tiles' specification in info.yaml")

    analog_count_match = re.search(r"analog_pins:\s*(\d+)", content)
    if analog_count_match:
        num_analog_pins = int(analog_count_match.group(1))
        ua_pins = re.findall(r"ua\[(\d+)\]:\s*[\"']([^\"']*)[\"']", content)
        non_empty_ua = [p for p in ua_pins if p[1].strip() != ""]
        if len(non_empty_ua) != num_analog_pins:
            errors.append(
                f"Mismatch: 'analog_pins' count is {num_analog_pins}, but found {len(non_empty_ua)} non-empty ua[...] pin definitions in info.yaml"
            )
    else:
        errors.append("Missing 'analog_pins' count in info.yaml")

    if errors:
        print(f"FAILED precheck DEF/pin config check in {info_path}:")
        for err in errors:
            print(f"  - {err}")
        return False

    print(f"PASSED precheck DEF/pin config check in {info_path}")
    return True


def check_def_template_config(repo_root="."):
    info_path = os.path.join(repo_root, "info.yaml")
    docs_info_path = os.path.join(repo_root, "docs/info.md")

    if not os.path.exists(info_path):
        print(f"ERROR: {info_path} does not exist.")
        return False

    errors = []

    with open(info_path, "r") as f:
        content = f.read()

    if not re.search(r"language:\s*[\"']?Analog[\"']?", content, re.IGNORECASE):
        errors.append("Missing or invalid 'language: Analog' in info.yaml")

    tile_match = re.search(r"tiles:\s*[\"']?(3x2)[\"']?", content)
    if not tile_match:
        errors.append("Expected 'tiles: 3x2' for tt_analog_3x2_3v3.def template resolution in info.yaml")

    if not re.search(r"uses_vapwr:\s*true", content):
        errors.append("Expected 'uses_vapwr: true' for 3.3V analog power domain in info.yaml")

    if not os.path.exists(docs_info_path):
        errors.append(f"Missing documentation file: {docs_info_path}")
    else:
        with open(docs_info_path, "r") as f:
            docs_content = f.read()
        if "## How it works" not in docs_content:
            errors.append("Missing '## How it works' section in docs/info.md")
        if "## How to test" not in docs_content:
            errors.append("Missing '## How to test' section in docs/info.md")

    if errors:
        print(f"FAILED DEF template and docs config check in {info_path}:")
        for err in errors:
            print(f"  - {err}")
        return False

    print(f"PASSED DEF template and docs config check in {info_path}")
    return True


def check_viewer_and_docs_deployment_config(repo_root="."):
    gds_path = os.path.join(repo_root, ".github/workflows/gds.yaml")
    docs_path = os.path.join(repo_root, ".github/workflows/docs.yaml")

    errors = []

    if not os.path.exists(gds_path):
        errors.append(f"Missing file: {gds_path}")
    else:
        with open(gds_path, "r") as f:
            gds_content = f.read()

        if "viewer:" not in gds_content:
            errors.append("Missing 'viewer' job definition in gds.yaml")
        if "TinyTapeout/tt-gds-action/viewer@ttihp26b" not in gds_content:
            errors.append("Missing 'viewer@ttihp26b' action tag in gds.yaml")
        if "pages: write" not in gds_content or "id-token: write" not in gds_content:
            errors.append("Missing required Pages and OIDC permissions in viewer job in gds.yaml")
        if "runs-on: ubuntu-24.04" not in gds_content:
            errors.append("Missing 'runs-on: ubuntu-24.04' runner configuration in gds.yaml")

    if not os.path.exists(docs_path):
        errors.append(f"Missing file: {docs_path}")
    else:
        with open(docs_path, "r") as f:
            docs_content = f.read()

        if "docs:" not in docs_content:
            errors.append("Missing 'docs' job definition in docs.yaml")
        if "TinyTapeout/tt-gds-action/docs@ttihp26b" not in docs_content:
            errors.append("Missing 'docs@ttihp26b' action tag in docs.yaml")
        if "submodules: recursive" not in docs_content:
            errors.append("Missing 'submodules: recursive' setting in docs.yaml")
        if "runs-on: ubuntu-24.04" not in docs_content:
            errors.append("Missing 'runs-on: ubuntu-24.04' runner configuration in docs.yaml")

    if errors:
        print("FAILED viewer and docs deployment config check:")
        for err in errors:
            print(f"  - {err}")
        return False

    print("PASSED viewer and docs deployment config check")
    return True


def check_docs_build_and_asset_config(repo_root="."):
    info_path = os.path.join(repo_root, "info.yaml")
    docs_info_path = os.path.join(repo_root, "docs/info.md")
    docs_workflow_path = os.path.join(repo_root, ".github/workflows/docs.yaml")

    errors = []

    if not os.path.exists(info_path):
        errors.append(f"Missing file: {info_path}")
    else:
        with open(info_path, "r") as f:
            info_content = f.read()
        for field in ["title:", "author:", "description:", "pinout:"]:
            if field not in info_content:
                errors.append(f"Missing required metadata field '{field}' in info.yaml")

    if not os.path.exists(docs_info_path):
        errors.append(f"Missing file: {docs_info_path}")
    else:
        with open(docs_info_path, "r") as f:
            docs_content = f.read()
        if "## How it works" not in docs_content:
            errors.append("Missing '## How it works' section in docs/info.md")
        if "## How to test" not in docs_content:
            errors.append("Missing '## How to test' section in docs/info.md")

    if not os.path.exists(docs_workflow_path):
        errors.append(f"Missing file: {docs_workflow_path}")
    else:
        with open(docs_workflow_path, "r") as f:
            workflow_content = f.read()
        if "TinyTapeout/tt-gds-action/docs@ttihp26b" not in workflow_content:
            errors.append("Missing action tag 'TinyTapeout/tt-gds-action/docs@ttihp26b' in docs.yaml")

    if errors:
        print("FAILED docs build and asset config check:")
        for err in errors:
            print(f"  - {err}")
        return False

    print("PASSED docs build and asset config check")
    return True


def check_top_module_step_config(repo_root="."):
    filepath = os.path.join(repo_root, ".github/workflows/gds.yaml")
    if not os.path.exists(filepath):
        print(f"ERROR: {filepath} does not exist.")
        return False

    with open(filepath, "r") as f:
        content = f.read()

    errors = []

    if "name: Read top module name" not in content:
        errors.append("Missing 'Read top module name' step in gds.yaml")

    if "yq '.project.top_module' info.yaml" not in content and 'yq ".project.top_module" info.yaml' not in content:
        errors.append("Missing yq command extracting top_module in gds.yaml")

    if "TOP_MODULE=" not in content:
        errors.append("Missing TOP_MODULE output assignment in gds.yaml")

    if errors:
        print(f"FAILED top module step config check in {filepath}:")
        for err in errors:
            print(f"  - {err}")
        return False

    print(f"PASSED top module step config check in {filepath}")
    return True


def check_lef_pin_and_boundary_config(repo_root="."):
    info_path = os.path.join(repo_root, "info.yaml")
    top_module = "tt_um_tnt_mosbius"
    if os.path.exists(info_path):
        with open(info_path, "r") as f:
            content = f.read()
            match = re.search(r"top_module:\s*[\"']?([a-zA-Z0-9_]+)[\"']?", content)
            if match:
                top_module = match.group(1)

    lef_path = os.path.join(repo_root, "lef", f"{top_module}.lef")
    if not os.path.exists(lef_path):
        print(f"ERROR: LEF file does not exist: {lef_path}")
        return False

    with open(lef_path, "r") as f:
        lef_content = f.read()

    errors = []

    macro_match = re.search(r"MACRO\s+" + re.escape(top_module), lef_content)
    if not macro_match:
        errors.append(f"LEF missing MACRO declaration for top_module '{top_module}'")

    size_match = re.search(r"SIZE\s+([\d\.]+)\s+BY\s+([\d\.]+)", lef_content)
    if size_match:
        width = float(size_match.group(1))
        height = float(size_match.group(2))
        if width <= 0 or height <= 0:
            errors.append(f"Invalid MACRO SIZE in LEF: width={width}, height={height}")
    else:
        errors.append("Missing MACRO SIZE definition in LEF")

    required_pins = ["ua[0]", "ua[1]", "ua[2]", "ua[3]", "ua[4]", "ua[5]", "clk", "ena", "rst_n"]
    for pin in required_pins:
        pin_pattern = r"PIN\s+" + re.escape(pin) + r"(?:\s|;|$)"
        if not re.search(pin_pattern, lef_content):
            errors.append(f"Missing PIN declaration for '{pin}' in LEF")

    if errors:
        print(f"FAILED LEF pin and boundary config check in {lef_path}:")
        for err in errors:
            print(f"  - {err}")
        return False

    print(f"PASSED LEF pin and boundary config check for {top_module}")
    return True


def check_viewer_artifact_and_staging_config(repo_root="."):
    gds_workflow_path = os.path.join(repo_root, ".github/workflows/gds.yaml")
    if not os.path.exists(gds_workflow_path):
        print(f"ERROR: {gds_workflow_path} does not exist.")
        return False

    with open(gds_workflow_path, "r") as f:
        content = f.read()

    errors = []

    if "viewer:" not in content:
        errors.append("Missing 'viewer' job in gds.yaml")
    if "needs: gds" not in content:
        errors.append("Missing 'needs: gds' dependency in viewer job in gds.yaml")
    if "TinyTapeout/tt-gds-action/viewer@ttihp26b" not in content:
        errors.append("Missing expected 'viewer@ttihp26b' action tag in gds.yaml")

    info_path = os.path.join(repo_root, "info.yaml")
    top_module = "tt_um_tnt_mosbius"
    if os.path.exists(info_path):
        with open(info_path, "r") as f:
            info_content = f.read()
            match = re.search(r"top_module:\s*[\"']?([a-zA-Z0-9_]+)[\"']?", info_content)
            if match:
                top_module = match.group(1)

    gds_file = os.path.join(repo_root, "gds", f"{top_module}.gds")
    if not os.path.exists(gds_file) or os.path.getsize(gds_file) == 0:
        errors.append(f"GDS artifact for viewer staging missing or empty: {gds_file}")

    if errors:
        print(f"FAILED viewer artifact and staging config check:")
        for err in errors:
            print(f"  - {err}")
        return False

    print(f"PASSED viewer artifact and staging config check")
    return True


def check_pages_deployment_and_oidc_config(repo_root="."):
    gds_workflow_path = os.path.join(repo_root, ".github/workflows/gds.yaml")
    if not os.path.exists(gds_workflow_path):
        print(f"ERROR: {gds_workflow_path} does not exist.")
        return False

    with open(gds_workflow_path, "r") as f:
        content = f.read()

    errors = []

    if "permissions:" not in content:
        errors.append("Missing 'permissions:' block in gds.yaml")
    if "pages: write" not in content:
        errors.append("Missing 'pages: write' permission scope in gds.yaml")
    if "id-token: write" not in content:
        errors.append("Missing 'id-token: write' OIDC permission scope in gds.yaml")
    if "runs-on: ubuntu-24.04" not in content:
        errors.append("Missing 'runs-on: ubuntu-24.04' runner configuration in gds.yaml")

    if errors:
        print(f"FAILED Pages deployment and OIDC config check:")
        for err in errors:
            print(f"  - {err}")
        return False

    print(f"PASSED Pages deployment and OIDC config check")
    return True


def check_klayout_drc_and_geometry_config(repo_root="."):
    drc_script_path = os.path.join(repo_root, "tcl/magic_drc.tcl")
    gds_workflow_path = os.path.join(repo_root, ".github/workflows/gds.yaml")

    errors = []

    if not os.path.exists(drc_script_path):
        errors.append(f"Missing DRC script file: {drc_script_path}")
    else:
        with open(drc_script_path, "r") as f:
            drc_content = f.read()
        if "drc euclidean on" not in drc_content:
            errors.append("Missing 'drc euclidean on' setting in tcl/magic_drc.tcl")
        if 'drc style "drc(full)"' not in drc_content and "drc style drc(full)" not in drc_content:
            errors.append("Missing 'drc style \"drc(full)\"' setting in tcl/magic_drc.tcl")
        if "drc check" not in drc_content:
            errors.append("Missing 'drc check' command in tcl/magic_drc.tcl")

    if not os.path.exists(gds_workflow_path):
        errors.append(f"Missing workflow file: {gds_workflow_path}")
    else:
        with open(gds_workflow_path, "r") as f:
            gds_content = f.read()
        if "TinyTapeout/tt-gds-action/precheck@ttihp26b" not in gds_content:
            errors.append("Missing 'precheck@ttihp26b' action in gds.yaml for DRC and geometry checks")

    if errors:
        print("FAILED DRC and geometry config check:")
        for err in errors:
            print(f"  - {err}")
        return False

    print("PASSED DRC and geometry config check")
    return True


def check_eda_toolchain_and_container_config(repo_root="."):
    gds_workflow_path = os.path.join(repo_root, ".github/workflows/gds.yaml")
    errors = []

    if not os.path.exists(gds_workflow_path):
        errors.append(f"Missing workflow file: {gds_workflow_path}")
    else:
        with open(gds_workflow_path, "r") as f:
            content = f.read()

        if "TinyTapeout/tt-gds-action/custom_gds@ttihp26b" not in content:
            errors.append("Missing 'custom_gds@ttihp26b' action step in gds.yaml")
        if "pdk: ihp-sg13g2" not in content:
            errors.append("Missing 'pdk: ihp-sg13g2' parameter in gds.yaml")
        if "runs-on: ubuntu-24.04" not in content:
            errors.append("Missing 'runs-on: ubuntu-24.04' runner configuration in gds.yaml")
        if "verilog_path: src/project.v" not in content:
            errors.append("Missing 'verilog_path: src/project.v' parameter in gds.yaml")

    if errors:
        print("FAILED EDA toolchain and container config check:")
        for err in errors:
            print(f"  - {err}")
        return False

    print("PASSED EDA toolchain and container config check")
    return True


def check_precheck_execution_and_reporting_config(repo_root="."):
    gds_workflow_path = os.path.join(repo_root, ".github/workflows/gds.yaml")
    errors = []

    if not os.path.exists(gds_workflow_path):
        errors.append(f"Missing workflow file: {gds_workflow_path}")
    else:
        with open(gds_workflow_path, "r") as f:
            content = f.read()

        if "precheck:" not in content:
            errors.append("Missing 'precheck' job definition in gds.yaml")
        if "needs: gds" not in content:
            errors.append("Missing 'needs: gds' dependency in precheck job in gds.yaml")
        if "TinyTapeout/tt-gds-action/precheck@ttihp26b" not in content:
            errors.append("Missing 'precheck@ttihp26b' action step in gds.yaml")
        if "continue-on-error: true" not in content:
            errors.append("Missing 'continue-on-error: true' setting in precheck job in gds.yaml")

    if errors:
        print("FAILED precheck execution and reporting config check:")
        for err in errors:
            print(f"  - {err}")
        return False

    print("PASSED precheck execution and reporting config check")
    return True


def check_workflow_execution_summary_config(repo_root="."):
    gds_path = os.path.join(repo_root, ".github/workflows/gds.yaml")
    docs_path = os.path.join(repo_root, ".github/workflows/docs.yaml")
    errors = []

    if not os.path.exists(gds_path):
        errors.append(f"Missing file: {gds_path}")
    else:
        with open(gds_path, "r") as f:
            gds_content = f.read()
        for action in ["custom_gds@ttihp26b", "precheck@ttihp26b", "viewer@ttihp26b"]:
            if action not in gds_content:
                errors.append(f"Missing action reference '{action}' in gds.yaml execution flow")

    if not os.path.exists(docs_path):
        errors.append(f"Missing file: {docs_path}")
    else:
        with open(docs_path, "r") as f:
            docs_content = f.read()
        if "docs@ttihp26b" not in docs_content:
            errors.append("Missing action reference 'docs@ttihp26b' in docs.yaml execution flow")

    if errors:
        print("FAILED workflow execution summary config check:")
        for err in errors:
            print(f"  - {err}")
        return False

    print("PASSED workflow execution summary config check")
    return True


def check_workflow_trigger_events_config(repo_root="."):
    gds_path = os.path.join(repo_root, ".github/workflows/gds.yaml")
    docs_path = os.path.join(repo_root, ".github/workflows/docs.yaml")
    errors = []

    required_triggers = ["push:", "pull_request:", "workflow_dispatch:"]

    for path in [gds_path, docs_path]:
        filename = os.path.basename(path)
        if not os.path.exists(path):
            errors.append(f"Missing workflow file: {path}")
        else:
            with open(path, "r") as f:
                content = f.read()
            for trigger in required_triggers:
                if trigger not in content:
                    errors.append(f"Missing '{trigger[:-1]}' trigger event in {filename}")

    if errors:
        print("FAILED workflow trigger events config check:")
        for err in errors:
            print(f"  - {err}")
        return False

    print("PASSED workflow trigger events config check")
    return True


def check_git_submodule_and_checkout_config(repo_root="."):
    gds_path = os.path.join(repo_root, ".github/workflows/gds.yaml")
    docs_path = os.path.join(repo_root, ".github/workflows/docs.yaml")
    errors = []

    for path in [gds_path, docs_path]:
        filename = os.path.basename(path)
        if not os.path.exists(path):
            errors.append(f"Missing workflow file: {path}")
        else:
            with open(path, "r") as f:
                content = f.read()
            if "actions/checkout@v4" not in content:
                errors.append(f"Missing 'actions/checkout@v4' step in {filename}")
            if "submodules: recursive" not in content:
                errors.append(f"Missing 'submodules: recursive' setting in {filename}")

    if errors:
        print("FAILED git submodule and checkout config check:")
        for err in errors:
            print(f"  - {err}")
        return False

    print("PASSED git submodule and checkout config check")
    return True


def check_synthesis_makefile_config(repo_root="."):
    makefile_path = os.path.join(repo_root, "src/Makefile")
    if not os.path.exists(makefile_path):
        print(f"ERROR: {makefile_path} does not exist.")
        return False

    with open(makefile_path, "r") as f:
        content = f.read()

    errors = []

    if "yosys" not in content:
        errors.append("Missing Yosys command reference in src/Makefile")

    if "stdcells.v" not in content:
        errors.append("Missing stdcells.v inclusion in Yosys elaboration rule in src/Makefile")

    if "sky130" in content:
        errors.append("Found legacy sky130 reference in src/Makefile")

    if errors:
        print(f"FAILED synthesis Makefile config check in {makefile_path}:")
        for err in errors:
            print(f"  - {err}")
        return False

    print(f"PASSED synthesis Makefile config check in {makefile_path}")
    return True


def check_stdcell_declarations(repo_root="."):
    stdcells_path = os.path.join(repo_root, "src/stdcells.v")
    ctrl_block_path = os.path.join(repo_root, "src/ctrl_block.v")
    ctrl_top_path = os.path.join(repo_root, "src/ctrl_top.v")
    project_path = os.path.join(repo_root, "src/project.v")

    errors = []

    if not os.path.exists(stdcells_path):
        errors.append(f"Missing file: {stdcells_path}")
    else:
        with open(stdcells_path, "r") as f:
            content = f.read()
        if "sky130_fd_sc_hd" in content:
            errors.append("Found legacy sky130_fd_sc_hd reference in src/stdcells.v")
        if "sg13g2_" not in content:
            errors.append("Missing sg13g2_ standard cell blackbox declarations in src/stdcells.v")

    for path in [ctrl_block_path, ctrl_top_path, project_path]:
        filename = os.path.basename(path)
        if not os.path.exists(path):
            errors.append(f"Missing file: {path}")
        else:
            with open(path, "r") as f:
                content = f.read()
            if "sky130_fd_sc_hd" in content:
                errors.append(f"Found legacy sky130_fd_sc_hd reference in {filename}")

    if errors:
        print("FAILED stdcell declarations check:")
        for err in errors:
            print(f"  - {err}")
        return False

    print("PASSED stdcell declarations check")
    return True


def main():
    print("=== Running CI/CD Configuration Verification ===")
    # Locate repo root (assuming py/ directory resides directly under repo root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, ".."))

    gds_ok = check_gds_workflow(repo_root)
    docs_ok = check_docs_workflow(repo_root)
    info_ok = check_info_yaml(repo_root)
    artifacts_ok = check_gds_lef_artifacts(repo_root)
    pages_ok = check_pages_api_config(repo_root)
    precheck_def_pin_ok = check_precheck_def_and_pin_config(repo_root)
    def_template_ok = check_def_template_config(repo_root)
    top_module_step_ok = check_top_module_step_config(repo_root)
    viewer_docs_deploy_ok = check_viewer_and_docs_deployment_config(repo_root)
    lef_pin_boundary_ok = check_lef_pin_and_boundary_config(repo_root)
    docs_build_asset_ok = check_docs_build_and_asset_config(repo_root)
    viewer_artifact_ok = check_viewer_artifact_and_staging_config(repo_root)
    pages_deploy_ok = check_pages_deployment_and_oidc_config(repo_root)
    drc_geom_ok = check_klayout_drc_and_geometry_config(repo_root)
    eda_toolchain_ok = check_eda_toolchain_and_container_config(repo_root)
    precheck_exec_ok = check_precheck_execution_and_reporting_config(repo_root)
    wf_summary_ok = check_workflow_execution_summary_config(repo_root)
    wf_trigger_ok = check_workflow_trigger_events_config(repo_root)
    checkout_submodule_ok = check_git_submodule_and_checkout_config(repo_root)
    stdcell_decl_ok = check_stdcell_declarations(repo_root)
    synthesis_makefile_ok = check_synthesis_makefile_config(repo_root)

    if (
        gds_ok
        and docs_ok
        and info_ok
        and artifacts_ok
        and pages_ok
        and precheck_def_pin_ok
        and def_template_ok
        and top_module_step_ok
        and viewer_docs_deploy_ok
        and lef_pin_boundary_ok
        and docs_build_asset_ok
        and viewer_artifact_ok
        and pages_deploy_ok
        and drc_geom_ok
        and eda_toolchain_ok
        and precheck_exec_ok
        and wf_summary_ok
        and wf_trigger_ok
        and checkout_submodule_ok
        and stdcell_decl_ok
        and synthesis_makefile_ok
    ):
        print("All CI/CD configuration checks passed successfully!")
        sys.exit(0)
    else:
        print("CI/CD configuration verification failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
