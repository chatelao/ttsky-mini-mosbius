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
  - [ ] **1.3.3** Execute Pages API check via `curl -H "Authorization: Bearer <token>" https://api.github.com/repos/<owner>/<repo>/pages` to verify HTTP 200 OK status.

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
    - [ ] **3.3.1.1** Verify `push` event triggers `gds` and `docs` workflows automatically on push.
    - [ ] **3.3.1.2** Verify `workflow_dispatch` manual trigger option is available in Actions UI.
  - [ ] **3.3.2 Monitor Live Job Execution**
    - [ ] **3.3.2.1** Verify `check` job completes successfully in ~1 minute.
    - [ ] **3.3.2.2** Verify `gds` job output artifacts (`gds/tt_um_tnt_mosbius.gds`, `lef/tt_um_tnt_mosbius.lef`).
    - [ ] **3.3.2.3** Verify `precheck` job execution starts upon `gds` completion.
    - [ ] **3.3.2.4** Verify `viewer` job execution starts upon `gds` completion.
  - [ ] **3.3.3 Inspect Pipeline Execution Logs**
    - [ ] **3.3.3.1** Review full build logs for warning messages or unexpected tool output.
    - [ ] **3.3.3.2** Confirm overall workflow completion status is green across all matrix jobs.

- [ ] **3.4 Verify Precheck Job Execution & Output**
  - [ ] **3.4.1 Verify DEF Template Resolution**
    - [ ] **3.4.1.1** Check precheck logs to confirm `../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def` is found and loaded without `FileNotFoundError`.
  - [ ] **3.4.2 Validate SG13G2 Boundary & Layer Checks**
    - [ ] **3.4.2.1** Confirm `prBoundary.boundary` layer `235/4` is correctly detected instead of sky130 `189/4`.
    - [ ] **3.4.2.2** Verify front-end active and gate layers (layers 64, 65, 66) pass layer check without invalid layer errors.
    - [ ] **3.4.2.3** Verify metal interconnect layers (layers 67, 68, 69, 70, 71) pass layer check without false positive invalid layer errors.
    - [ ] **3.4.2.4** Verify special and boundary layers (layers 235, 236) pass layer check.
  - [ ] **3.4.3 Confirm Analog Pin Placement Verification**
    - [ ] **3.4.3.1** Confirm analog pins (`ua[0]` through `ua[5]`) alignment against `tt_analog_3x2_3v3.def`.
    - [ ] **3.4.3.2** Confirm power and ground pins (`vdpwr`, `vapwr`, `vgnd`) pin bounding box checks pass.
  - [ ] **3.4.4 Confirm Precheck Job Green Status**
    - [ ] **3.4.4.1** Verify KLayout DRC step completes with zero errors.
    - [ ] **3.4.4.2** Confirm overall precheck job completes with a successful green status check.

- [ ] **3.5 Verify Pages & Documentation Deployment Jobs**
  - [ ] **3.5.1 Confirm 3D Viewer Artifact & Pages Deployment**
    - [ ] **3.5.1.1** Verify `gds_render` 3D rendering artifact is generated by `viewer` job.
    - [ ] **3.5.1.2** Verify `gh-pages/index.html` file is generated referencing PDK `ihp-sg13g2`.
    - [ ] **3.5.1.3** Confirm `actions/deploy-pages@v5` step executes without HTTP 404 API error.
  - [ ] **3.5.2 Confirm Documentation Build Job**
    - [ ] **3.5.2.1** Verify `docs` action builds documentation PDF/HTML from repository markdown files.
    - [ ] **3.5.2.2** Confirm documentation artifact is uploaded and accessible in workflow summary.
  - [ ] **3.5.3 Validate Live Page URLs**
    - [ ] **3.5.3.1** Access `https://<owner>.github.io/<repo>/` in browser.
    - [ ] **3.5.3.2** Confirm 3D layout viewer loads and displays `tt_um_tnt_mosbius.gds` geometry interactively.
