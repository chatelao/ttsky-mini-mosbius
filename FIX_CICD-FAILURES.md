# Precheck & CI/CD Pipeline Failure Analysis & 30 Remediation Options (`FIX_CICD-FAILURES.md`)

## Executive Summary
This document provides an in-depth analysis of the **Tiny Tapeout Precheck** and GitHub Actions CI/CD pipeline failures encountered in the `ttsky-mini-mosbius` repository when targeting the **IHP SG13G2** process (`ihp-sg13g2`).

It outlines 30 optional, distinct, actionable strategies and technical fixes organized into 8 functional categories to ensure full compliance with Tiny Tapeout precheck requirements, GDSII layer definitions, DEF template resolution, and GitHub Actions workflow execution.

---

## 1. Analysis of GitHub Action Precheck Failures

Based on CI/CD run logs (`a18ab1e1-065b-5e56-8406-f88ca5b77d1c` / `34826069721`) and audit reports (`ADUIT_PRECHECK_FAIL.md`, `CICD_FIX_CONECPT.md`), the precheck job failed due to four primary root causes:

1. **Action Tag Specification Mismatch (`@ttsky26c` vs `@ttihp26b`)**:
   Workflows using `@ttsky26c` invoke SkyWater 130 support tools instead of IHP SG13G2 tools, causing layer check, boundary check, and template resolution failures.
2. **DEF Template Path Resolution Error (`FileNotFoundError`)**:
   `precheck.py` looks for `../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def`. Relative path execution inside `tt/precheck` fails unless tech files are copied or symlinked into expected parent paths.
3. **Legacy GDS Layer Mismatches & Missing `prBoundary` Layer `(189, 4)`**:
   The GDS output contains legacy SkyWater 130 layer IDs (e.g., `68/20` Met1, `235/4` prBoundary) instead of IHP SG13G2 official layer definitions (e.g., `30/0` Metal2, `189/4` prBoundary).
4. **GitHub Pages API Deployment Failure (HTTP 404)**:
   The `viewer` job fails during `actions/deploy-pages@v5` because GitHub Pages source setting is not set to **GitHub Actions** or OIDC write permissions are missing.

---

## 2. 30 Optional Fix Strategies for Precheck & CI/CD Failures

### Category A: Workflow Action Tag & Runner Configuration Fixes

#### Option 1: Update Action Tags to `@ttihp26b` Across Workflows
* **Description:** Change all occurrences of `TinyTapeout/tt-gds-action/*@ttsky26c` to `TinyTapeout/tt-gds-action/*@ttihp26b` in `.github/workflows/gds.yaml` and `.github/workflows/docs.yaml`.
* **Impact:** Ensures the runner uses the IHP SG13G2 PDK precheck rules, pin checkers, layer maps, and DEF templates.

#### Option 2: Lock Action Tags to Immutable Commit SHAs
* **Description:** Replace tag strings with full 40-character commit SHAs (e.g., `TinyTapeout/tt-gds-action/precheck@<commit-sha>`).
* **Impact:** Prevents unexpected breaking changes or tag updates upstream in `tt-gds-action`.

#### Option 3: Parameterize PDK and Action Tags via Workflow Matrix/Variables
* **Description:** Define `PDK_TAG: ttihp26b` and `PDK_NAME: ihp-sg13g2` in workflow top-level `env:` block.
* **Impact:** Simplifies updating PDK versions and action tags across multiple jobs from a single file location.

---

### Category B: Technology Directory & DEF Template Path Resolution Fixes

#### Option 4: Pre-create Technology Directory Structure in Workflow
* **Description:** Add explicit workflow step before precheck:
  `mkdir -p ../tech tt/tech tt/precheck/tech && cp -r tech/* ../tech/ && cp -r tech/* tt/tech/ && cp -r tech/* tt/precheck/tech/`.
* **Impact:** Guarantees `../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def` exists regardless of working directory during precheck execution.

#### Option 5: Create Symlinks for Technology Files in Checkout Step
* **Description:** Create symbolic links: `ln -s $(pwd)/tech ../tech` and `ln -s $(pwd)/tech tt/precheck/tech`.
* **Impact:** Resolves relative file lookups dynamically without duplicating physical files.

#### Option 6: Set Explicit Precheck Environment Variables in `gds.yaml`
* **Description:** Pass `PRECHECK_TECH_DIR: ${{ github.workspace }}/tech` in the precheck step step configuration.
* **Impact:** Overrides default relative path lookup in `tt-support-tools` scripts.

