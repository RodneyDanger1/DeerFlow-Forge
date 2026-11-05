# Execution Wave / 01 — Craft Path Repair Plan (GAP-BIN · GAP-ARGV · GAP-MCP)

**Owner:** `stack-vps-auditor` · **Task:** `task-8` (completed, revision 3) · **Prepared:** 2026-11-05, 10:32–10:48 America/Chicago = 16:32–16:48 UTC
**Predecessor evidence:** [`../wave2/01-STACK-VPS.md`](../wave2/01-STACK-VPS.md) + [`01-VPS-FACTS.json`](../wave2/01-VPS-FACTS.json) — this document **starts** from GAP-BIN / GAP-ARGV / GAP-MCP and does not re-audit the stack.
**Mutation policy:** **PLAN ONLY.** No production file, config, container, service or database was edited to produce this document. Every probe wrote exclusively to `/tmp` on the host (`/tmp/audit_probe*.png`, `/tmp/audit_traced.{svg,pdf}`, `/tmp/audit_pc*.png`, `/tmp/audit_trim_out.png`, `/tmp/audit_sized.png`, `/tmp/audit_from_svg.png`, `/tmp/audit_svg_trim.png`, `/tmp/audit_traced.svg`, `/tmp/nodir/`, `/tmp/vcnest/`). Those are scratch artefacts and carry no production meaning.

**Evidence labels:** `VERIFIED` = observed in this session's command output · `READ` = file:line in repo/host · `EXPECTED` = predicted output of a *planned* command (not yet run) · `UNVERIFIED` = cannot be proven with current access.

---

## 0. What this plan does and does not cover

| In scope | Out of scope (other task / blocked) |
|---|---|
| Replace the 5 `exit 127` shims with absolute, version-pinned launchers (GAP-BIN) | Obtain DesignCraft / EffectCraft / FilmCraft vendor binaries (GAP-TOOLS — no artefact exists on this host) |
| Rewrite `routes.py` argv to the **verified** VectorCraft 0.21.1 / PhotoCraft 0.20.2 contracts (GAP-ARGV) | Filling `products.json` Fourthwall template ids (GAP-PUBLISH) |
| Register VectorCraft + PhotoCraft MCP stdio servers in DeerFlow (GAP-MCP) | Experience-ledger / eval / learning loop (GAP-STATE, GAP-LEARN) |
| Preflight refusal that names the missing tool, plus tests and rollback | Visual critic / GUI automation (GAP-GUI — headless only) |

**Hard boundary:** after this plan is executed, **only** the `apparel` route can advance past both craft steps, and even that route stops at `effectcraft_distress` because EffectCraft does not exist. The plan deliberately turns that into a *fast, named* refusal instead of a 127-exit mystery. No route becomes publishable until GAP-TOOLS and GAP-PUBLISH are closed.

---

## 1. Verification baseline gathered for this plan (all `VERIFIED` today, read-only)

These replace the `ASSUMPTION` contracts in `routes.py` with measured ones.

| Fact | Observed output |
|---|---|
| VectorCraft has **no** `trace` subcommand | `vectorcraft-cli: unknown subcommand 'trace'` |
| VectorCraft real batch contract | `vectorcraft-cli run [--in FILE] [--cmd ID [--params JSON] \| --commands FILE\|-]... [--export FILE]... [--scale N]` |
| Trace end-to-end **works** headless | `run --in /tmp/audit_probe2.png --cmd select.all --cmd imageTrace.make --params '{"params":{…}}' --cmd imageTrace.expand --export /tmp/audit_traced.svg` → `{"command":"imageTrace.make","result":{"anchors":4,"colors":1,"id":4,"paths":1,"warnings":[]},"step":"cmd"}` → `{"result":{"bytes":334,"format":"svg","path":"/tmp/audit_traced.svg","warnings":[]},"step":"export"}` (exit 0) |
| VectorCraft PDF export works | same run with `--export /tmp/audit_traced.pdf` → `{"format":"pdf","bytes":4626}` |
| VectorCraft does **not** create missing export directories | `vectorcraft-cli: step 1: export /tmp/vcnest/a/b.svg: … No such file or directory (os error 2)` |
| PhotoCraft real contract | `photocraft-cli run <FILE\|--new JSON> --cmd ID [--params JSON] --out FILE`; also `convert IN OUT`, `commands`, `info`, `batch`, `droplet`, `mcp`, `serve` |
| PhotoCraft opens **SVG** (traced art) | `photocraft-cli run /tmp/audit_traced.svg --cmd image.imageSize … --out …` → `{"command":"image.imageSize","result":{"height":1600,"width":1400}}` + `warning: 1 layer(s) flattened; layers, masks and blend modes are not kept` |
| PhotoCraft trim | `--cmd image.trim --params '{"basedOn":"transparent"}'` → `{"result":{"height":121,"width":161,"x":20,"y":20}}`, output RGBA 161×121 |
| PhotoCraft image size + 300 ppi | `--cmd image.imageSize --params '{"width":1400,"height":1600,"resolution":300,"resample":"lanczos"}'` → output 1400×1600 at dpi `(299.9994, 299.9994)` |
| PhotoCraft creates missing `--out` parent dirs | `--out /tmp/nodir/sub/out.png` → file written |
| Command-id discoverability | `vectorcraft-cli commands` → 918 ids (JSON); `photocraft-cli commands` → 965 ids (TSV) |
| Ids needed by the new routes exist | VC `select.all`, `imageTrace.make`, `imageTrace.expand`; PC `image.trim`, `image.imageSize`, `edit.convertToProfile`, `image.canvasSize`, `image.mode.rgb` |
| Parameter schemas | from the checked-in catalogue `blueprint/files/skills/artcraft-command-atlas/references/catalogues/photocraft-commands.json` (valid JSON, 965 entries, per-id `params` strings) |
| Binaries are container-compatible | both ELF x86-64 dynamic, max `GLIBC_2.35`; gateway container is Debian 12 **glibc 2.36** → bind-mount viable (`ldd`: only `libgcc_s`, `libm`, `libc`) |
| `pod` user can execute the vendor binaries | `su -s /bin/sh pod -c '<vc> --version'` → `vectorcraft-cli 0.21.1` |
| Current shims still stubbed | `env -i PATH=/opt/pod-pipeline/bin:… /opt/pod-pipeline/bin/vectorcraft-cli --version` → `vectorcraft-cli: vendor binary not installed…` |
| MCP stdio flags | VC: `mcp [--connect ADDR \| --headless] [--automation-read-root DIR]… [--automation-write-root DIR]…`; PC: `mcp [--bridge ADDR] [--automation-read-root DIR]… [--automation-write-root DIR]…` (**no** `--headless` flag) |
| DeerFlow stdio MCP schema | `extensions_config.example.json`: `{enabled, type:"stdio", command, args:[], env:{}, tool_name_prefix, session_init_timeout, tool_call_timeout, description}` |
| Compose project identity | `project=deer-flow-dev`, config `/opt/deer-flow/docker/docker-compose-dev.yaml`, working dir `/opt/deer-flow/docker` |

