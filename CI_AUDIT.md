# CI/CD Target Conflict Audit Report (`CI_AUDIT.md`)

## Executive Summary

This audit report provides a comparative analysis of target specifications, action configurations, and deployment requirements between `CICD_FIX_ROADMAP.md` and `ROADMAP.md` for the **Mini-MOSbius** project on IHP SG13G2 (`ihp-sg13g2`).

The primary objective of this audit is to identify target conflicts, omissions, and discrepancies between the project migration roadmap (`ROADMAP.md`) and the dedicated CI/CD fix roadmap (`CICD_FIX_ROADMAP.md`), ensuring full alignment across workflows, automation scripts, and documentation.

---

## 1. Overview of Analyzed Documents

| Document | Purpose & Scope | Target Focus |
| :--- | :--- | :--- |
| **`ROADMAP.md`** | High-level, 5-phase migration roadmap for porting Mini-MOSbius from SkyWater 130nm (`sky130A`) to IHP SG13G2 (`sg13g2`). | Full chip migration (CI/CD, Schematics, Digital Logic, Layout, Verification). |
| **`CICD_FIX_ROADMAP.md`** | Detailed operational roadmap focused specifically on fixing GitHub Actions CI/CD pipeline failures and achieving green CI status. | CI/CD pipeline repair, action tag migration, Pages/OIDC deployment, and automated config verification. |

---

## 2. Detailed Target Conflicts and Discrepancies

### Conflict 1: PDK Identifier Parameter Mismatch (`pdk: sg13g2` vs `pdk: ihp-sg13g2`)

* **`ROADMAP.md` (Phase 1.1):**
  Specifies updating `.github/workflows/gds.yaml` with parameter `pdk: sg13g2`.
* **`CICD_FIX_ROADMAP.md` (Phase 2.1):**
  Specifies updating `.github/workflows/gds.yaml` with parameter `pdk: ihp-sg13g2`.
* **Actual Codebase Implementation:**
  `.github/workflows/gds.yaml` uses `pdk: ihp-sg13g2`, and static verification (`py/verify_cicd_config.py`) enforces `pdk: ihp-sg13g2`.
* **Severity:** **High (Functional Failure)**
* **Analysis:** Using `pdk: sg13g2` causes action failures in `TinyTapeout/tt-gds-action@ttihp26b` because the IHP SG13G2 action runner specifically expects the canonical PDK identifier string `ihp-sg13g2`.

---

### Conflict 2: Action Tag Specification & Toolchain Versioning

* **`ROADMAP.md` (Phase 1.1):**
  References generic `tt-gds-action updates` without specifying explicit action release tags.
* **`CICD_FIX_ROADMAP.md` (Phase 2.1 & 2.2):**
  Explicitly mandates the `@ttihp26b` action tag for all workflow steps (`custom_gds@ttihp26b`, `precheck@ttihp26b`, `viewer@ttihp26b`, `docs@ttihp26b`).
* **Actual Codebase Implementation:**
  Both `.github/workflows/gds.yaml` and `.github/workflows/docs.yaml` use `@ttihp26b`.
* **Severity:** **High (Build / Toolchain Failure)**
* **Analysis:** Unspecified or legacy action tags (such as `@ttsky26c`) pull SkyWater 130nm technology decks, resulting in missing DEF template errors (`tt_analog_3x2_3v3.def`) and false-positive layer check failures in precheck. `@ttihp26b` is required for IHP SG13G2 compatibility.

---

### Conflict 3: GitHub Pages Deployment Prerequisites & OIDC Configuration Gap

* **`ROADMAP.md` (Phase 1):**
  Omits GitHub Pages deployment configuration, OIDC permission settings, and API authentication prerequisites.
* **`CICD_FIX_ROADMAP.md` (Phase 1):**
  Provides a dedicated phase for GitHub Pages repository settings (setting Build and deployment Source to `GitHub Actions`) and details OIDC token permissions (`pages: write`, `id-token: write`) in `gds.yaml`.
