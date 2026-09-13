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

    if errors:
        print(f"FAILED {filepath}:")
        for err in errors:
            print(f"  - {err}")
        return False

    print(f"PASSED {filepath} (top_module={match.group(1)})")
    return True


def main():
    print("=== Running CI/CD Configuration Verification ===")
    # Locate repo root (assuming py/ directory resides directly under repo root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, ".."))

    gds_ok = check_gds_workflow(repo_root)
    docs_ok = check_docs_workflow(repo_root)
    info_ok = check_info_yaml(repo_root)

    if gds_ok and docs_ok and info_ok:
        print("All CI/CD configuration checks passed successfully!")
        sys.exit(0)
    else:
        print("CI/CD configuration verification failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