---

## 2. Gap → repair map

| Gap (from wave2) | Repair action | Closes fully? |
|---|---|---|
| GAP-BIN — 5 shims exit 127 | **R1** absolute launchers + loud refusal stubs | Yes for VC/PC; DC/EC/FC become named refusals |
| GAP-ARGV — invented CLI contracts | **R2** route rewrite against measured contracts | Yes for the two installed tools |
| GAP-TOOLS — DC/EC/FC absent | **R3** preflight `E_TOOL_NOT_INSTALLED` (fail fast) | **No** — needs vendor artefacts |
| GAP-MCP — craft MCP unregistered | **R4** bind mounts + two stdio servers | Yes, pending runtime proof |
| — (no gap id) | **R5** tests: unit + real-binary marker + stub update | Gate for R1/R2 |
| GAP-SYNC — copy-deployed tree | **R6** staging-first rollout | Mitigated |
| — | **R7** rollback with exercised inverse | Gate |

---

## 3. R1 — Replace the shims (GAP-BIN)

### R1.1 Source of truth
Add a launcher directory to the repo: `blueprint/files/deploy/craft-launchers/`. The existing `deploy/craft-bin/*` stay as the *refusal* stubs for tools that are not installed. `READ` `blueprint/files/deploy/setup-pipeline.sh:88-90` currently installs a stub only when `bin/$tool` is missing — so re-running setup never overwrites a real launcher (good) but also never repairs one (this plan calls `install` explicitly).

### R1.2 File: `deploy/craft-launchers/vectorcraft-cli` (mode 0755)
```sh
#!/bin/sh
# Pinned absolute launcher — VectorCraft 0.21.1 (GAP-BIN repair).
BIN=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
if [ ! -x "$BIN" ]; then
  echo "E_TOOL_NOT_INSTALLED vectorcraft expected=$BIN" >&2
  exit 127
fi
exec "$BIN" "$@"
```
`deploy/craft-launchers/photocraft-cli` is identical with
`BIN=/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli` and `E_TOOL_NOT_INSTALLED photocraft`.

### R1.3 File: `deploy/craft-bin/{designcraft,effectcraft,filmcraft}-cli` (edit text only)
Replace the body's message with a named refusal so a run log says *which* tool and where the plan lives:
```sh
#!/bin/sh
echo "E_TOOL_NOT_INSTALLED ${0##*/} — vendor binary not present on this host; see research/eko-deerflow-agent/execution-wave/01-EXECUTION-REPAIR.md" >&2
exit 127
```
(Keep `set -e`-free POSIX, exit **127** so `runner.TRANSIENT_EXIT_CODES` at `runner.py:17` still treats it as non-retryable — 127 is not transient.)

### R1.4 setup-pipeline.sh patch (idempotent, `READ` `setup-pipeline.sh:88-90`)
```bash
for tool in vectorcraft-cli photocraft-cli designcraft-cli effectcraft-cli filmcraft-cli; do
  if [[ -x "$ROOT/deploy/craft-launchers/$tool" ]]; then
    install -m 0755 -o "$APP_USER" -g "$APP_GROUP" "$ROOT/deploy/craft-launchers/$tool" "$ROOT/bin/$tool"
  elif [[ ! -e "$ROOT/bin/$tool" ]]; then
    install -m 0755 "$ROOT/deploy/craft-bin/$tool" "$ROOT/bin/$tool"
  fi
done
```