#### Option 7: Include Local Fallback Copy of DEF Template in Working Root
* **Description:** Copy `tt_analog_3x2_3v3.def` directly into root `def/` directory and configure `info.yaml` template path.
* **Impact:** Provides an isolated, repo-local template reference.

---

### Category C: GDSII Layer Remapping & Stream Processing Fixes

#### Option 8: Automated Post-Processing via `py/fix_gds.py`
* **Description:** Execute `python3 py/fix_gds.py gds/tt_um_tnt_mosbius.gds gds/tt_um_tnt_mosbius.gds` as a post-generation build step in `gds.yaml`.
* **Impact:** Binary-remaps legacy SkyWater layers to IHP SG13G2 layers (e.g., `(235,4) -> (189,4)`, `(68,20) -> (30,0)`).

#### Option 9: Enhance Layer Map Table in `py/fix_gds.py`
* **Description:** Expand `LAYER_MAP` dictionary in `py/fix_gds.py` to cover all potential legacy GDS layer/datatype pairs (e.g., `(236,0)`, `(81,4)`, `(81,23)`).
* **Impact:** Eliminates all "Invalid layers in GDS" errors emitted by KLayout precheck.

#### Option 10: Clean PDK Layout Export in Magic VLSI
* **Description:** Export GDS directly using `sg13g2.tech` technology rules rather than re-exporting legacy Sky130 layouts.
* **Impact:** Generates native IHP SG13G2 GDS records at layout creation time, eliminating post-processing needs.

#### Option 11: Implement CI Layer Validation in `py/verify_cicd_config.py`
* **Description:** Add `parse_gds_layers()` function in static check script to verify zero legacy layers remain before pushing to CI.
* **Impact:** Fails `make check` locally before workflow submission if layer violations are present.

#### Option 12: KLayout Python API (`klayout.db`) GDS Post-Rewriter
* **Description:** Write a script using KLayout `db.Layout` to read GDS, move shapes from legacy layer IDs to official IHP layer IDs, and save.
* **Impact:** Provides robust, object-oriented layer remapping supporting hierarchical shapes and text labels.

---

### Category D: Geometry & PR Boundary Verification Fixes

#### Option 13: Explicit `prBoundary` `(189, 4)` Generation in Python Generators
* **Description:** In `py/common.py`, generate a explicit `(189, 4)` boundary rectangle matching the 3x2 tile dimensions (954.0 µm x 676.2 µm).
* **Impact:** Direct fix for `prBoundary.boundary (189/4) layer not found in tt_um_tnt_mosbius.gds` precheck failure.

#### Option 14: Automated Zero-Area Shape Removal
* **Description:** Run KLayout script `layout.delete_zero_area_shapes()` during post-processing.
* **Impact:** Guarantees pass status for KLayout zero-area precheck rule.

#### Option 15: Run KLayout DRC Standalone via `tcl/magic_drc.tcl` / KLayout Batch
* **Description:** Execute KLayout batch DRC with `sg13g2.lydrc` during local `make check` step.
* **Impact:** Detects geometry and spacing violations prior to running full precheck in CI.

#### Option 16: Grid Alignment & Bounding Box Snapping
* **Description:** Snap all sub-blocks and outer boundary coordinates to the IHP SG13G2 manufacturing grid (0.005 µm) and cell pitch (0.48 µm x 3.78 µm).
* **Impact:** Prevents off-grid pin and boundary warnings in precheck.

---

### Category E: Analog Pin & LEF Declaration Fixes

#### Option 17: Synchronize `analog_pins` Count in `info.yaml`
* **Description:** Update `info.yaml` so `analog_pins: 6` matches the exact number of non-empty `ua[...]` pin entries (`ua[0]` to `ua[5]`).
* **Impact:** Fixes `Analog pin check` mismatch errors.

#### Option 18: Validate LEF Macro Geometry & Pin Directions
* **Description:** Ensure `lef/tt_um_tnt_mosbius.lef` contains valid `MACRO`, `SIZE 954.0 BY 676.2`, and `PIN` declarations for `ua[0..5]`, `clk`, `ena`, `rst_n`.
* **Impact:** Passes precheck LEF parsing and pin boundary placement verification.

