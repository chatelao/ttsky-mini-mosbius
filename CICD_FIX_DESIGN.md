# CI/CD Fix Design Document (`CICD_FIX_DESIGN.md`)

## 1. System Goal & Scope

This document specifies the technical design to fix all GitHub Actions CI/CD failures for Sylvain Munaut's (246tnt) variant of **Mini-MOSbius** targeted at the **IHP SG13G2** process (`ihp-sg13g2`).

The scope encompasses:
1. Correcting GitHub Actions workflow configurations in `.github/workflows/gds.yaml` and `.github/workflows/docs.yaml`.
2. Resolving PDK and technology toolchain mismatches (`sky130A` vs `ihp-sg13g2`).
3. Alignment with TinyTapeout IHP shuttle tooling standards (`@ttihp26b`).
4. Enabling GitHub Pages deployment configuration for automated 3D GDS rendering viewer output.

---

## 2. Root Cause Analysis & Technical Design Fixes

### 2.1 Action Tag Mismatch & Precheck Layer/DEF Failures

#### Problem Analysis
The workflows currently reference `TinyTapeout/tt-gds-action/*@ttsky26c`.
* The `@ttsky26c` tag invokes scripts configured for SkyWater 130nm (`sky130A`).
* Under `@ttsky26c`, `precheck` searches for SkyWater DEF templates and evaluates GDS layers against SkyWater layer maps (e.g., checking for `prBoundary` on layer `189/4` instead of IHP SG13G2 boundary layer `235/4`).
* This causes false positive failures on layer checks, boundary checks, and pin checks.

#### Design Solution
Update all `TinyTapeout/tt-gds-action/*` action references from `@ttsky26c` to `@ttihp26b`.
* `@ttihp26b` uses the proper `ihp-sg13g2` tech files, DEF templates (`tt_analog_3x2_3v3.def`), and KLayout DRC/LVS rule decks tailored for IHP 130nm SG13G2.

---

### 2.2 GitHub Pages Deployment Failure (HTTP 404 / Not Found)

#### Problem Analysis
During the `viewer` job in `.github/workflows/gds.yaml`, deployment via `actions/deploy-pages@v5` fails with:
`HttpError: Not Found (status: 404)` - `Ensure GitHub Pages has been enabled`.

This occurs because:
1. GitHub Pages is not initialized/enabled on the target GitHub repository.
2. The GitHub Pages build and deployment source setting is not set to **GitHub Actions**.

#### Design Solution
Specify the required repository settings configuration and workflow permissions:
1. Ensure the `viewer` job in `.github/workflows/gds.yaml` retains required permissions:
   ```yaml
   permissions:
     pages: write
     id-token: write
   ```
2. Document mandatory GitHub repository configuration step in `CICD_FIX_ROADMAP.md` (Settings -> Pages -> Build and deployment -> Source: GitHub Actions).

---

## 3. Workflow File Specifications

### 3.1 Updated `.github/workflows/gds.yaml`

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

### 3.2 Updated `.github/workflows/docs.yaml`

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

## 4. Verification & Criteria for Success

1. **Workflow Verification:**
   - Both `.github/workflows/gds.yaml` and `.github/workflows/docs.yaml` reference `@ttihp26b`.
   - `pdk` parameter in `custom_gds` step remains `ihp-sg13g2`.
2. **Local Repository Verification:**
   - `make check` and `make lint` execute successfully without errors.
3. **CI Pipeline Verification:**
   - `check` job passes.
   - `gds` job generates GDS/LEF artifacts successfully.
   - `precheck` job completes green with IHP SG13G2 layer map and DEF templates.
   - `viewer` and `docs` jobs build and publish artifacts / pages without 404 errors.