### R1.5 Install on the VPS (production change — execute only in the rollout phase, R6)
```bash
install -d -m 0755 /opt/pod-pipeline/deploy/craft-launchers
# copy the two launchers + 3 refusal stubs from the staging tree
install -m 0755 -o pod -g pod /opt/pod-pipeline/deploy/craft-launchers/vectorcraft-cli  /opt/pod-pipeline/bin/vectorcraft-cli
install -m 0755 -o pod -g pod /opt/pod-pipeline/deploy/craft-launchers/photocraft-cli  /opt/pod-pipeline/bin/photocraft-cli
install -m 0755 -o pod -g pod /opt/pod-pipeline/deploy/craft-bin/designcraft-cli        /opt/pod-pipeline/bin/designcraft-cli
install -m 0755 -o pod -g pod /opt/pod-pipeline/deploy/craft-bin/effectcraft-cli        /opt/pod-pipeline/bin/effectcraft-cli
install -m 0755 -o pod -g pod /opt/pod-pipeline/deploy/craft-bin/filmcraft-cli          /opt/pod-pipeline/bin/filmcraft-cli
```
### R1.6 Verify (expected outputs)
```bash
/opt/pod-pipeline/bin/vectorcraft-cli --version            # EXPECTED: vectorcraft-cli 0.21.1
/opt/pod-pipeline/bin/photocraft-cli --version             # EXPECTED: photocraft-cli 0.20.2 (7c12f6471, 2026-11-05)
su -s /bin/sh pod -c '/opt/pod-pipeline/bin/vectorcraft-cli --version'   # EXPECTED: same version (pod can exec)
/opt/pod-pipeline/bin/designcraft-cli; echo "exit=$?"      # EXPECTED: E_TOOL_NOT_INSTALLED designcraft-cli … exit=127
env -i PATH=/opt/pod-pipeline/bin:/usr/local/bin:/usr/bin:/bin HOME=/tmp LANG=C.UTF-8 TMPDIR=/tmp QT_QPA_PLATFORM=offscreen \
  /opt/pod-pipeline/bin/vectorcraft-cli --version          # EXPECTED: vectorcraft-cli 0.21.1  (runner's minimal env)
```
### R1.7 Failure cases
| Symptom | Cause | Action |
|---|---|---|
| `vectorcraft-cli: vendor binary not installed` | launcher not installed (setup-pipeline no-op because `bin/` existed) | run the explicit `install` lines in R1.5 |
| `E_TOOL_NOT_INSTALLED vectorcraft expected=/opt/craft/...` | tarball removed / path version bumped | `ls /opt/craft/vectorcraft/` and re-pin the path in the launcher |
| `Permission denied` on exec | `/opt/craft` payload ownership (uid 1001) lost | `chmod 0755` the binary; verify with `su -s /bin/sh pod -c …` |
| Exit 126 instead of 127 | launcher lost its `+x` | `chmod 0755 /opt/pod-pipeline/bin/*-cli` |

---

## 4. R2 — Rewrite `routes.py` argv to the real contracts (GAP-ARGV)

All edits are in `blueprint/files/pod_pipeline/routes.py` (deployed copy byte-identical — `sha256 298ecfac…`, see wave2 §12). The file header already promises it is "the ONLY place that knows the Craft CLI command lines" (`routes.py:1-3`) — this repair restores that promise.

### R2.1 Trace step — replace `routes.py:73-82`
```python
TRACE_PARAMS = (
    '{{"params":{{"mode":"{cfg[trace_mode]}","palette":"{cfg[trace_palette]}",'
    '"colors":{cfg[trace_colors]},"paths":{cfg[trace_paths]},"corners":{cfg[trace_corners]},'
    '"noise":{cfg[trace_noise]},"ignoreWhite":true,"method":"abutting","fills":true,'
    '"strokes":false,"shapes":false,"autoGrouping":false,"gradients":false}}}}'
)


def trace_step(route: Route) -> Step:
    """VectorCraft image trace. Contract VERIFIED against vectorcraft-cli 0.21.1
    (`run --in … --cmd imageTrace.make --params … --cmd imageTrace.expand --export …`)."""
    return Step(
        name="vector_trace",
        module="vectorcraft",
        argv=("vectorcraft-cli", "run", "--in", "{src}",
              "--cmd", "select.all",
              "--cmd", "imageTrace.make", "--params", TRACE_PARAMS,
              "--cmd", "imageTrace.expand",
              "--export", "{work}/traced.svg",
              "--export", "{work}/traced.pdf"),
        outputs=("{work}/traced.svg", "{work}/traced.pdf"),
    )
```
Why the escaped braces: `render()` (`routes.py:202-207`) uses `str.format_map`, so `{{`/`}}` are the only way to carry literal JSON through a template. A unit test (R5.1) pins this. The mechanism itself is proved (system Python 3.14, this workstation): `'{{"params":{{"colors":{cfg[trace_colors]}}}}}'.format_map({"cfg":{"trace_colors":12}})` → `{"params":{"colors":12}}`, and `json.loads` accepts it. A **missing** key raises `KeyError`, which `render()` converts to a named `ConfigError` (`routes.py:202-207`) — so a bad `products.json` still refuses by name rather than emitting broken JSON.

Route knobs, added to `DEFAULT_CFG` (`routes.py:24-49`) — values are the `craft_trace.py` defaults, which were exercised on this host:
```python
DEFAULT_CFG["apparel"].update(trace_mode="color", trace_palette="limited",
                              trace_colors=12, trace_paths=65, trace_corners=45, trace_noise=16)
# knitwear: palette_limit is a hard factory cap -> trace_colors = palette_limit=6,
# trace_palette="limited"; other trace_* inherit.
```
`trace_extra` (`routes.py:65, 120`) becomes unused and must be deleted from `Route` and from `trace_step` — `--palette-limit` is **not** a `vectorcraft-cli` flag (the 6-colour cap now travels inside the JSON `colors`).

### R2.2 Raster fallback — replace `routes.py:84-93`
```python
def raster_fallback_step() -> Step:
    """Tier-1 fallback when the trace exits 1: PhotoCraft resample, no tracing.
    Contract VERIFIED against photocraft-cli 0.20.2."""
    return Step(
        name="raster_fallback",
        module="photocraft",
        argv=("photocraft-cli", "run", "{src}",
              "--cmd", "image.imageSize",
              "--params", '{{"resolution":{fallback_dpi},"resample":"lanczos"}}',
              "--cmd", "edit.convertToProfile", "--params", '{{"profile":"srgb"}}',
              "--out", "{work}/raster.png"),
        outputs=("{work}/raster.png",),
    )
```
`{work}/raster/*.png` cannot survive: **VectorCraft** refuses missing directories and a flat name is simpler. (PhotoCraft itself does create parents — verified — but this step is contract-checked in R5.1 for both shapes, so keep it flat and directory-independent.)

