---
name: visual-verification-critic
description: "Use when judging rendered art or a GUI result: artifact/hash, domain gates, independent render, tile/crop metrics, a blind schema-constrained critic, and a human rubric. Refuses exit-code-only, global-SSIM-only or screenshot-only success; designs defect tests for print/vector/raster outputs. Triggers: visual critic, verify art, check render, screen proof, print defect, visual QA, image diff, blind review."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [visual, verification, critic, render, gates, print, image-diff]
    related_skills: [agent-learning-loop, forge-harness-architect, apparel-print-master, artcraft-image-cleanup, artcraft-vector-trace]
---

# Visual verification critic

Exit codes and screenshots are not proof. This skill defines the evidence chain that turns a rendered
artifact into a defensible verdict — and the limits of what a vision model may claim.

## When to use / not use

- Use after any render/export/print master, before delivery or skill promotion.
- Use when a GUI/computer-use agent claims success.
- Use to build the blind critic prompt/schema and its defect test set.
- Not for the initial design decision (art direction) or a model benchmark.

## Evidence ladder (all applicable rungs)

1. **Process** — exit code, JSON result, command id, params, duration; a missing result is a failure.
2. **Artifact** — exists, non-zero, expected format, SHA-256, dimensions/DPI/colourspace.
3. **Domain gates** — `craft_trace` ten gates, `prep_print_art` coverage/upscale, print geometry.
4. **Independent render** — render SVG/PDF/PNG with a second renderer; compare engine vs independent.
5. **Tile/crop metrics** — SSIM/RMSE per tile + diff bounding box; global SSIM misses localized defects.
6. **Blind critic** — sees brief + renders only; crop-cited per dimension; no exit/gate/operator claims.
7. **Human rubric** — brief fit, hierarchy, type, colour, print safety; required for taste/publish.

A verdict is `pass` only if all applicable rungs agree. Missing evidence → `unverified`, never pass.

## Hard-won facts

- `craft_trace` writes the artifact **before** gates; a failed run can leave a PNG.
- `retyped_text_present` is vacuous when `retype_boxes == 0`; text requires a retype spec.
- `prep_print_art.ok` is hard-coded true; the 2.5× upscale limit is a **warning** (observed 3.609× with ok).
- Global SSIM 0.99994 on a good render only fell to 0.9787 after whitening a 120×100 block (~4% frame).
- Engine vs rsvg can be extremely close (SSIM 0.99994 / RMSE 0.0011) — use the independent render as a
  check, not as proof of print quality.
- Headless previews: VectorCraft ≤4096 px, PhotoCraft ≤2048 px; window screenshots need a GUI bridge and
  currently fail (`libxkbcommon-x11.so` missing).

## Required metrics

| Metric | Purpose | Failure signal |
|---|---|---|
| SHA-256 + dimensions/DPI | bind verdict to bytes | missing/mismatch |
| white residual ratio | paper/rim left | >0.002 |
| speck count | dust/grain | >0 |
| coverage | subject fill | outside 0.05–0.95 |
| edge density/definition | lost strokes | below threshold |
| hard-alpha share | feathered edge | <0.85 |
| tile SSIM / diff bbox | localized defect | any tile below threshold or unexpected bbox |
| palette/fill count | trace drift | outside 2–40 |
| text box/overlay | retype proof | 0 boxes with text |
| human rubric | taste | <3 or disagreement |

## Blind critic schema (minimum)

```json
{"verdict":"pass|fail|needs_human|unverified",
 "dimensions":[{"name":"brief_fit","score":1,"crop":[x,y,w,h],"observation":"...","severity":"none|minor|major"}],
 "defects":[{"kind":"halo|fringe|ghost_text|speck|layout|colour","crop":[...],"severity":"..."}],
 "confidence":0.0,"unseen":["..."],"model_id":"...","prompt_version":"..."}
```

Reject: no crop for a dimension, a score with no observation, a claim contradicted by a gate, or a
verdict that mentions exit codes/gate values (the critic is blinded to them).

## Critic test set

Build ≥50 labelled defects: white fringe, grey halo, ghost/repeated text, misplaced label, dust/speck,
lost thin stroke, wrong brand hex, margin violation, wrong DPI, banding, JPEG blocking, bad mask edge.
Measure precision/recall/false-pass per defect; re-run on any model/prompt change. The current
`deepseek-flash` vision accuracy is **unmeasured**.

## Human rubric

1–5 anchors for brief fit, hierarchy, typography, colour/brand, print safety, originality. Two reviewers
for promotion/publish; record disagreement, do not average it away. A human may fail a gate-passing
artifact on taste; that is `needs_human`, not a critic override.

## Commands / tools (safe)

```bash
identify -format '%f %wx%h %x %y %[colorspace]\n' /tmp/out.png
python -m tools.craft_trace --input /tmp/art.png --canvas-width 2400 --canvas-height 3000 --dpi 300 \
  --print-width-in 8 --output /tmp/master.png --svg /tmp/master.svg --report-json /tmp/master.json
python -m tools.prep_print_art --input /tmp/art.png --width-px 2400 --height-px 3000 --dpi 300 \
  --mode white --report-json /tmp/prep.json
rsvg-convert -w 2400 -o /tmp/out_rsvg.png /tmp/master.svg
python -c "from PIL import Image, ImageChops; ..."   # tile diff/metrics, written for the run
```

Read the report; `ok` alone is not enough; parse `warnings` and each gate value.

## Anti-patterns

- “Exit 0, so it worked.”
- One global SSIM score as the whole review.
- A critic that sees the gate report or the operator's claim.
- A screenshot of a UI toast as print proof.
- A human rubric invented after seeing the result.
- Claiming vision accuracy without the defect set.

## Output contract

Return: artifact hash/path/dimensions, gate values, independent-render deltas, tile/diff evidence,
critic JSON with crops, human score/approval, verdict, and `UNVERIFIED`. A verdict without this is
`unverified`.

## Sources

`wave2/03-CRAFT-SURFACE.md` §5–6; `wave2/04-HARNESS-DESIGN.md` §7; `craft_trace.py`,
`prep_print_art.py`; `apparel-print-master`; OpenAdapt read-back/stop-on-uncertainty evidence.