* **Actual Codebase Implementation:**
  `.github/workflows/gds.yaml` includes explicit `permissions: pages: write` and `id-token: write` on the `viewer` job.
* **Severity:** **Medium (Deployment Failure)**
* **Analysis:** Without setting GitHub Pages source to "GitHub Actions" in repository settings, the `viewer` action job fails with `HttpError: Not Found (status: 404)` during site deployment. `ROADMAP.md` lacks coverage of this critical deployment requirement.

---

### Conflict 4: CI/CD Verification Infrastructure & Static Testing Depth

* **`ROADMAP.md` (Phase 1.3):**
  Mentions basic "Makefile lint and synthesis check targets to be executed in CI".
* **`CICD_FIX_ROADMAP.md` (Phase 3.1.3):**
  Details static CI/CD workflow parameter verification (`py/verify_cicd_config.py`) and unit testing (`py/test_verify_cicd_config.py`) covering action tags, PDK parameters, permissions, dependencies, runner OS (`ubuntu-24.04`), and top module definitions.
* **Actual Codebase Implementation:**
  `make check` executes `py/verify_cicd_config.py` and runs `python3 -m unittest discover -s py`.
* **Severity:** **Low (Documentation Completeness)**
* **Analysis:** `ROADMAP.md` understates the automated verification suite implemented in the repository to prevent workflow regression.

---

### Conflict 5: Scope Alignment & Phase Granularity

* **`ROADMAP.md`:**
  Presents a macro-level 5-phase migration path covering the full lifecycle of chip redesign (CI/CD, Schematics, Digital Logic, Python layout generators, and Physical Verification).
* **`CICD_FIX_ROADMAP.md`:**
  Presents a micro-level 3-phase operational plan for fixing and monitoring the CI/CD pipeline infrastructure.
* **Severity:** **Informational (Architectural Alignment)**
* **Analysis:** The two documents serve complementary roles, but `ROADMAP.md` Phase 1 must reflect the exact technical parameters defined in `CICD_FIX_ROADMAP.md` to avoid misleading developers or maintainers.

---

## 3. Impact Analysis Summary Table

| Conflict / Issue | `ROADMAP.md` Specification | `CICD_FIX_ROADMAP.md` Specification | Repository Source of Truth | Operational Impact |
| :--- | :--- | :--- | :--- | :--- |
| **PDK Parameter** | `pdk: sg13g2` | `pdk: ihp-sg13g2` | `pdk: ihp-sg13g2` | Action runner fails if set to `sg13g2`. |
| **Action Tag** | Unspecified (`tt-gds-action updates`) | Explicit `@ttihp26b` | `@ttihp26b` | Legacy tags cause precheck DEF & layer failures. |
| **GitHub Pages** | Not mentioned | Source: `GitHub Actions` + OIDC permissions | `pages: write`, `id-token: write` | Viewer job fails with 404 deployment error if missing. |
| **Static Verification** | Basic lint/synthesis | `py/verify_cicd_config.py` + unit tests | `make check` executes full Python test suite | Prevents workflow configuration regression. |

---

## 4. Recommendations for Roadmap Harmonization

1. **Update `ROADMAP.md` Phase 1.1:**
   - Change `pdk: sg13g2` reference to `pdk: ihp-sg13g2`.
   - Explicitly cite the `@ttihp26b` action tag requirement for all `tt-gds-action` workflows.
2. **Expand `ROADMAP.md` Phase 1.1 with Pages Deployment Prerequisites:**
   - Add a note regarding repository settings configuration (GitHub Pages source set to `GitHub Actions` and OIDC permission requirements).
3. **Update `ROADMAP.md` Phase 1.3 Verification Description:**
   - Reference `py/verify_cicd_config.py` and `py/test_verify_cicd_config.py` under automated checks.
4. **Maintain `CICD_FIX_ROADMAP.md` as Operational Reference:**
   - Retain `CICD_FIX_ROADMAP.md` for step-by-step CI/CD troubleshooting and monitoring while updating `ROADMAP.md` for macro-level consistency.