### R2.3 Apparel trim — replace `routes.py:102-108`
```python
Step("photocraft_trim", "photocraft",
     ("photocraft-cli", "run", "{art}",
      "--cmd", "image.trim", "--params", '{{"basedOn":"transparent"}}',
      "--cmd", "image.imageSize",
      "--params", '{{"width":{cfg[trim_width_px]},"height":{cfg[trim_height_px]},'
                  '"resolution":300,"resample":"lanczos"}}',
      "--cmd", "edit.convertToProfile", "--params", '{{"profile":"srgb"}}',
      "--out", "{work}/trimmed.png"),
     ("{work}/trimmed.png",)),
```
`{art}` is `traced.svg` on the happy path — **verified** that PhotoCraft opens an SVG (flatten warning appears on stderr and is benign for a flat trace). Add to `DEFAULT_CFG["apparel"]`: `trim_width_px=4200, trim_height_px=4800` (from the existing `max_px` print area).

### R2.4 Steps that stay blocked (do **not** invent substitutes)
`effectcraft_distress` (`routes.py:109-113`), `designcraft_stitch_matrix` (`122-128`), `designcraft_template` (`138-143`), `designcraft_wrap_tile` + `effectcraft_cylinder_taper` (`153-162`), `designcraft_cover` + `filmcraft_reel` (`171-183`) keep their argv but now fail through R3's preflight with `E_TOOL_NOT_INSTALLED <module>`. Two conditions on keeping them:
- `test_routes.py:40-47` (`test_knitwear_without_a_grid_refuses_by_name`) reads `ROUTES["knitwear"].steps[0]` and expects `render_argv` to raise `"rendered empty"` — the knitwear step must keep `{cfg[knit_grid]}` **and** its `--grid-scale` flag for that test to stay meaningful. Leave `designcraft_stitch_matrix` untouched.
- Do **not** try to express designcraft/effectcraft/filmcraft work as PhotoCraft filters. That is a product-semantics change (distress grit, stitch matrices, cylinder warp, mp4 reels), not a repair, and would ship fabricated output — forbidden by the project contract.

### R2.5 Verify (offline, no binaries needed)
```bash
cd /opt/pod-pipeline-staging && .venv/bin/python - <<'PY'
from pod_pipeline.routes import ROUTES, merged_cfg, render_argv, trace_step, raster_fallback_step
apparel = merged_cfg("apparel", {})
v = {"src": "/in.png", "art": "/in.png", "work": "/w", "build": "/b",
     "run_id": "r", "asset_id": 1, "fallback_dpi": 600, "cfg": apparel}
print(render_argv(trace_step(ROUTES["apparel"]), v))
print(render_argv(raster_fallback_step(), v))
print(render_argv(ROUTES["apparel"].steps[0], v))
PY
```
`EXPECTED` (abridged):
```
['vectorcraft-cli', 'run', '--in', '/in.png', '--cmd', 'select.all', '--cmd', 'imageTrace.make',
 '--params', '{"params":{"mode":"color","palette":"limited","colors":12,"paths":65,"corners":45,
  "noise":16,"ignoreWhite":true,"method":"abutting","fills":true,"strokes":false,"shapes":false,
  "autoGrouping":false,"gradients":false}}', '--cmd', 'imageTrace.expand',
 '--export', '/w/traced.svg', '--export', '/w/traced.pdf']
['photocraft-cli', 'run', '/in.png', '--cmd', 'image.imageSize', '--params', '{"resolution":600,
  "resample":"lanczos"}', '--cmd', 'edit.convertToProfile', '--params', '{"profile":"srgb"}',
 '--out', '/w/raster.png']
['photocraft-cli', 'run', '/in.png', '--cmd', 'image.trim', '--params', '{"basedOn":"transparent"}',
 '--cmd', 'image.imageSize', '--params', '{"width":4200,"height":4800,"resolution":300,
  "resample":"lanczos"}', '--cmd', 'edit.convertToProfile', '--params', '{"profile":"srgb"}',
 '--out', '/w/trimmed.png']
```
Then the real-binary gate (R5.3) — that is the only thing that proves the contract, not this dump.

### R2.6 Failure cases
| Symptom | Cause | Action |
|---|---|---|
| `unknown subcommand 'trace'` survives | old `routes.py` still imported (pod-mcp holds the module) | `systemctl restart pod-mcp.service` |
| `step 0: unexpected argument '--in'` | VectorCraft version ≠ 0.21.1 | re-read `vectorcraft-cli run --help`; pin the version in the launcher comment |
| `step 1: export …: No such file or directory (os error 2)` | export path's parent missing (VC creates nothing) | keep exports directly under `{work}`/`{build}` (orchestrator mkdirs both: `orchestrator.py:_execute`) |
| `E_FONT_MISSING`-style errors from a crafted path | not applicable here — routes no longer render text | — |
| Trace produces empty SVG | source has no opaque pixels (wholly transparent) | asset-side quarantine is correct; do not "fix" routes |
| `imageTrace.make` params rejected | `--params` JSON malformed by a bad `{cfg[...]}` value (empty string) | `render_argv` already raises `ConfigError` on an empty token (`routes.py:209-214`) |

---

## 5. R3 — Fast, named refusal for absent tools (GAP-TOOLS containment)

