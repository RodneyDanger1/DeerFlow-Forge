# Fix receipt

| File | Change | Evidence |
|---|---|---|
| `src/lib/blueprint/model.ts` | Measured trace/raster/trim argv, knit colour cap, truthful assumptions | `node --experimental-strip-types --test src/lib/blueprint/model.test.ts` → 6/6 |
| `src/lib/blueprint/model.test.ts` | New regression pins for trace, fallback, knit colours, trim, step adjacency, assumptions | same run |
| `src/components/forge/routes-view.tsx` | Trace label no longer says "no extra flags" when the measured contract has params | typecheck/browser |
| `scripts/blueprint-parity.test.mjs` | Compare rendered `routes.py` argv to rendered board plan; updated truth assertion | `node --test scripts/blueprint-parity.test.mjs` → 3/3 |
| `src/lib/blueprint/sources.ts` | Add two launchers + MCP example to Sources | typecheck/build/browser |
| `src/components/forge/playbook-view.tsx` | Measured run example; 39 skills | typecheck/build/browser |
| `blueprint/files/pod_pipeline/routes.py` | Distress step input `{work}/trimmed.png` | staging tests 53 passed/4 skipped; parity |
| `package.json` | Include `model.test.ts` in `npm test` | `npm test` → 65/65 |

**Commands**
- `npm run typecheck` → exit 0.
- `npm run lint` → 0 errors, 5 pre-existing warnings in research adapter files.
- `npm test` → 65 passed, 0 failed.
- `npm run build` → built; migrations skipped because `DATABASE_URL` unset.
- `node scripts/visual-console-smoke.mjs http://127.0.0.1:8080` → `ok: true`, zero console/page/request failures, desktop + mobile.
- Staging `pytest tests -q` → 53 passed, 4 skipped.

**Residual / unverified**
- The 4 staging tests skip because the staging test DB is not wired; they are not passes.
- Copy/Download were tested with a browser permission grant; a browser that blocks clipboard falls
  back to `execCommand` and can still fail silently (no user-facing error). This is a usability gap,
  not a shipped failure; not fixed here.
- No production deployment was made; the console is a viewer and does not execute the pipeline.
