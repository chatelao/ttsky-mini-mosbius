# CI/CD Fix Roadmap (`CICD_FIX_ROADMAP.md`)

## Overview

This document provides the step-by-step roadmap for resolving all GitHub Actions CI/CD pipeline failures and achieving green status for the **Mini-MOSbius** project on IHP SG13G2 (`ihp-sg13g2`).

---

## Phased Roadmap to Green CI/CD

```
┌────────────────────────────────────────────────────────┐
│  Phase 1: Repository Settings Configuration           │
│  - Enable GitHub Pages with source "GitHub Actions"   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  Phase 2: Workflow Configuration Updates               │
│  - Update .github/workflows/gds.yaml to @ttihp26b     │
│  - Update .github/workflows/docs.yaml to @ttihp26b    │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  Phase 3: Validation & CI Execution                    │
│  - Execute local verification (make check, make lint) │
│  - Trigger GitHub Actions CI run                      │
│  - Verify green status on precheck & viewer jobs       │
└───────────────────────────┬────────────────────────────┘
```

---

## Phase 1: Repository Settings Configuration (GitHub Pages)

> **Objective:** Ensure the GitHub Pages deployment API is accessible to the `viewer` action job.

- [ ] **1.1 Open Repository Settings**
  - Navigate to repository settings in GitHub: `https://github.com/<owner>/<repo>/settings/pages`.
- [ ] **1.2 Enable GitHub Pages Deployment Source**
  - Under **Build and deployment**, change **Source** from `Deploy from a branch` to **`GitHub Actions`**.
- [ ] **1.3 Save Pages Configuration & Verify Permissions**
  - Save changes and verify workflow permissions allow `pages: write` and `id-token: write`.

---

## Phase 2: Workflow Definition Updates

> **Objective:** Migrate GitHub Action references to match the `ihp-sg13g2` PDK toolchain tag (`@ttihp26b`).

- [x] **2.1 Update `.github/workflows/gds.yaml`**
  - Update action tags for `custom_gds`, `precheck`, and `viewer` steps:
    - `TinyTapeout/tt-gds-action/custom_gds@ttihp26b`
    - `TinyTapeout/tt-gds-action/precheck@ttihp26b`
    - `TinyTapeout/tt-gds-action/viewer@ttihp26b`
  - Confirm parameter `pdk: ihp-sg13g2` is present in `custom_gds`.

- [x] **2.2 Update `.github/workflows/docs.yaml`**
  - Update action tag for `docs` step:
    - `TinyTapeout/tt-gds-action/docs@ttihp26b`

---

## Phase 3: Local Verification & CI Execution

> **Objective:** Validate code formatting/verification locally and confirm green CI/CD status on GitHub Actions.

- [x] **3.1 Run Local Verification Checks**
  - Execute `make check` to verify Verilog elaboration and Python decap generator execution.
  - Execute `make lint` to verify RTL syntax and formatting.

- [ ] **3.2 Push Changes & Trigger CI Pipeline**
  - [ ] **3.2.1 Commit and Push Workflow Updates**
    - Commit updated `.github/workflows/gds.yaml` and `.github/workflows/docs.yaml` to the remote branch.
  - [ ] **3.2.2 Monitor Actions CI Run**
    - Open the GitHub Actions tab and locate the triggered pipeline run.
  - [ ] **3.2.3 Review Execution Logs Across Jobs**
    - Monitor `check`, `gds`, `precheck`, `viewer`, and `docs` job logs for proper step progression.

- [ ] **3.3 Verify Precheck & Deployment Success**
  - [ ] **3.3.1 Verify Custom GDS Artifact Generation**
    - Confirm `custom_gds` job builds `gds/tt_um_tnt_mosbius.gds` and `lef/tt_um_tnt_mosbius.lef` using `pdk: ihp-sg13g2`.
  - [ ] **3.3.2 Resolve DEF Template File Path & Pin/Boundary Check**
    - Ensure `../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def` template DEF file path is correctly resolved in precheck action environment under `@ttihp26b`.
  - [ ] **3.3.3 Validate SG13G2 Layer Map & Boundary Layers**
    - Verify `prBoundary.boundary` (`235/4` for SG13G2) and GDS layer map checks pass without false positives for standard SG13G2 layers.
  - [ ] **3.3.4 Verify Analog Pin Placement & Precheck Execution**
    - Confirm analog pin checks and overall KLayout DRC checks pass on `tt_um_tnt_mosbius.gds`.
  - [ ] **3.3.5 Confirm GitHub Pages 3D Viewer Deployment**
    - Confirm `viewer` job successfully deploys the 3D GDS rendering viewer to GitHub Pages without HTTP 404 deployment errors.
  - [ ] **3.3.6 Confirm Documentation Generation**
    - Confirm `docs` job builds project documentation using `@ttihp26b` without missing PDK references.
