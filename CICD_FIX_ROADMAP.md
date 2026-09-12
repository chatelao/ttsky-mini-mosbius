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

- [ ] **1.1 Enable GitHub Pages Deployment Source**
  1. Open repository settings in GitHub: `https://github.com/<owner>/<repo>/settings/pages`.
  2. Under **Build and deployment**:
     - Change **Source** from `Deploy from a branch` to **`GitHub Actions`**.
  3. Save changes.

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
  - Push workflow changes to GitHub repository.
  - Monitor CI run progress under the **Actions** tab.

- [ ] **3.3 Verify Precheck & Deployment Success**
  - Confirm `precheck` job passes all checks (KLayout SG13G2 DRC, pin check, layer check, DEF template validation).
  - Confirm `viewer` job successfully deploys the 3D GDS rendering viewer to GitHub Pages without 404 errors.
  - Confirm `docs` job builds documentation successfully.
