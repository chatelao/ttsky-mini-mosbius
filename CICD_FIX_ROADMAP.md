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
└────────────────────────────────────────────────────────┘
```

---

## Phase 1: Repository Settings Configuration (GitHub Pages)

> **Objective:** Ensure the GitHub Pages deployment API is accessible to the `viewer` action job.

- [ ] **1.1 Navigate to GitHub Pages Settings**
  - Open repository settings in GitHub: `https://github.com/<owner>/<repo>/settings/pages`.

- [ ] **1.2 Configure Deployment Source to GitHub Actions**
  - Under **Build and deployment**, change **Source** from `Deploy from a branch` to **`GitHub Actions`**.

- [ ] **1.3 Save Repository Pages Settings**
  - Save changes and verify GitHub Pages is configured for Actions deployment.

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

- [ ] **3.2 Commit and Push Workflow & Roadmap Updates**
  - Stage updated workflow definitions and roadmap documentation.
  - Commit changes with a descriptive commit message and push to repository.

- [ ] **3.3 Trigger and Monitor GitHub Actions Pipeline Run**
  - Trigger workflow on push or via manual `workflow_dispatch`.
  - Monitor live execution under the repository **Actions** tab.

- [ ] **3.4 Verify Precheck Job Execution & Output**
  - [ ] **3.4.1 Verify DEF Template Resolution**
    - Check precheck logs to confirm `../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def` is found and loaded without `FileNotFoundError`.
  - [ ] **3.4.2 Validate SG13G2 Boundary & Layer Checks**
    - Confirm `prBoundary.boundary` layer `235/4` is correctly detected.
    - Confirm standard SG13G2 layers (e.g. 64-71, 235) pass layer validation without false positive errors.
  - [ ] **3.4.3 Confirm Analog Pin Placement Verification**
    - Verify analog pin location checks against template DEF pass for `tt_um_tnt_mosbius.gds`.
  - [ ] **3.4.4 Confirm Precheck Job Green Status**
    - Verify overall precheck job completes with a successful green status check.

- [ ] **3.5 Verify Pages & Documentation Deployment Jobs**
  - [ ] **3.5.1 Confirm 3D Viewer Artifact & Pages Deployment**
    - Verify `viewer` job generates 3D rendering and deploys to GitHub Pages without HTTP 404 errors.
  - [ ] **3.5.2 Confirm Documentation Build Job**
    - Verify `docs` job completes successfully and publishes documentation artifacts.
  - [ ] **3.5.3 Validate Live Page URLs**
    - Access live GitHub Pages viewer URL and verify top module render displays correctly.