Without this, a run spends a step insertion, spawn, `nice` and a 127 exit to learn that EffectCraft is missing — for **every** route, on **every** attempt.

Patch `orchestrator._run_step` (`orchestrator.py:167-177`), immediately after `argv = render_argv(step, ctx.vars)` (`:170`):
```python
tool_bin = Path(s.bin_dir) / argv[0] if "/" not in argv[0] else Path(argv[0])
if "/" not in argv[0] and not os.access(tool_bin, os.X_OK):
    raise PipelineError(f"E_TOOL_NOT_INSTALLED {step.module} ({argv[0]} not executable in {s.bin_dir})")
```
Behaviour: deterministic, so `_run_step` must surface it *before* `start_step` (no retry; `max_attempts` untouched). Expected API outcome: `run_pipeline` summary `ok:false`, `error:"E_TOOL_NOT_INSTALLED effectcraft (effectcraft-cli not executable in /opt/pod-pipeline/bin)"`, `processing_jobs.status=failed`, `ingested_assets.status=failed`.

`EXPECTED` log line for the stationery route:
```
E_TOOL_NOT_INSTALLED designcraft (designcraft-cli not executable in /opt/pod-pipeline/bin)
```
Failure cases: a genuine 127 from a *real* binary (bad shebang inside a wrapper) no longer reaches `_run_step`'s exit-code path — acceptable, because the message names the step; keep the exit-code path for runtime failures.

---

## 6. R4 — Register the craft MCP servers in DeerFlow (GAP-MCP)

Target: DeerFlow's agent can call VectorCraft / PhotoCraft tools directly, with no bespoke bridge code.

### R4.1 Create shared roots on the host
```bash
install -d -m 0775 /opt/pod-pipeline/craft-agent
install -d -m 0775 /opt/pod-pipeline/craft-agent/out
```
`/opt/pod-pipeline/craft-agent` does not exist today (`ls` → No such file or directory).

### R4.2 Compose: bind mounts on the gateway (`READ` `/opt/deer-flow/docker/docker-compose-dev.yaml:213` = `volumes:`)
Insert after line **230** (`- gateway-uv-cache:/root/.cache/uv`):
```yaml
      # DeerFlow Forge craft tooling (GAP-MCP repair): binaries + artefact roots
      - /opt/craft:/opt/craft:ro
      - /opt/pod-pipeline/sandbox:/opt/pod-pipeline/sandbox:ro
      - /opt/pod-pipeline/build:/opt/pod-pipeline/build:ro
      - /opt/pod-pipeline/craft-agent:/opt/pod-pipeline/craft-agent:rw
```
Container user is `uid=0(root)` and the binaries need only glibc ≤ 2.35 (container has 2.36) — `VERIFIED` by ELF/`ldd` inspection, not yet by execution.

### R4.3 `extensions_config.json` — add two stdio servers, keep `forge` untouched
Backup first: `cp -p /opt/deer-flow/extensions_config.json /opt/deer-flow/extensions_config.json.bak-before-craft-mcp-$(date -u +%Y%m%dT%H%M%SZ)` (matching the existing `…bak-before-forge-mcp` convention).
```json
"vectorcraft": {
  "enabled": true,
  "type": "stdio",
  "command": "/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli",
  "args": ["mcp", "--headless",
           "--automation-read-root", "/opt/pod-pipeline/sandbox",
           "--automation-read-root", "/opt/pod-pipeline/build",
           "--automation-write-root", "/opt/pod-pipeline/craft-agent"],
  "tool_name_prefix": true,
  "session_init_timeout": 120,
  "tool_call_timeout": 600,
  "description": "VectorCraft 0.21.1 headless engine (draw, trace, export) for DeerFlow Forge"
},
"photocraft": {
  "enabled": true,
  "type": "stdio",
  "command": "/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli",
  "args": ["mcp",
           "--automation-read-root", "/opt/pod-pipeline/sandbox",
           "--automation-read-root", "/opt/pod-pipeline/build",
           "--automation-write-root", "/opt/pod-pipeline/craft-agent"],
  "tool_name_prefix": true,
  "session_init_timeout": 120,
  "tool_call_timeout": 600,
  "description": "PhotoCraft 0.20.2 headless engine (raster prep, export) for DeerFlow Forge"
}
```
Differences that matter (`VERIFIED` from `--help`): VectorCraft takes `--headless`; PhotoCraft has **no** `--headless` flag (headless is its default, `--bridge` is the alternative). Both accept repeatable `--automation-read-root` / `--automation-write-root`; an omitted root **denies** that direction, so both lists must be present. `tool_name_prefix: true` avoids collisions between the two servers' similarly-named commands.

### R4.4 Apply and verify
```bash
cd /opt/deer-flow/docker
docker compose -p deer-flow-dev -f docker-compose-dev.yaml up -d gateway
```
`EXPECTED`: `Container deer-flow-gateway  Recreating` → `Started` (observed project/config/workdir labels above, so `-p deer-flow-dev` reproduces the existing project rather than creating a second one).
```bash
docker inspect deer-flow-gateway --format '{{range .Mounts}}{{.Source}} {{end}}' | tr ' ' '\n' | grep -E 'craft|sandbox|build'
# EXPECTED: /opt/craft /opt/pod-pipeline/sandbox /opt/pod-pipeline/build /opt/pod-pipeline/craft-agent
docker exec deer-flow-gateway /opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli --version
# EXPECTED: vectorcraft-cli 0.21.1   (proves glibc 2.36 compatibility inside the container)
docker exec deer-flow-gateway /opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli --version
# EXPECTED: photocraft-cli 0.20.2 (7c12f6471, 2026-11-05)
curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:2026/     # EXPECTED: 200|30x (gateway up)
```
Final proof is a DeerFlow agent turn whose tool list contains `vectorcraft_*` / `photocraft_*` entries — `UNVERIFIED` until an agent run is made; the Forge HTTP server (`mcpServers.forge`) must keep working (`tools/list` still returns its 3 tools).

