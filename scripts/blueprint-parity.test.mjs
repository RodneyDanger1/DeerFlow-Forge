/**
 * Census parity: the console's blueprint model must match the pipeline's route table.
 *
 * `src/lib/blueprint/model.ts` hand-copies every route's command line and output
 * template from `blueprint/files/pod_pipeline/routes.py`. Nothing checked that
 * the two stayed equal, so an edit to routes.py would leave the console showing
 * a command the pipeline no longer runs. This test derives both sides from
 * source (TypeScript import + a Python dump) and fails on any drift.
 */
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

import { ASSUMPTIONS, FAMILIES, buildPlan } from "../src/lib/blueprint/model.ts";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const FILES = join(ROOT, "blueprint", "files");
const RUN_ID = "8f3c1a9b-4e20-4c11-9a77-0b1d2e3f4a5b";
const WORK = `/opt/pod-pipeline/sandbox/${RUN_ID}`;
const BUILD = `/opt/pod-pipeline/build/${RUN_ID}`;

function pythonBin() {
  for (const candidate of process.platform === "win32" ? ["python", "python3"] : ["python3", "python"]) {
    const probe = spawnSync(candidate, ["-c", "import sys; print(sys.version_info[0])"], { encoding: "utf8" });
    if (probe.status === 0 && probe.stdout.trim() === "3") return candidate;
  }
  return null;
}

/** Dump the real route table from routes.py (stdlib only, no project deps). */
function routeContract(python) {
  const code = `
import json, sys
sys.path.insert(0, ${JSON.stringify(FILES)})
from pod_pipeline.routes import PRODUCT_TYPES, ROUTES, merged_cfg, render_argv
out = {"types": list(PRODUCT_TYPES), "routes": {}}
for pt, route in ROUTES.items():
    cfg = merged_cfg(pt, {"knitwear": {"knit_grid": "112x140"}})
    variables = {"src": "${WORK}/input.png", "art": "${WORK}/traced.svg",
                 "work": "${WORK}", "build": "${BUILD}", "run_id": "${RUN_ID}",
                 "asset_id": 1, "fallback_dpi": 600, "cfg": cfg}
    out["routes"][pt] = {
        "upload": route.upload,
        "final": route.final,
        "steps": [
            {
                "name": step.name,
                "module": step.module,
                "argv": list(step.argv),
                "argv_rendered": render_argv(step, variables),
                "outputs": list(step.outputs),
                "validators": [list(v) for v in step.validators],
                "timeout": step.timeout_s,
            }
            for step in route.steps
        ],
    }
print(json.dumps(out))
`;
  const result = spawnSync(python, ["-c", code], { encoding: "utf8" });
  if (result.status !== 0) {
    throw new Error(`routes.py dump failed: ${result.stderr || result.stdout}`);
  }
  return JSON.parse(result.stdout);
}

/** Shell-ish tokenizer: quoted groups become one token, the quotes are display-only. */
function tokens(command) {
  const out = [];
  const pattern = /"([^"]*)"|'([^']*)'|(\S+)/g;
  let match;
  while ((match = pattern.exec(command)) !== null) {
    out.push(match[1] ?? match[2] ?? match[3]);
  }
  return out;
}

const python = pythonBin();

test("console families cover exactly the pipeline's product types", (t) => {
  if (!python) return t.skip("python 3 is required to read routes.py");
  const contract = routeContract(python);
  assert.deepEqual(
    FAMILIES.map((family) => family.id).sort(),
    [...contract.types].sort(),
    "FAMILIES drifted from PRODUCT_TYPES",
  );
  assert.equal(FAMILIES.length, contract.types.length);
});

test("every console route step matches routes.py by name, module, argv, output, validator, timeout", (t) => {
  if (!python) return t.skip("python 3 is required to read routes.py");
  const contract = routeContract(python);
  for (const family of FAMILIES) {
    const route = contract.routes[family.id];
    assert.ok(route, `routes.py has no route for ${family.id}`);
    assert.equal(family.upload, route.upload, `${family.id}: upload template drifted`);
    assert.equal(
      family.steps.length,
      route.steps.length,
      `${family.id}: step count ${family.steps.length} vs routes.py ${route.steps.length}`,
    );
    route.steps.forEach((step, index) => {
      const shown = family.steps[index];
      const plan = buildPlan(family.id, false, true).find((item) => item.id === step.name);
      assert.ok(plan, `${family.id}[${index}] ${step.name}: not present in the rendered board plan`);
      const where = `${family.id}[${index}] ${step.name}`;
      assert.equal(shown.name, step.name, `${where}: step name drifted`);
      assert.equal(shown.module, step.module, `${where}: module drifted`);
      assert.deepEqual(tokens(plan.command), [...step.argv_rendered], `${where}: rendered command drifted from routes.py`);
      assert.equal(step.outputs.length, 1, `${where}: pin assumes one output per route step`);
      assert.equal(shown.output, step.outputs[0], `${where}: output template drifted`);
      const validator = step.validators[0]?.[0] ?? null;
      assert.equal(shown.validator, validator, `${where}: validator drifted`);
      const timeout = step.timeout === null ? null : `${step.timeout}s`;
      assert.equal(shown.timeout, timeout, `${where}: timeout drifted`);
    });
  }
});

// OLD → NEW: the console no longer says "craft-bin exits 127" after Phase 0.
// It must describe the measured contracts and the real absent-app refusals.
test("the console's stated assumptions describe measured commands and named refusals", () => {
  const text = ASSUMPTIONS.join(" ");
  assert.match(text, /measured 0\.21\.1/);
  assert.match(text, /run --in/);
  assert.match(text, /DesignCraft, EffectCraft and FilmCraft are absent/);
  assert.doesNotMatch(text, /never gave a vectorcraft-cli line/i);
  assert.doesNotMatch(text, /Knitwear adds --palette-limit/i);
});
