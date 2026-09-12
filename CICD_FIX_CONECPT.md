# CI/CD Failure Analysis & Fix Concept (`CICD_FIX_CONECPT.md`)

## Executive Summary
This document provides a detailed analysis of all errors found in the GitHub Actions CI/CD run log for the `ttsky-mini-mosbius` project (Job Run `bef31c12-318f-50d5-a145-7b65c35db4c3`, `precheck` job) and outlines the step-by-step remediation plan to fix them.

---

## 1. Error Overview & Summary Table

During execution of the `precheck` job in `.github/workflows/gds.yaml`, the precheck step failed with the following results summary:

| Precheck Step | Result | Error Message / Details |
| :--- | :---: | :--- |
| **KLayout pin label overlapping drawing** | ✅ Pass | — |
| **KLayout SG13G2 DRC** | ✅ Pass | — |
| **KLayout zero area** | ✅ Pass | — |
| **KLayout Checks** | ❌ Fail | `prBoundary.boundary (189/4) layer not found in tt_um_tnt_mosbius.gds` |
| **Pin check** | ❌ Fail | `[Errno 2] No such file or directory: '../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def'` |
| **Boundary check** | ❌ Fail | `[Errno 2] No such file or directory: '../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def'` |
| **Layer check** | ❌ Fail | `Invalid layers in GDS: {(64, 5), (95, 20), (71, 20), (64, 20), ...}` |
| **Cell name check** | ✅ Pass | — |
| **Analog pin check** | ❌ Fail | Cascaded failure from missing DEF template file |
| **Verilog syntax check** | ✅ Pass | — |

---

## 2. Detailed Root Cause Analysis

### Error 1: Action Tag Mismatch (`@ttsky26c` vs `@ttihp26b`)
* **Log Lines:**
  ```text
  Download action repository 'TinyTapeout/tt-gds-action@ttsky26c'
  Run TinyTapeout/tt-gds-action/precheck@ttsky26c
  ```
* **Root Cause:**
  The workflow `.github/workflows/gds.yaml` uses `TinyTapeout/tt-gds-action/*@ttsky26c`.
  The `@ttsky26c` tag is meant for SkyWater 130nm (`sky130A`) TinyTapeout shuttles. The current repository targets the **IHP SG13G2** process (`ihp-sg13g2`).
  Invoking `@ttsky26c` forces `tt-support-tools` to use SkyWater 130nm layer maps, DEF templates, and checking logic against an IHP SG13G2 GDS design.

---

### Error 2: Missing DEF Template File Path
* **Log Lines:**
  ```text
  INFO: using def template ../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def
  ...
  | Pin check | ❌ Fail: [Errno 2] No such file or directory: '../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def' |
  | Boundary check | ❌ Fail: [Errno 2] No such file or directory: '../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def' |
  ```
* **Root Cause:**
  The precheck runner under `ttsky26c` expects SkyWater technology trees and fails to locate `tt_analog_3x2_3v3.def` for `ihp-sg13g2`. Switching the action tag to `@ttihp26b` fetches the proper IHP SG13G2 support tools and template DEF files.

---

### Error 3: GDS Layer Map Mismatch (`Invalid layers in GDS`)
* **Log Lines:**
  ```text
  | Layer check | ❌ Fail: Invalid layers in GDS: {(64, 5), (95, 20), (71, 20), (64, 20), (67, 16), (68, 5), (75, 20), (68, 20), (66, 20), (64, 59), (71, 16), (81, 23), (66, 44), (64, 16), (70, 5), (68, 44), (125, 20), (94, 20), (70, 20), (236, 0), (235, 4), (65, 20), (81, 4), (70, 44), (68, 16), (83, 44), (67, 5), (65, 44), (67, 20), (70, 16), (69, 20), (67, 44), (78, 44), (66, 15), (71, 5), (69, 44), (122, 16), (93, 44)} |
  ```
* **Root Cause:**
  Under `@ttsky26c`, the layer checker checks the GDS against SkyWater 130nm PDK allowed layers. Standard IHP SG13G2 GDS layers (e.g. 64=NWell, 65=Activ, 66=GatPoly, 67=Metal1, 68=Metal2, 69=Metal3, 70=Metal4, 71=Metal5) were misidentified as invalid or forbidden layers.

---

### Error 4: Missing SkyWater `prBoundary` Layer (`189/4`)
* **Log Lines:**
  ```text
  | KLayout Checks | ❌ Fail: prBoundary.boundary (189/4) layer not found in .../tt_um_tnt_mosbius.gds |
  ```
* **Root Cause:**
  Layer `189/4` is the `prBoundary` layer in SkyWater 130 (`sky130A`). In IHP SG13G2 (`ihp-sg13g2`), boundary layers are defined on different layer/purpose pairs (e.g., `235/4`). Evaluating SkyWater boundary rules on an IHP layout caused a false failure.

---

### Error 5: Analog Pin Check Failure
* **Log Lines:**
  ```text
  | Analog pin check | ❌ Fail:  |
  ```
* **Root Cause:**
  The analog pin check compares pin placement in GDS/LEF against `tt_analog_3x2_3v3.def`. Because loading the DEF file failed (Error 2), the analog pin check crashed and failed.

---

## 3. How to Tackle and Fix the Errors

To resolve all failures, update the GitHub Actions workflows to reference `@ttihp26b` instead of `@ttsky26c`.

### 1. Update `.github/workflows/gds.yaml`
Modify action references in `.github/workflows/gds.yaml`:

```yaml
name: gds

on:
  push:
  pull_request:
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-24.04
    steps:
      - name: checkout repo
        uses: actions/checkout@v4
        with:
          submodules: recursive

      - name: Run verification checks
        run: |
          make check

  gds:
    runs-on: ubuntu-24.04
    steps:
      - name: checkout repo
        uses: actions/checkout@v4
        with:
          submodules: recursive

      - name: Read top module name
        id: top_module
        run: |
          echo TOP_MODULE=`yq '.project.top_module' info.yaml` | tee $GITHUB_OUTPUT

      - name: Create and publish the GDS artifact
        uses: TinyTapeout/tt-gds-action/custom_gds@ttihp26b
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
      - name: Run Tiny Tapeout Precheck
        uses: TinyTapeout/tt-gds-action/precheck@ttihp26b

  viewer:
    needs: gds
    runs-on: ubuntu-24.04
    continue-on-error: true
    permissions:
      pages: write      # to deploy to Pages
      id-token: write   # to verify the deployment originates from an appropriate source
    steps:
      - uses: TinyTapeout/tt-gds-action/viewer@ttihp26b
```

### 2. Update `.github/workflows/docs.yaml`
Modify action reference in `.github/workflows/docs.yaml`:

```yaml
name: docs

on:
  push:
  pull_request:
  workflow_dispatch:

jobs:
  docs:
    runs-on: ubuntu-24.04
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4
        with:
          submodules: recursive

      - name: Build docs
        uses: TinyTapeout/tt-gds-action/docs@ttihp26b
```

---

## 4. Verification

After applying these workflow updates:
1. Local pre-push verification:
   ```bash
   make check
   make lint
   ```
2. Trigger the GitHub Actions CI workflow to confirm that precheck succeeds under `@ttihp26b`.
