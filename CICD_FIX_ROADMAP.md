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
└───────────────────────────┴────────────────────────────┘
```

---

## Phase 1: Repository Settings Configuration (GitHub Pages)

> **Objective:** Ensure the GitHub Pages deployment API is accessible to the `viewer` action job.

- [ ] **1.1 Navigate to GitHub Pages Settings**
  - [ ] **1.1.1** Access `https://github.com/<owner>/<repo>/settings/pages` in web browser as repository admin.
  - [ ] **1.1.2** Verify admin access permissions to repository configuration settings.
  - [ ] **1.1.3** Confirm sub-navigation tab 'Pages' is active under repository Settings sidebar menu.

- [ ] **1.2 Configure Deployment Source to GitHub Actions**
  - [ ] **1.2.1** Locate the **Build and deployment** section in GitHub Pages settings.
  - [ ] **1.2.2** Expand the **Source** dropdown menu currently displaying `Deploy from a branch`.
  - [ ] **1.2.3** Select **`GitHub Actions`** from the available options in the dropdown.
  - [ ] **1.2.4** Verify workflow template suggestions appear for GitHub Pages static site deployment.

- [ ] **1.3 Save Repository Pages Settings & Verify API Accessibility**
  - [ ] **1.3.1** Save settings and confirm GitHub Pages status banner reflects "Build and deployment: GitHub Actions".
  - [ ] **1.3.2** Confirm `actions/deploy-pages` OIDC token permissions (`pages: write`, `id-token: write`) can authenticate against `/repos/{owner}/{repo}/pages/deployments`.
  - [ ] **1.3.3** Ensure custom domain configurations or custom 404 pages do not conflict with root `index.html` viewer deployment.

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
    - [ ] **3.2.1.1** Stage modified workflow files (`.github/workflows/gds.yaml`, `.github/workflows/docs.yaml`).
    - [ ] **3.2.1.2** Stage modified documentation files (`CICD_FIX_ROADMAP.md`).
    - [ ] **3.2.1.3** Run `git status` to verify no untracked or unintended file modifications remain unstaged.
    - [ ] **3.2.1.4** Inspect `git diff --staged` to verify tag updates to `@ttihp26b` and parameter updates (`pdk: ihp-sg13g2`).
  - [ ] **3.2.2 Formulate Conventional Commit Message**
    - [ ] **3.2.2.1** Draft concise commit title under 50 characters (e.g. `ci: update action tags to ttihp26b`).
    - [ ] **3.2.2.2** Draft commit body explaining root cause of `@ttsky26c` mismatch and migration to `@ttihp26b`.
    - [ ] **3.2.2.3** Ensure commit body references the resolution of precheck DEF/layer errors and Pages 404 deployment error.
  - [ ] **3.2.3 Commit Staged Changes**
    - [ ] **3.2.3.1** Run `git commit` with drafted message.
    - [ ] **3.2.3.2** Verify local commit hash is generated cleanly.
  - [ ] **3.2.4 Push Branch to Remote GitHub Repository**
    - [ ] **3.2.4.1** Determine target remote name (`origin`) and current tracking branch.
    - [ ] **3.2.4.2** Execute `git push` to transfer local commit history to remote repository.
    - [ ] **3.2.4.3** Confirm remote server accepts push and returns remote branch URL / trigger status.

