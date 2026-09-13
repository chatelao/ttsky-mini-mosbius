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

    if gds_ok and docs_ok and info_ok and artifacts_ok and pages_ok and precheck_def_pin_ok:
        print("All CI/CD configuration checks passed successfully!")
        sys.exit(0)
    else:
        print("CI/CD configuration verification failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
