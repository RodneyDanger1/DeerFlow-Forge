import assert from "node:assert/strict";
import test from "node:test";

import { ASSUMPTIONS, buildPlan } from "./model.ts";

test("board trace command is the measured run contract, not the old invented argv", () => {
  const trace = buildPlan("apparel", false, true).find((step) => step.id === "trace");
  assert.ok(trace);
  assert.match(trace.command, /^vectorcraft-cli run --in /);
  assert.match(trace.command, /--cmd select\.all/);
  assert.match(trace.command, /--cmd imageTrace\.make/);
  assert.match(trace.command, /--cmd imageTrace\.expand/);
  assert.match(trace.command, /--export .*traced\.svg/);
  assert.doesNotMatch(trace.command, /vectorcraft-cli trace /);
  assert.doesNotMatch(trace.command, /--input /);
  assert.doesNotMatch(trace.command, /--svg-out /);
});

test("raster fallback points at the flat raster.png produced by the measured contract", () => {
  const fallback = buildPlan("apparel", true, true).find((step) => step.id === "fallback");
  assert.ok(fallback);
  assert.match(fallback.command, /^photocraft-cli run /);
  assert.match(fallback.command, /--cmd image\.imageSize/);
  assert.match(fallback.command, /--out .*\/raster\.png/);
  assert.doesNotMatch(fallback.command, /--out-dir/);
});

test("knitwear trace colours obey the factory palette cap without a CLI flag", () => {
  const trace = buildPlan("knitwear", false, true).find((step) => step.id === "trace");
  assert.ok(trace);
  const params = trace.command.match(/--params '(.+?)' /)?.[1];
  assert.ok(params);
  const parsed = JSON.parse(params) as { params: { colors: number } };
  assert.equal(parsed.params.colors, 6);
  assert.doesNotMatch(trace.command, /--palette-limit/);
});

test("apparel trim uses run/--cmd/--out, not the old input/out-dir argv", () => {
  const trim = buildPlan("apparel", false, true).find((step) => step.id === "photocraft_trim");
  assert.ok(trim);
  assert.match(trim.command, /^photocraft-cli run /);
  assert.match(trim.command, /--cmd image\.trim/);
  assert.match(trim.command, /--out .*\/trimmed\.png/);
  assert.doesNotMatch(trim.command, /--out-dir/);
});

test("apparel trim feeds the distress step from the path it actually writes", () => {
  const plan = buildPlan("apparel", false, true);
  const trim = plan.find((step) => step.id === "photocraft_trim");
  const distress = plan.find((step) => step.id === "effectcraft_distress");
  assert.ok(trim && distress);
  assert.match(trim.command, /--out \S+\/trimmed\.png/);
  assert.match(distress.command, /--input \S+\/trimmed\.png/);
  assert.doesNotMatch(distress.command, /apparel\/trimmed\.png/);
});

test("assumptions describe measured commands and absent-app refusals", () => {
  const text = ASSUMPTIONS.join(" ");
  assert.doesNotMatch(text, /never gave a vectorcraft-cli line/i);
  assert.doesNotMatch(text, /Knitwear adds --palette-limit/i);
  assert.match(text, /measured 0\.21\.1/);
  assert.match(text, /DesignCraft, EffectCraft and FilmCraft are absent/);
});
