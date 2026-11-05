# W3-A recon — artifact verifier and gate-report parser

**Scope:** G3 verifier only. Critic and learning stay out of this step.

- **Target behavior today:** G0 artifacts and `trace_report.json` exist, but nothing converts a gate
  report + artifact bytes into a fail-closed verdict. A report can say `ok:true` while its
  `output_sha256` does not match the file, or while every check is non-applicable.
- **Entry point:** `research/eko-deerflow-agent/execution-wave/g0/trace_report.json` and
  `trace_master.png`; future caller is the Forge episode pipeline.
- **Tests:** real G0 pair must pass; tampered report hash, vacuous applicable count, failed check,
  missing artifact and wrong dimensions must fail. Run on staging with Pillow.
- **Data flow:** artifact path -> bytes/hash + IHDR/DPI; report -> applicable checks + failures +
  declared output hash; combine -> named verdict. Failure path: missing file -> `E_ARTIFACT_MISSING`.
- **Unknowns:** critic protocol and human-taste scoring (W3-B); retrieval/promotion (later).
- **Files:** `blueprint/files/forge_verifier.py`, `blueprint/files/tests/test_forge_verifier.py`.
- **Non-goals:** no production write, no rerun of Craft, no claim that report evidence replaces a gate.

## Implementation status

Done: 7/7 verifier tests on the real G0 pair; staging **104 pass/9 skip**. See
`execution-wave/20-W3A-VERIFIER.md`. Critic is W3-B; learning is later.
