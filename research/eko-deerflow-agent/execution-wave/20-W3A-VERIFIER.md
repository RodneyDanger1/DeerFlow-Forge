# W3-A â€” artifact verifier and gate-report parser

**Date:** 2026-11-05 Â· **Scope:** G3 verifier only; local source, no production.
Recon: `docs/W3A-RECON.md` Â· Gate: `docs/W3A-GATE1.md`.

## Added

| File | Purpose |
|---|---|
| `blueprint/files/forge_verifier.py` | fail-closed PNG hash/IHDR/DPI inspector + gate-report parser + CLI (`pass` exit 0 / `fail` exit 1) |
| `blueprint/files/tests/test_forge_verifier.py` | 8 tests against the real G0 artifact/report |

Checks:
- artifact exists, non-zero bytes, readable PNG, positive dimensions;
- actual SHA-256 equals `report.output_sha256`;
- `ok` and `saved` are both true;
- every applicable check passes; non-applicable checks are ignored;
- `applicable_checks` equals the computed applicable count and is **not zero**;
- every check entry is an object; malformed entries return `E_REPORT_INVALID`;
- optional expected dimensions and DPI (300 Â± 0.01).

Named failures: `E_ARTIFACT_MISSING`, `E_ARTIFACT_EMPTY`, `E_ARTIFACT_UNREADABLE`,
`E_ARTIFACT_FORMAT`, `E_REPORT_INVALID`, `E_GATE_FAILED`, `E_ARTIFACT_HASH_MISMATCH`,
`E_GATE_COUNT_MISMATCH`, `E_GATE_VACUOUS`, `E_GATE_CHECK_FAILED`, `E_DIMENSION_MISMATCH`,
`E_DPI_MISMATCH`, `E_PARAM_REJECTED`.

## Proof

```text
python -m unittest -v tests.test_forge_verifier
Ran 8 tests ... OK

# CLI positive
forge_verifier.py --artifact trace_master.png --report trace_report.json \
  --expected-px 1500x1800 --expected-dpi 300
{"ok": true, "verdict": "pass", "applicable_checks": 9, "artifact": {"sha256": "ab64aad7â€¦", ...}}
exit=0

# CLI negative: report hash tampered
{"ok": false, "verdict": "fail", "code": "E_ARTIFACT_HASH_MISMATCH", ...}
exit=1

# staging suite with the real G0 bundle mounted
FORGE_G0_DIR=/opt/pod-pipeline-staging/data/staging/g0 pytest tests -q
112 passed, 4 skipped
```

The 9 skips remain the DB/e2e tests without `FORGE_TEST_DSN`; the verifier tests skip when
`FORGE_G0_DIR` is absent, rather than silently passing.

## Not done / unverified

- Critic (blind critique/crop grounding) is **not implemented**; W3-B.
- No episode ledger write of the verdict yet; verifier is a pure consumer.
- No production service/systemd wiring.
- Does not replace `craft_trace`; it independently checks its report and artifact.
- No real image outside the G0 pair was exercised.


