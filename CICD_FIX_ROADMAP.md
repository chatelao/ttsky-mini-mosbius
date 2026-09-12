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

- [ ] **1.1 Enable GitHub Pages Deployment Source**
  - [ ] **1.1.1 Navigate to GitHub Pages Settings**
    - Open `https://github.com/<owner>/<repo>/settings/pages` in browser or verify Pages API configuration via GitHub REST API / CLI (`gh api repos/<owner>/<repo>/pages`).
  - [ ] **1.1.2 Configure Build and Deployment Source**
    - Under **Build and deployment**, change **Source** from `Deploy from a branch` to **`GitHub Actions`**.
  - [ ] **1.1.3 Save and Verify Configuration**
    - Save changes and confirm that Pages deployment permissions allow workflow runs to create deployments.

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
  - [ ] **3.2.1 Commit Local Workflow & Roadmap Changes**
    - Ensure all workflow updates and roadmap updates are committed locally on git branch.
  - [ ] **3.2.2 Push Branch to Remote Repository**
    - Push branch to GitHub remote repository (`git push origin <branch_name>`).
  - [ ] **3.2.3 Monitor GitHub Actions Pipeline Execution**
    - Open GitHub repository **Actions** tab and monitor active runs for `gds.yaml` (`gds`, `precheck`, `viewer` jobs) and `docs.yaml` (`docs` job).

- [ ] **3.3 Verify Precheck & Deployment Success**
  - [ ] **3.3.1 Resolve DEF Template File Path & Pin/Boundary Check**
    - [ ] **3.3.1.1 Check DEF Template Path Resolution**
      - Verify `precheck` action output logs show `../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def` is found without `[Errno 2] No such file or directory` errors.
    - [ ] **3.3.1.2 Verify Pin & Boundary Check Log Status**
      - Confirm `Pin check` and `Boundary check` report `✅ Pass` in job summary.
  - [ ] **3.3.2 Validate SG13G2 Layer Map & Boundary Layers**
    - [ ] **3.3.2.1 Verify SG13G2 prBoundary Layer Detection**
      - Confirm `prBoundary.boundary` check uses layer `235/4` (SG13G2) instead of SkyWater `189/4`.
    - [ ] **3.3.2.2 Verify Layer Map Allowed Layers**
      - Confirm `Layer check` passes without reporting invalid layer errors on standard SG13G2 metal/activ layers (64-71).
  - [ ] **3.3.3 Verify Analog Pin Placement & Precheck Execution**
    - [ ] **3.3.3.1 Verify Analog Pin Check**
      - Confirm `Analog pin check` succeeds without cascaded missing DEF file errors.
    - [ ] **3.3.3.2 Verify Overall Precheck Job Status**
      - Confirm `precheck` job finishes with a green checkmark status in GitHub Actions.
  - [ ] **3.3.4 Confirm GitHub Pages Viewer & Docs Deployment**
    - [ ] **3.3.4.1 Confirm Viewer Deployment API Request**
      - Confirm `actions/deploy-pages@v5` in `viewer` job receives `201 Created` response instead of `404 Not Found`.
    - [ ] **3.3.4.2 Confirm 3D GDS Viewer Site URL**
      - Visit deployed GitHub Pages URL (`https://<owner>.github.io/<repo>/`) to verify 3D GDS rendering page loads properly.
    - [ ] **3.3.4.3 Confirm Documentation Site Build**
      - Verify `docs` workflow job successfully builds and publishes project documentation.
