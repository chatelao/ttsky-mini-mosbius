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
  - [x] **3.1.1 Run `make check`**
    - Execute `make check` to verify Verilog elaboration and Python decap generator execution.
  - [x] **3.1.2 Run `make lint`**
    - Execute `make lint` to verify RTL syntax and formatting.

- [ ] **3.2 Commit and Push Workflow & Roadmap Updates**
  - [ ] **3.2.1 Stage Modified Repository Files**
    - Stage modified workflow files (`.github/workflows/gds.yaml`, `.github/workflows/docs.yaml`) and roadmap file (`CICD_FIX_ROADMAP.md`).
  - [ ] **3.2.2 Formulate Conventional Commit Message**
    - Prepare commit subject line (under 50 characters) and descriptive body detailing `@ttihp26b` action tag migration and roadmap refinements.
  - [ ] **3.2.3 Commit Staged Changes**
    - Execute git commit to record changes locally.
  - [ ] **3.2.4 Push Branch to Remote GitHub Repository**
    - Push local branch to GitHub remote repository to trigger automated CI pipeline execution.

- [ ] **3.3 Remote CI/CD Trigger & Execution Monitoring (GitHub Actions)**
  - [ ] **3.3.1 Trigger Remote Workflow Run**
    - Push commits to GitHub repository or invoke `workflow_dispatch` to trigger the CI pipeline.
  - [ ] **3.3.2 Monitor Remote `check` Job**
    - Access GitHub Actions UI and verify `check` job log output for `make check` execution.
  - [ ] **3.3.3 Monitor Remote `gds` Job**
    - Monitor `gds` job for successful GDS and LEF artifact generation.
  - [ ] **3.3.4 Monitor Downstream `precheck` Job Status**
    - Monitor progress of `precheck` job execution in GitHub Actions UI.
  - [ ] **3.3.5 Monitor Downstream `viewer` Job Status**
    - Monitor progress of `viewer` job execution in GitHub Actions UI.
  - [ ] **3.3.6 Monitor Downstream `docs` Job Status**
    - Monitor progress of `docs` job execution in GitHub Actions UI.
  - [ ] **3.3.7 Review Workflow Execution Summary**
    - Inspect detailed job execution logs to confirm all steps complete without fatal errors or unhandled exceptions.

- [ ] **3.4 Remote Verification of Precheck Job Execution & Output**
  - [ ] **3.4.1 Check DEF Template Resolution in Remote Logs**
    - Inspect precheck step log in GitHub Actions to confirm `../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def` path is resolved.
  - [ ] **3.4.2 Confirm DEF Template Parsing**
    - Verify in remote log output that template DEF file is parsed without `Errno 2` missing file errors.
  - [ ] **3.4.3 Confirm SG13G2 prBoundary Detection**
    - Verify in remote log output that `prBoundary.boundary` layer `235/4` is detected (replacing sky130 `189/4`).
  - [ ] **3.4.4 Confirm SG13G2 Layer Map Validation**
    - Verify in remote log output that standard SG13G2 layers (64-71, 235) pass layer validation without false positive errors.
  - [ ] **3.4.5 Confirm Analog Pin Placement Checks**
    - Verify in remote log output that analog pin checks against the template DEF succeed for `tt_um_tnt_mosbius.gds`.
  - [ ] **3.4.6 Confirm Precheck Job Final Status**
    - Check that the `precheck` job status badge is green (success) in GitHub Actions.

- [ ] **3.5 Remote Verification of Pages & Documentation Deployment**
  - [ ] **3.5.1 Check 3D Viewer Artifact Generation**
    - Verify in `viewer` job logs that `gds_render` artifact is downloaded and 3D web model is generated.
  - [ ] **3.5.2 Check Pages Deployment API Response**
    - Confirm `actions/deploy-pages` step completes with HTTP 200/201 response in remote log output.
  - [ ] **3.5.3 Check Documentation Build Artifacts**
    - Verify `docs` job log output shows successful build and publication of documentation artifacts.
  - [ ] **3.5.4 Verify Live Pages Web Output**
    - Navigate to the published GitHub Pages site URL in a web browser to confirm 3D top module model renders correctly.
