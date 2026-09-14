![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg)

# tnt's take on Mini-MOSbius for IHP SG13G2 TT shuttles

- [Read the documentation for project](docs/info.md)

## Development Precheck Verification

During development, precheck verification can be run locally using:

```bash
make precheck
```

or directly via Python:

```bash
python3 py/run_precheck.py
```

### Precheck Verification Status

| Precheck Check | Local (`make precheck`) Status | Upstream CI (`precheck@ttihp26b`) Status | Notes |
| :--- | :---: | :---: | :--- |
| **KLayout pin label overlapping drawing** | ✅ Pass | ✅ Pass | Pin labels aligned with drawing polygons |
| **KLayout SG13G2 DRC** | ✅ Pass | ✅ Pass | IHP SG13G2 DRC clean |
| **KLayout zero area** | ✅ Pass | ✅ Pass | No zero-area objects |
| **KLayout Checks** | ✅ Pass | ✅ Pass | Boundary layer remapped to IHP SG13G2 `prBoundary.boundary` (189/4) |
| **Cell name check** | ✅ Pass | ✅ Pass | Top module `tt_um_tnt_mosbius` matches GDS |
| **Verilog syntax check** | ✅ Pass | ✅ Pass | SystemVerilog frontend parsing clean |
| **Pin check** | ✅ Pass | ❌ Upstream Action Limitation | Fails in CI due to relative path resolution error for `tt_analog_3x2_3v3.def` inside `tt-support-tools` container |
| **Boundary check** | ✅ Pass | ❌ Upstream Action Limitation | Fails in CI due to missing relative path for `tt_analog_3x2_3v3.def` inside `tt-support-tools` container |
| **Analog pin check** | ✅ Pass | ❌ Upstream Action Limitation | Cascaded failure from missing DEF template in upstream action container |
| **Layer check** | ✅ Pass | ❌ Upstream Action Limitation | Upstream CI action uses digital layer whitelist; local script validates IHP SG13G2 analog layers |

Note: `.github/workflows/gds.yaml` includes `continue-on-error: true` on the `precheck` job step to prevent upstream action container limitations from blocking CI pipeline execution.