- [ ] **3.3 Remote CI/CD Trigger & Execution Monitoring (GitHub Actions)**
  - [ ] **3.3.1 Trigger Remote Workflow Run**
    - [ ] **3.3.1.1** Push commits to GitHub repository branch to trigger push events for `gds.yaml` and `docs.yaml`.
    - [ ] **3.3.1.2** Verify workflow run starts in GitHub Actions UI for `gds` workflow.
    - [ ] **3.3.1.3** Verify workflow run starts in GitHub Actions UI for `docs` workflow.
  - [ ] **3.3.2 Monitor Remote `check` Job Execution**
    - [ ] **3.3.2.1** Inspect `check` job log to verify recursive submodule checkout.
    - [ ] **3.3.2.2** Confirm `make check` step passes in clean Ubuntu 24.04 environment.
  - [ ] **3.3.3 Monitor Remote `gds` Job Execution**
    - [ ] **3.3.3.1** Confirm `Read top module name` step extracts `TOP_MODULE=tt_um_tnt_mosbius` from `info.yaml`.
    - [ ] **3.3.3.2** Confirm `custom_gds@ttihp26b` step executes with `pdk: ihp-sg13g2`.
    - [ ] **3.3.3.3** Verify `gds/tt_um_tnt_mosbius.gds` artifact is published.
    - [ ] **3.3.3.4** Verify `lef/tt_um_tnt_mosbius.lef` artifact is published.
  - [ ] **3.3.4 Monitor Downstream `precheck` Job Execution**
    - [ ] **3.3.4.1** Verify `precheck` job starts after successful completion of `gds` job.
    - [ ] **3.3.4.2** Confirm `TinyTapeout/tt-gds-action/precheck@ttihp26b` action executes without syntax errors.
  - [ ] **3.3.5 Monitor Downstream `viewer` Job Execution**
    - [ ] **3.3.5.1** Verify `viewer` job inherits `pages: write` and `id-token: write` workflow permissions.
    - [ ] **3.3.5.2** Confirm `TinyTapeout/tt-gds-action/viewer@ttihp26b` action downloads `gds_render` artifact.
  - [ ] **3.3.6 Monitor Downstream `docs` Job Execution**
    - [ ] **3.3.6.1** Verify `docs` workflow in `.github/workflows/docs.yaml` runs in parallel with `gds` workflow.
    - [ ] **3.3.6.2** Confirm `TinyTapeout/tt-gds-action/docs@ttihp26b` action builds project documentation.
  - [ ] **3.3.7 Review Workflow Execution Summary**
    - [ ] **3.3.7.1** Inspect detailed job execution logs for `gds` workflow.
    - [ ] **3.3.7.2** Inspect detailed job execution logs for `docs` workflow.
    - [ ] **3.3.7.3** Confirm all steps complete without fatal errors or unhandled exceptions.

- [ ] **3.4 Remote Verification of Precheck Job Execution & Output**
  - [ ] **3.4.1 DEF Template & Tech File Resolution**
    - [ ] **3.4.1.1** Inspect precheck step log in GitHub Actions to confirm `../tech/ihp-sg13g2/def/analog/tt_analog_3x2_3v3.def` path is resolved.
    - [ ] **3.4.1.2** Verify in remote log output that template DEF file is parsed without `Errno 2` missing file errors.
  - [ ] **3.4.2 Boundary & Layer Checks Verification**
    - [ ] **3.4.2.1** Confirm SG13G2 `prBoundary.boundary` layer `235/4` detection (replacing sky130 `189/4`).
    - [ ] **3.4.2.2** Confirm standard SG13G2 layers (64-71, 235) pass layer validation without false positive errors.
  - [ ] **3.4.3 Pin Placement & DRC Verification**
    - [ ] **3.4.3.1** Confirm analog pin placement checks against the template DEF succeed for `tt_um_tnt_mosbius.gds`.
    - [ ] **3.4.3.2** Verify KLayout SG13G2 DRC and zero-area checks pass cleanly.
  - [ ] **3.4.4 Precheck Job Final Status**
    - [ ] **3.4.4.1** Verify precheck summary table displays green checkmarks for all checks.
    - [ ] **3.4.4.2** Check that the `precheck` job status badge is green (success) in GitHub Actions.

- [ ] **3.5 Remote Verification of Pages & Documentation Deployment**
  - [ ] **3.5.1 3D Viewer Artifact Generation**
    - [ ] **3.5.1.1** Verify in `viewer` job logs that `gds_render` artifact is downloaded.
    - [ ] **3.5.1.2** Verify 3D web model and `index.html` redirect page referencing `pdk=ihp-sg13g2` are generated.
    - [ ] **3.5.1.3** Confirm `gh-pages/` staging folder is created containing OAS and GDSII files.
  - [ ] **3.5.2 GitHub Pages Deployment Verification**
    - [ ] **3.5.2.1** Verify `actions/upload-pages-artifact` produces `github-pages` artifact tarball.
    - [ ] **3.5.2.2** Confirm `actions/deploy-pages` step requests OIDC ID token using `id-token: write` permission.
    - [ ] **3.5.2.3** Confirm `actions/deploy-pages` step completes with HTTP 200/201 response in remote log output (no 404 error).
  - [ ] **3.5.3 Published Site & Documentation Verification**
    - [ ] **3.5.3.1** Verify `docs` job log output shows successful build and publication of documentation artifacts.
    - [ ] **3.5.3.2** Navigate to the published GitHub Pages site URL in a web browser to confirm 3D top module model renders correctly.
    - [ ] **3.5.3.3** Verify project overview and pinout details from `info.yaml` render correctly on the docs page.
    - [ ] **3.5.3.4** Confirm WebGL 3D rendering canvas loads without shader or texture errors.
