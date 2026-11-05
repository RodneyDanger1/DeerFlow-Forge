# Fix receipt

| File | Change | Evidence |
|---|---|---|
| `src/lib/blueprint/model.ts` | Measured trace/raster/trim argv, knit colour cap, truthful assumptions | `node --experimental-strip-types --test src/lib/blueprint/model.test.ts` → 6/6 |
| `src/lib/blueprint/model.test.ts` | New regression pins for trace, fallback, knit colours, trim, step adjacency, assumptions | same run |
| `src/components/forge/routes-view.tsx` | Trace label no longer says "no extra flags" when the measured contract has params | typecheck/browser |
| `scripts/blueprint-parity.test.mjs` | Compare rendered `routes.py` argv to rendered board plan; updated truth assertion | `node --test scripts/blueprint-parity.test.mjs` → 3/3 |
| `src/lib/blueprint/sources.ts` | Add two launchers + MCP example to Sources | typecheck/build/browser |
| `src/components/forge/playbook-view.tsx` | Measured run example; 39 skills | typecheck/build/browser |
| `src/components/forge/copy-button.tsx` | Explicit `Copied` / `Copy failed` state instead of silent failure | denied-clipboard browser probe showed `Copy failed`; granted probe showed `Copied` |
| `blueprint/files/pod_pipeline/routes.py` | Distress step input `{work}/trimmed.png` | staging tests 53 passed/4 skipped; parity |
| `package.json` | Include `model.test.ts` in `npm test` | `npm test` → 65/65 |

**Commands**
- `npm run typecheck` → exit 0.
- `npm run lint` → 0 errors, 5 pre-existing warnings in research adapter files.
- `npm test` → 65 passed, 0 failed.
- `npm run build` → built; migrations skipped because `DATABASE_URL` unset.
- **Built-output correction:** plain `npm run build` produced the Vercel preset, while `.output` was a stale
  node-server build. Rebuilt with `NITRO_PRESET=node-server npm run build`; then
  `node .output/server/index.mjs` and smoke test → all five tabs, `ok:true`, no errors.
- `node scripts/visual-console-smoke.mjs http://127.0.0.1:8092` → `ok: true`, zero console/page/request
  failures, desktop + mobile.
- Copy success: granted clipboard → `Copied`, clipboard prefix `"""Product routing table...`.
- Copy failure: both clipboard paths denied → button `Copy failed`.
- Staging `pytest tests -q` → 53 passed, 4 skipped.

**Residual / unverified**
- The 4 staging tests skip because the staging test DB is not wired; they are not passes.
- Copy/Download were tested with a browser permission grant and with clipboard denied. Failure now
  shows `Copy failed`; no separate timeout/retry UI is provided.
- No production deployment was made; the console is a viewer and does not execute the pipeline.
