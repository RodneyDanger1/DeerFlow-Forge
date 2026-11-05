# Post-review corrections (after independent reviews 13/14)

**Date:** 2026-11-05 · **Status:** corrections applied after the independent W1-C/G0 reviews.

| Review finding | Correction | Evidence |
|---|---|---|
| D1: G0 direct trace sizes were wrong in HEAD (958,860 / 1,618,404) | corrected to actual **979,800 / 1,572,959 B** | `11-G0-EVIDENCE.md`; artifact stdout |
| D2: `retyped_text_present` passed with `retype_boxes:0` (decorative pass) | `craft_trace.verify` now returns `applicable:false`, `pass:null`, `value:"not_requested"` when no retype is requested; `passed` only evaluates applicable checks; added regression test | `tools/craft_trace.py`; `tests/test_craft_trace.py`; real report regenerated |
| D3: MANIFEST omitted previews/tarball/itself | bundle cleaned; `MANIFEST.json` now covers **22 files** including 3 previews | `g0/MANIFEST.json` |
| D4: G0 prose omitted the direct PDF hash | added direct PDF hash and corrected report hash | `11-G0-EVIDENCE.md` |
| D5: execution provenance self-asserted only | **remains U**; no VPS access for the independent reviewer. Artifact consistency is PASS; origin is not proven independently | `14-G0-ARTIFACT-REVIEW.md` |
| Review 14 says “10/10” | historical report retained; current truth is **9/9 applicable + 1 not requested** | regenerated `trace_report.json` |

## Current measurements

- Staging suite: **54 passed, 4 skipped**.
- CraftTrace: exit 0, `ok:true`, `saved:true`, `applicable_checks:9`, `retyped:false`, `retype_boxes:0`.
- `trace_master.png` hash unchanged (`ab64aad7…`); `trace_report.json` new hash `c6719594…`.
- W1-C 39/39 remains valid; W2 not started because G0 provenance is U.