### R4.5 Failure cases
| Symptom | Cause | Action |
|---|---|---|
| gateway restart loops / `exec format error` | bind mount path wrong (typo in version dir) | `docker logs deer-flow-gateway --tail 50`; fix path |
| `GLIBC_2.36 not found` inside container | some future craft build needs > 2.36 | revert R4.2/R4.3; use a host-side bridge (see R4.6) |
| Agent sees 0 craft tools | entry JSON invalid (trailing comma) or `enabled:false` | `python3 -c "import json;json.load(open('/opt/deer-flow/extensions_config.json'))"` |
| Tool calls fail `permission denied` on write root | `/opt/pod-pipeline/craft-agent` not 0775 or container writes outside mounted root | `chmod -R 0775 /opt/pod-pipeline/craft-agent` |
| Existing `forge` tools disappear | JSON edited destructively | restore the `.bak-before-craft-mcp-*` file and restart |
| In-flight agent runs killed by restart | compose recreate | do it when `deerflow.db runs = 0` (true today: `runs 0`) |

### R4.6 Deferred alternative (do not implement in this plan)
If container exec of the bind-mounted binaries fails, run the MCP servers **on the host** and expose them over HTTP. That needs a new stdio↔streamable-HTTP bridge (the repo's `deploy/mcp-stdio.mjs` is client-side, not server-side) — new code, new tests, new failure surface. Recorded, not planned.

---

## 7. R5 — Tests (gate before any rollout)

### R5.1 New: `tests/test_route_argv_contracts.py` (pure, no DB, no binaries)
- Asserts the exact rendered argv for `trace_step`, `raster_fallback_step`, `ROUTES["apparel"].steps[0]` (the three lists in R2.5). Pins the escaped-brace JSON: `render_argv` output must be parseable by `json.loads` for every `--params` token.
- Asserts every `--cmd <id>` belongs to the checked-in catalogue:
  - VectorCraft: `skills/artcraft-command-atlas/references/catalogues/vectorcraft-commands.json` (918 ids)
  - PhotoCraft: `skills/artcraft-command-atlas/references/catalogues/photocraft-commands.json` (965 ids, valid JSON `READ`)
  Implementation: walk `render_argv` for every route, collect `--cmd` values, assert membership; assert each step's `module` maps to an expected binary name.
- Asserts no `Route.trace_extra` attribute remains (`AttributeError` guard) so R2.1's deletion cannot half-land.
- Keeps `test_routes.py:40-47` green: knitwear step[0] still renders empty without `knit_grid`.

### R5.2 Update `tests/stubs/craft_stub.py` (required — integration tests call the stubs)
`READ` `craft_stub.py:72-80`: the VectorCraft branch asserts `sys.argv[1] == "trace"` and requires `--input/--svg-out/--pdf-out`. New branch:
```python
if tool == "vectorcraft-cli":
    assert sys.argv[1] == "run", f"vectorcraft-cli needs 'run', got {sys.argv[1:]}"
    code = int(os.environ.get("STUB_VECTOR_EXIT", "0"))
    if code:
        print("ERROR: trace failed: path simplification diverged", file=sys.stderr)
        sys.exit(code)
    need(a, "--in")
    exports = a.get("--export") or []
    if not exports:
        print("ERROR: stub requires --export", file=sys.stderr); sys.exit(64)
    for target in exports:
        p = Path(target); p.parent.mkdir(parents=True, exist_ok=True)
        if p.suffix == ".svg":
            p.write_text("<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10'/>")
        else:
            p.write_bytes(PDF)
```
`READ` `craft_stub.py:81-91` PhotoCraft branch requires `--out-dir/--input/--target-dpi/--dimensions`; new branch:
```python
elif tool == "photocraft-cli":
    argv_all = sys.argv[1:]
    positional = [t for t in argv_all if not t.startswith("--")]
    src = next((t for t in positional if not t.startswith("{")), None)  # file arg, if present
    cmds = a.get("--cmd") or []
    out = need(a, "--out")
    if "image.trim" in cmds:
        art(out)
    else:
        art(out, size=(600, 750))
```
(designcraft/effectcraft/filmcraft branches unchanged — `craft_stub.py:92-139`.)
`conftest.py:26 CRAFT_TOOLS` and `conftest.py:68 stubs_env` need no change.

### R5.3 New marker test: `tests/test_craft_binaries.py` (real binaries; skips when absent)
```python
VC = Path("/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli")
pytestmark = pytest.mark.skipif(not VC.is_file(), reason="VectorCraft not installed")
```
- Builds a 96×96 RGBA fixture (opaque square, like the probe), copies the *rendered* `trace_step` argv with `{src}`→fixture, `{work}`→tmp_path, runs `subprocess.run(argv, timeout=600)`.
- Asserts: `returncode == 0`; both exports exist and are non-empty; stdout lines parse as JSON and include `"step":"export"` with `"format":"svg"`/`"format":"pdf"`.
- Same shape for `photocraft-cli` with `raster_fallback_step` and `ROUTES["apparel"].steps[0]` (real PhotoCraft opens the traced SVG — flatten warning allowed on stderr).
- Asserts the refusal path: run with `PATH=/nonexistent` and expect `E_TOOL_NOT_INSTALLED` from R3 before any spawn.

### R5.4 Commands + expected results (run in the staging tree first)
```bash
cd /opt/pod-pipeline-staging
.venv/bin/python -m pytest tests/ -q -k "not integration"      # EXPECTED: 27 passed, 5 skipped (4 integration + marker skips)
TEST_DATABASE_URL=postgresql://pod_app:<POD_DB_PASS>@127.0.0.1:5432/pod_test \
  .venv/bin/python -m pytest tests/ -q                          # EXPECTED: 31 passed
```
`UNVERIFIED` until run: the exact counts (README claims 31 pipeline tests / 27 pure + 4 integration; today's cache says `lastfailed = {}`). The staging DB `pod_test` is created/dropped by `tests/conftest.py:_create_schema` — **must be a staging DSN**, never `pod`.

---

## 8. R6 — Staging-first rollout (ordered; each step gated by the previous)

| # | Action | Verify |
|---|---|---|
| 0 | `systemctl is-active pod-mcp` and `psql count(*)` baseline | `active`; all tables 0 |
| 1 | `cp -a /opt/pod-pipeline /opt/pod-pipeline-staging` | `diff -rq` only `__pycache__` |
| 2 | Apply R1 + R2 + R3 + R5 **in staging** | R5.4 green; R2.5 dump matches |
| 3 | Snapshot production: `tar -C /opt -cpf /opt/backups/pod-pipeline-pre-repair-$(date -u +%Y%m%dT%H%M%SZ).tar pod-pipeline` | tar exists, non-zero |
| 4 | Install into production: `routes.py`, `orchestrator.py`, `runner.py` (if touched), `deploy/craft-launchers/*`, `bin/*`, `deploy/setup-pipeline.sh`, `tests/*` | `sha256sum` of installed files == staging |
| 5 | `systemctl restart pod-mcp.service` | `ActiveEnterTimestamp` fresh; `curl 127.0.0.1:8765/health` → `{"ok":true}` |
| 6 | Insert one account + one inbox asset; `trigger_pipeline_job` apparel | run reaches `photocraft_trim`, fails at `effectcraft_distress` with `E_TOOL_NOT_INSTALLED effectcraft`; `processing_jobs` shows 3 rows (orchestrator + trace + trim) with `succeeded` |
| 7 | R4 (MCP) | R4.4 commands + one agent turn listing craft tools |
| 8 | Record `product_state=draft`, `last_error` = the named refusal | no fake publish |

Step 6 is the first honest end-to-end proof this stack has ever had for craft execution. It **must** fail at `effectcraft_distress`; a green apparel run would mean a stub or a fabricated artefact slipped in.

---

## 9. R7 — Rollback (exact, and the inverse must be exercised once)

| Layer | Rollback command | Restores |
|---|---|---|
| Pipeline code | `install -m 0644 /opt/deerflow-forge/blueprint/files/pod_pipeline/{routes,orchestrator,runner}.py /opt/pod-pipeline/pod_pipeline/` then `systemctl restart pod-mcp.service` | byte-identical commit `32fc71f` content — `VERIFIED` by the 26/26 sha256 comparison in wave2 §12 |
| Launchers | `install -m 0755 -o pod -g pod /opt/deerflow-forge/blueprint/files/deploy/craft-bin/<tool> /opt/pod-pipeline/bin/<tool>` | the original `exit 127` shims |
| Tests | `install -m 0644 /opt/deerflow-forge/blueprint/files/tests/*.py /opt/pod-pipeline/tests/` | pre-repair tests |
| Fixtures | `install -m 0644 /opt/deerflow-forge/blueprint/files/tests/stubs/craft_stub.py /opt/pod-pipeline/tests/stubs/` | pre-repair stub |
| MCP | `cp -p /opt/deer-flow/extensions_config.json.bak-before-craft-mcp-<ts> /opt/deer-flow/extensions_config.json && cd /opt/deer-flow/docker && docker compose -p deer-flow-dev -f docker-compose-dev.yaml up -d gateway` | only `forge` registered |
| Compose | restore `docker-compose-dev.yaml` from the pre-edit backup, same `up -d gateway` | no craft mounts |
| Whole tree | `systemctl stop pod-mcp; tar -C /opt -xpf /opt/backups/pod-pipeline-pre-repair-<ts>.tar; systemctl start pod-mcp` | exact pre-repair tree |
| DB | **nothing to roll back** — no migration in this plan; `pod` DB stays 0 rows until step 6 inserts an account/asset, which is separately removable (`DELETE … RESTART IDENTITY`, only with owner approval) |

**Inverse exercise (project contract §20):** after R4 is verified, run the MCP rollback once (restore `.bak`, recreate gateway, confirm the craft tools are gone and `forge` still answers `tools/list`), then re-apply R4. Record both outcomes.

---

## 10. Consolidated failure matrix

| # | Symptom | Root cause | Fix |
|---|---|---|---|
| F1 | `vectorcraft-cli: unknown subcommand 'trace'` | R2 not installed, or pod-mcp still holding old module | R1/R2 install + `systemctl restart pod-mcp` |
| F2 | `E_TOOL_NOT_INSTALLED designcraft` | expected today (GAP-TOOLS) | stop; needs vendor artefacts |
| F3 | `vendor binary not installed` from a launcher | R1 not installed (`bin/` existed so setup no-op'd) | explicit `install` (R1.5) |
| F4 | `export … No such file or directory (os error 2)` | export path nested under a missing dir (VC creates none) | keep exports flat under `{work}`/`{build}` |
| F5 | Trace succeeds but trim fails on `.svg` | PhotoCraft version < 0.20.2 or flatten disabled | `photocraft-cli info <svg>`; pin 0.20.2 |
| F6 | `--params` JSON parse error in a step | an empty `{cfg[...]}` rendered into JSON | `render_argv` empty-token guard (`routes.py:209-214`) + R5.1 |
| F7 | craft tools absent from agent after R4 | gateway not recreated / JSON invalid / tool_server init timeout | `docker logs`, validate JSON, raise `session_init_timeout` |
| F8 | gateway cannot exec mounted binary | glibc > 2.36 in a future build | revert mounts; R4.6 host bridge |
| F9 | tests fail only in production tree | `.pytest_cache`/`POD_ROOT` confusion | always run R5.4 from `/opt/pod-pipeline-staging` |
| F10 | `E_TOOL_NOT_INSTALLED` for a tool that *is* installed | `bin_dir` wrong after `POD_ROOT` change | check `settings.bin_dir` = `/opt/pod-pipeline/bin` |

---

## 11. What remains unverified (explicit)

1. `UNVERIFIED` — **Runtime exec of craft binaries inside the gateway container.** glibc 2.35 ≤ 2.36 and `ldd` deps are present, but nothing has executed them there. R4.4 step 2 is the proof.
2. `UNVERIFIED` — **DeerFlow's stdio MCP path.** All working servers today are `type: http`; the stdio entries in `extensions_config` are disabled examples. First agent turn is the proof.
3. `UNVERIFIED` — **PhotoCraft MCP tool inventory.** VectorCraft's was handshaked (8 tools + resources); PhotoCraft's `mcp` was only `--help`-checked.
4. `UNVERIFIED` — **`--export` twice in one VectorCraft `run`.** SVG and PDF exports were each verified in isolation, not together.
5. `UNVERIFIED` — **SVG flatten fidelity.** PhotoCraft warns `1 layer(s) flattened; layers, masks and blend modes are not kept`; a traced SVG is a single flat layer, so this *should* be lossless, but no pixel comparison was made.
6. `UNVERIFIED` — **Test counts** after the rewrite (README's 31/207 numbers were never reproduced; caches only say `lastfailed = {}`).
7. `UNVERIFIED` — **EffectCraft / DesignCraft / FilmCraft availability anywhere** (absent from this host filesystem).
8. `UNVERIFIED` — **Publish path** still blocked: `products.json` template ids are `REPLACE_WITH_TEMPLATE_ID` (GAP-PUBLISH, out of scope).
9. `UNVERIFIED` — **Timing/latency** of craft steps under the 900 s `POD_STEP_TIMEOUT_S` and 2 vCPU / 8 GB host (probe fixtures were 96×96; real 4200×4800 work is untested).
10. `UNVERIFIED` — **Concurrency interaction**: `POD_MAX_CONCURRENCY=2` with headless craft processes on a 2-vCPU box (R4 in wave2).

---

## 12. Done definition for the execution wave

- [ ] R1 verified by the four `--version`/refusal commands in R1.6, including `su pod` and the minimal-env run.
- [ ] R2 verified by R2.5 dump **and** R5.3 real-binary test on `apparel` reaching `photocraft_trim`.
- [ ] R3 verified by an `E_TOOL_NOT_INSTALLED effectcraft` failure inside 1 s, no retry row.
- [ ] R4 verified by mounts + in-container `--version` + a live agent turn listing `vectorcraft_*`/`photocraft_*` tools.
- [ ] R5 verified by the two pytest commands with quoted counts.
- [ ] R7 inverse exercised once (MCP removal → `forge` intact → re-apply).
- [ ] No production DB rows fabricated; no publish attempted; no secret printed.

---

## 13. Commands run to produce this plan (all read-only; host writes only under `/tmp`)

`vectorcraft-cli --version|--help|commands|run --in|--export`, `photocraft-cli --version|--help|commands|convert|info|run|run --new|mcp --help|serve --help`, `file`, `ldd`, `strings | grep GLIBC_`, `su -s /bin/sh pod -c …`, `env -i … exec`, `PIL` fixtures via `/opt/pod-pipeline/.venv/bin/python`, `python3` JSON walks of both catalogues, `docker inspect` (mounts, project labels, container user/glibc), `docker exec … ld /usr/bin/…`, `awk/sed` line-anchoring of `docker-compose-dev.yaml`, `ls/du/df`, repo greps for `routes.py` / `craft_stub.py` / `setup-pipeline.sh` / `conftest.py` anchors. No `systemctl restart`, no `docker compose up`, no writes outside `/tmp`, no secret value read.

---

## 14. Source index

- `blueprint/files/pod_pipeline/routes.py:1-3, 12, 65, 73-82, 84-93, 98-117, 120-128, 138-143, 153-162, 171-183, 196-207`
- `blueprint/files/pod_pipeline/orchestrator.py:147-149, 167-177`; `runner.py:17, 42-64`
- `blueprint/files/deploy/setup-pipeline.sh:88-90`; `blueprint/files/deploy/craft-bin/*`; `blueprint/files/tests/{conftest.py:26,68, stubs/craft_stub.py:72-91, 92-139, test_routes.py:40-47, test_pipeline_integration.py:55,86,100,120}`
- `blueprint/files/skills/artcraft-command-atlas/references/catalogues/{vectorcraft,photocraft}-commands.json`
- Host: `/opt/deer-flow/docker/docker-compose-dev.yaml:213-230`, `/opt/deer-flow/extensions_config.json`, `/opt/deer-flow/extensions_config.example.json`, `/opt/craft/**`, `/opt/pod-pipeline/**`
- Predecessor: [`../wave2/01-STACK-VPS.md`](../wave2/01-STACK-VPS.md) §10, §12, §15 (GAP-BIN, GAP-ARGV, GAP-MCP, GAP-TOOLS)
- Machine-readable companion: [`01-REPAIR.json`](01-REPAIR.json)
