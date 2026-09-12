# CI/CD Failure Analysis & Fix Concept (`CICD_FIX_CONECPT.md`)

## Executive Summary
This document provides a detailed analysis of all errors found in the GitHub Actions CI/CD run logs for the `ttsky-mini-mosbius` project:
1. **First Action Flow**: `precheck` job (Job Run `bef31c12-318f-50d5-a145-7b65c35db4c3`)
2. **Second Action Flow**: `viewer` job (Job Run `911c0c88-54d1-565f-825d-a75110d48289`)

It outlines root causes and a step-by-step remediation plan to resolve all CI/CD pipeline issues.

---

## 1. Error Overview & Summary Tables

### 1.1 First Action Flow: `precheck` Job (`bef31c12-318f-50d5-a145-7b65c35db4c3`)
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

### 1.2 Second Action Flow: `viewer` Job (`911c0c88-54d1-565f-825d-a75110d48289`)
During execution of the `viewer` job in `.github/workflows/gds.yaml`, the workflow failed during GitHub Pages deployment with the following summary:

| Viewer Step | Result | Error Message / Details |
| :--- | :---: | :--- |
| **Download GDS artifact** | ✅ Pass | Successfully downloaded `tt_submission` |
| **Read PDK information** | ✅ Pass | `PDK=ihp-sg13g2` extracted from `pdk.json` |
| **Download gds_render artifact** | ✅ Pass | Successfully downloaded `gds_render` |
| **Copy OAS And GDSII** | ✅ Pass | Copied files to `gh-pages/` directory |
| **Generate redirect HTML page** | ✅ Pass | Created `gh-pages/index.html` referencing `pdk=ihp-sg13g2` |
| **Upload Pages artifact** | ✅ Pass | Archived and uploaded `github-pages` artifact |
| **Deploy to GitHub Pages** | ❌ Fail | `HttpError: Not Found (status: 404)` - `Failed to create deployment ... Ensure GitHub Pages has been enabled` |
| **Check for failure** | ❌ Fail | `Failed to deploy to GitHub Pages, please follow the link to troubleshoot: https://tinytapeout.com/faq/#my-github-action-is-failing-on-the-pages-part` |
| **Action Tag Specification** | ⚠️ Warning | Using `TinyTapeout/tt-gds-action/viewer@ttsky26c` instead of `@ttihp26b` |

---

## 2. Detailed Root Cause Analysis

### Error 1: Action Tag Mismatch (`@ttsky26c` vs `@ttihp26b`)
* **Log Lines:**
  ```text
  Download action repository 'TinyTapeout/tt-gds-action@ttsky26c'
  Run TinyTapeout/tt-gds-action/precheck@ttsky26c
  Run TinyTapeout/tt-gds-action/viewer@ttsky26c
  ```
* **Root Cause:**
  The workflows `.github/workflows/gds.yaml` and `.github/workflows/docs.yaml` use `TinyTapeout/tt-gds-action/*@ttsky26c`.
  The `@ttsky26c` tag is meant for SkyWater 130nm (`sky130A`) TinyTapeout shuttles. The current repository targets the **IHP SG13G2** process (`ihp-sg13g2`).
  Invoking `@ttsky26c` forces `tt-support-tools` to use SkyWater 130nm layer maps, DEF templates, viewer configurations, and checking logic against an IHP SG13G2 design.

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

### Error 6: GitHub Pages Deployment Failure (HTTP 404 / Not Found)
* **Log Lines:**
  ```text
  2026-09-12T14:47:05.2650482Z ##[error]Creating Pages deployment failed
  2026-09-12T14:47:05.4268138Z ##[error]HttpError: Not Found
  ...
  2026-09-12T14:47:05.4275885Z ##[error]Error: Failed to create deployment (status: 404) with build version c1543e2bcca3e583d8dec0df541374c4484b7e6a. Request ID A420:2B2385:37D9303:B455F66:6AA565E9 Ensure GitHub Pages has been enabled: https://github.com/chatelao/ttsky-mini-mosbius/settings/pages
  2026-09-12T14:47:05.4747737Z Failed to deploy to GitHub Pages, please follow the link to troubleshoot: https://tinytapeout.com/faq/#my-github-action-is-failing-on-the-pages-part
  ```
* **Root Cause:**
  The `actions/deploy-pages@v5` action failed with HTTP 404 when attempting to call the GitHub Pages deployment API (`/repos/{owner}/{repo}/pages/deployments`).
  This occurs when:
  1. GitHub Pages is not enabled in the repository settings.
  2. The GitHub Pages build and deployment source is not configured to **GitHub Actions** (under Repository Settings -> Pages -> Build and deployment -> Source).

---

## 3. How to Tackle and Fix the Errors

To resolve all failures across both action flows, update GitHub repository configuration settings and update the GitHub Actions workflows to reference `@ttihp26b` instead of `@ttsky26c`.

### 1. Enable GitHub Pages in Repository Settings
In the GitHub repository settings for `chatelao/ttsky-mini-mosbius`:
1. Navigate to **Settings** -> **Pages**.
2. Under **Build and deployment**:
   - Set **Source** to **GitHub Actions** (instead of "Deploy from a branch").
3. Save the settings.

---

### 2. Update `.github/workflows/gds.yaml`
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

---

### 3. Update `.github/workflows/docs.yaml`
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

After applying these workflow updates and repository settings:
1. Local pre-push verification:
   ```bash
   make check
   make lint
   ```
2. Trigger the GitHub Actions CI workflow (`gds.yaml` and `docs.yaml`) to confirm that:
   - The `precheck` job succeeds under `@ttihp26b`.
   - The `viewer` job succeeds and deploys the 3D GDS viewer page to GitHub Pages without 404 errors.
