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

- [ ] **1.1 Navigate to GitHub Pages Settings**
  - [ ] **1.1.1** Access `https://github.com/<owner>/<repo>/settings/pages` in web browser as repository admin.
  - [ ] **1.1.2** Verify admin access permissions to repository configuration settings.

- [ ] **1.2 Configure Deployment Source to GitHub Actions**
  - [ ] **1.2.1** Locate the **Build and deployment** section in GitHub Pages settings.
  - [ ] **1.2.2** Change **Source** dropdown selection from `Deploy from a branch` to **`GitHub Actions`**.

- [ ] **1.3 Save Repository Pages Settings & Verify API Accessibility**
  - [ ] **1.3.1** Save settings and confirm GitHub Pages reflects "Build and deployment: GitHub Actions".
  - [ ] **1.3.2** Confirm `/repos/{owner}/{repo}/pages/deployments` API endpoint is enabled for GitHub Actions workflow tokens.

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
  - [ ] **3.2.1 Stage Updated Files**
    - Stage modified `.github/workflows/gds.yaml`, `.github/workflows/docs.yaml`, and `CICD_FIX_ROADMAP.md`.
  - [ ] **3.2.2 Create Commit with Conventional Message**
    - Commit staged changes using a short subject line and detailed commit body describing toolchain migration.
  - [ ] **3.2.3 Push Branch to Remote Repository**
    - Push local branch to GitHub to trigger automated CI pipeline execution.

- [ ] **3.3 Trigger and Monitor GitHub Actions Pipeline Run**
  - [ ] **3.3.1 Confirm Automated Workflow Trigger**
    - Confirm pipeline execution is triggered on push or manually invoke `workflow_dispatch`.
  - [ ] **3.3.2 Monitor `check` and `gds` Job Execution**
    - Monitor `check` job log output for `make check` completion.
    - Monitor `gds` job for GDS and LEF artifact generation.
  - [ ] **3.3.3 Monitor `precheck`, `viewer`, and `docs` Job Execution**
    - Track concurrent execution of downstream jobs.
  - [ ] **3.3.4 Inspect Pipeline Execution Logs for Warnings/Errors**
    - Confirm all job steps run to completion without unhandled exceptions or fatal errors.

- [ ] **3.4 Verify Precheck Job Execution & Output**
  - [ ] **3.4.1 Verify DEF Template Path Resolution**
    - Check precheck logs to confirm `../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def` path is correctly expanded.
  - [ ] **3.4.2 Confirm DEF Template Loading without FileNotFoundError**
    - Verify template DEF file is parsed without `Errno 2` missing file errors.
  - [ ] **3.4.3 Validate SG13G2 prBoundary Layer Detection**
    - Confirm `prBoundary.boundary` layer `235/4` is correctly detected instead of sky130 `189/4`.
  - [ ] **3.4.4 Validate SG13G2 Standard Layers**
    - Confirm standard SG13G2 layers (e.g. 64-71, 235) pass layer validation without false positive errors.
  - [ ] **3.4.5 Confirm Analog Pin Placement Verification**
    - Verify analog pin location checks against template DEF pass for `tt_um_tnt_mosbius.gds`.
  - [ ] **3.4.6 Confirm Precheck Job Green Status**
    - Verify overall precheck job completes with a successful green status check.

- [ ] **3.5 Verify Pages & Documentation Deployment Jobs**
  - [ ] **3.5.1 Verify 3D Viewer Artifact Generation**
    - Check viewer job log for gds_render artifact download and 3D web model build.
  - [ ] **3.5.2 Confirm Pages Deployment API Call Success**
    - Verify `actions/deploy-pages` succeeds with HTTP 200/201 without 404 Not Found error.
  - [ ] **3.5.3 Confirm Documentation Build Job Output**
    - Verify `docs` job completes successfully and publishes documentation artifacts.
  - [ ] **3.5.4 Validate Live Page Viewer URLs**
    - Access live GitHub Pages viewer URL and verify top module render displays correctly.
