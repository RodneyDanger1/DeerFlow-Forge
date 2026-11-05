# Control traces and confirmed defects

| ID | Tab | Symptom | Root | Status |
|---|---|---|---|---|
| T1 | Board and Routes | Displayed `vectorcraft-cli trace --input`, `--svg-out`, old `--out-dir`, and knitwear `--palette-limit` although the repaired `routes.py` uses `run --cmd/--export` | `src/lib/blueprint/model.ts` was hand-copied from the pre-repair route table and never updated | FIXED |
| T2 | Board and Routes | Apparel distress step read `{work}/apparel/trimmed.png`, but the new trim step writes `{work}/trimmed.png` | `routes.py` effectcraft step + model template still used the old output directory | FIXED |
| T3 | Sources | New `deploy/craft-launchers/*` and DeerFlow MCP example were absent from the source registry | `src/lib/blueprint/sources.ts` imported only the old `craft-bin` stubs | FIXED |
| T4 | Playbook | Image-trace example still showed the old `--commands` JSON format; skill count said 22 | Static `playbook-view.tsx` content not updated after Phase 0 | FIXED |

## Trace ladder

**T1**
1. Render: Board HTML showed `vectorcraft-cli trace … --input`.
2. Handler: `Board` computes `buildPlan` from `model.ts`.
3. Shared model: `buildPlan` hard-coded the old trace array; `FAMILIES` contained old trim/knitwear commands.
4. Root: model.ts stale versus `routes.py`; the parity test was also pinning the stale raw-form behavior.
5. Fix: measured contracts in `model.ts`; parity test now compares rendered `routes.py` argv to the rendered board plan.
6. Proof: model tests 6/6, parity 3/3, typecheck 0, `npm test` 65/65, browser smoke ok.

**T2**
1. Render: apparel distress command showed `.../apparel/trimmed.png`.
2. Route: `routes.py` effectcraft argv still pointed at `{work}/apparel/trimmed.png` after trim moved to `{work}/trimmed.png`.
3. Root: two edge contracts drifted; parity passed only because both sides were stale.
4. Fix: route + model now use `{work}/trimmed.png`; model test asserts trim `--out` equals distress `--input`.
5. Proof: model test 6/6; parity 3/3; browser Board no longer shows the old path.

**T3**
1. Render: Sources showed `craft-bin` stubs but no launcher files.
2. Handler: `SourcesView` only shows `SOURCES`.
3. Root: `sources.ts` registry not updated when `craft-launchers/` and the MCP example were added.
4. Fix: import/list both launchers and the MCP example.
5. Proof: typecheck 0, build 0, browser Sources heading `deploy/craft-launchers/vectorcraft-cli`, 34 source buttons.

**T4**
1. Render: Playbook code block still used `{"command":"select.all"}` and `--commands`.
2. Handler: static content, no data source.
3. Root: copy was not updated after the measured `run` contract.
4. Fix: measured run example; 22 → 39 skills.
5. Proof: typecheck/build 0; browser Playbook all three jumps work, no errors.

## Negative paths tested

- All five family selections; all five accordions.
- `Docker sandbox` toggle changes to native `nice -n 10`.
- `Vector trace exits 1` produces a FAIL trace, raster fallback, and "Run again".
- Mobile Sources select exists; no overflow at 390×844.
- Copy writes clipboard (with permission) and Download yields `craft_stub.py`.
- No control was left unexercised except the mobile select's option-change action (select is present and options render).