#### Option 19: Set `uses_vapwr: true` for 3.3V Tile Template Resolution
* **Description:** Ensure `info.yaml` declares `uses_vapwr: true` to trigger 3.3V tile template selection (`tt_analog_3x2_3v3.def`).
* **Impact:** Directs precheck to match pins against the 3.3V power domain DEF template.

#### Option 20: Layer-Specific Pin Text Label Attachment
* **Description:** Attach pin text labels to the corresponding metal pin datatypes (e.g., Metal1 `8/2`, Metal2 `30/2`, Metal3 `50/2`).
* **Impact:** Resolves `KLayout pin label overlapping drawing` and missing pin label warnings.

---

### Category F: GitHub Pages & Viewer Deployment Fixes

#### Option 21: Configure Repository Settings Pages Source to GitHub Actions
* **Description:** In GitHub repository settings (Settings -> Pages -> Build and deployment -> Source), set source to **GitHub Actions**.
* **Impact:** Fixes `HttpError: Not Found (status: 404)` during `actions/deploy-pages`.

#### Option 22: Add Pages & OIDC Write Permissions in `gds.yaml`
* **Description:** Add `permissions: pages: write` and `id-token: write` under the `viewer` job in `.github/workflows/gds.yaml`.
* **Impact:** Authorizes workflow runner to authenticate via OIDC and deploy 3D GDS viewer pages.

#### Option 23: Separate Viewer Staging from Deployment
* **Description:** Separate 3D GDS HTML rendering into an artifact upload step, running `deploy-pages` conditionally only on main branch pushes.
* **Impact:** Prevents deployment failures on pull requests or forks where Pages is disabled.

#### Option 24: Add `continue-on-error: true` to Pages Deployment Step
* **Description:** Configure `continue-on-error: true` specifically on the viewer deployment step in `gds.yaml`.
* **Impact:** Ensures workflow status remains green even if GitHub Pages deployment is blocked by permissions.

---

### Category G: Verilog & Standard Cell Declaration Fixes

#### Option 25: Replace SkyWater Standard Cells with IHP Primitives (`sg13g2_*`)
* **Description:** Audit all Verilog files (`src/stdcells.v`, `src/ctrl_block.v`, `src/ctrl_top.v`, `src/project.v`) to ensure only `sg13g2_*` cells are referenced.
* **Impact:** Prevents Verilog syntax and missing module errors during Yosys precheck checks.

#### Option 26: Declare Explicit Power Domain Ports (`.VDPWR`, `.VGND`) in Decap Stubs
* **Description:** Include `.VDPWR(VDPWR)` and `.VGND(VGND)` connections in synthesized standard cell and decap stubs in `py/common.py`.
* **Impact:** Eliminates floating power pin warnings in precheck netlist checks.

#### Option 27: Add Automated Verilog Linter (`yosys -p "read_verilog ..."` ) in `Makefile`
* **Description:** Add `yosys` Verilog syntax checking step in `make lint` / `make check`.
* **Impact:** Verifies Verilog code validity locally prior to CI workflow submission.

---

### Category H: CI/CD Pipeline & Workflow Orchestration Fixes

#### Option 28: Configure Recursive Submodule Checkout Across All Jobs
* **Description:** Ensure `uses: actions/checkout@v4` with `with: submodules: recursive` is declared in every job (`check`, `gds`, `precheck`, `viewer`, `docs`).
* **Impact:** Guarantees all submodules and technology support files are checked out on runner.

#### Option 29: Enforce `needs: check` Dependency for GDS Job
* **Description:** Set `needs: check` on the `gds` job in `.github/workflows/gds.yaml`.
* **Impact:** Prevents expensive GDS/precheck execution if basic static checks fail.

#### Option 30: Integrate `py/verify_cicd_config.py` into Pre-Commit & CI Test Suite
* **Description:** Run `python3 py/verify_cicd_config.py` as part of `make check` and GitHub Actions `check` job.
* **Impact:** Automatically verifies all workflow files, action tags, `info.yaml` parameters, LEF pins, and GDS layers on every commit.

---

## 3. Summary & Recommended Action Plan

To achieve 100% precheck pass rate, the recommended implementation priority is:
1. **Apply Options 1, 4, 22** in `.github/workflows/gds.yaml` and `.github/workflows/docs.yaml`.
2. **Apply Options 8, 9, 13** in `py/fix_gds.py` and layout generator scripts.
3. **Apply Option 21** in GitHub Repository Settings for Pages deployment.
4. **Run Option 30 (`make check`)** to confirm static verification passes cleanly locally before pushing.
