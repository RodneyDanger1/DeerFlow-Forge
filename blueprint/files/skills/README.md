# ArtCraft + Ridgeboundia skills

Reusable agent skills for the design apps (VectorCraft 0.21.1, PhotoCraft 0.20.2) and the
print pipeline. Each folder holds one `SKILL.md` with YAML frontmatter (`name`, `description`
with trigger words), exact commands and real paths, a step-by-step workflow, acceptance gates,
refusal conditions, worked examples and pitfalls.

## Install locations

- **Source of truth:** `blueprint/files/skills/<skill-name>/SKILL.md` (this tree, committed with
  the blueprint).
- **Agent runtime copy:** `%USERPROFILE%\.dsh\skills\<skill-name>\SKILL.md` — create-only; never
  overwrite an existing runtime skill. Copy after editing the blueprint copy.
- Update the blueprint first, then re-copy. One skill, one directory, one file.

## The eight skills

| Skill | Job | Input → output |
|---|---|---|
| `artcraft-vector-trace` | Raster → clean editable SVG (Image Trace + Expand, 10 gates) | PNG/JPG → SVG master + rendered check |
| `artcraft-image-cleanup` | PhotoCraft raster retouch in Photoshop order | Photo/scan/AI raster → corrected raster at known DPI |
| `apparel-print-master` | Provider canvas at 300 DPI, gated, print-ready | Art + template/area → PNG master + JSON report |
| `embroidery-art` | Stitch-legal art with measured minimums | Mark/brief + area → art + constraints (never a stitch file) |
| `brand-system` | Logo variants, palette, type, rules, templates | Mark + palette → brand kit and rules doc |
| `ad-creative` | Social/paid stills at 1080 canvases | Offer + assets → PNG/WebP creative |
| `web-banner` | Site hero/banner, desktop + mobile | Art + copy → WebP/PNG within budget |
| `shipping-card-tag` | Cards, inserts, hang tags with bleed | Spec + copy → print PDF / 300 DPI PNG |

## How they chain

**trace → master → publish**

1. `artcraft-vector-trace` produces the SVG master (or proves the art must stay raster).
2. `apparel-print-master` composes it on the provider canvas, retypes text, runs the 10 gates.
3. Publish is the handoff in `apparel-print-master`: upload → create hidden → `PUBLIC` → hide
   older versions → sync → verify `/shop` and product pages. It changes the live store, so it
   needs explicit owner approval.

**cleanup → trace**

`artcraft-image-cleanup` fixes the source (crop, dust, colour, sharpen at final size), then
`artcraft-vector-trace` traces the cleaned, white-cut raster. Cleanup never pretends to
vectorise, and trace never traces a dirty image.

**embroidery → art only**

`embroidery-art` ends at measured, stitch-legal artwork plus constraints. There is no stitch
file in this environment; a digitizer or the provider's embroidery service produces
`.DST/.PES/.EXP`. Never present the art as a stitch file.

**brand-system feeds the rest**

The kit (logo variants, hex palette, type with licences, print rules) is the input for
`ad-creative`, `web-banner`, `shipping-card-tag` and the garment/embroidery lockups. Those
skills consume the kit; they do not re-derive colours or type.

## Shared environment facts

- Pipeline root: `/opt/pod-pipeline` (run tools from there with `.venv/bin/python -m tools.<tool>`).
- VectorCraft CLI: `/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli`.
- PhotoCraft CLI: `/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli`.
- Provider geometry: `/opt/pod-pipeline/config/fourthwall-template-details.json` (623 rows,
  `areaGeometry` per area with inches and pixels at 300 DPI).
- Reference notes: `/srv/vaults/storefront/30-reference/art-learning/` (07 command atlas,
  09 workflows, 10 prompt templates, 13 usage guide, 15 apparel/print/marketing).
- Fonts: FreeSansBold and NimbusSans-Bold are installed; VectorCraft families include FreeSans,
  Nimbus Sans, Liberation Sans, Inter, Source Sans 3.

## Non-negotiable rules

- **No dry-run** in the craft CLIs: export to new paths and inspect the per-step JSON.
- **No browser automation** here: proof is rendered files, not page screenshots.
- **No stitch-file engine**: art and constraints only.
- **White rule**: every white transparent on garment art; cream/tan lettering survives.
- **Mockups are not print proof**: only a physical sample proves scale and colour.

## Verified on

2026-11-05 against the installed CLIs and pipeline: `imageTrace.make`/`expand`, `run` JSON
steps, `document.export` ppi math, `text.create`/`fontList`, `object.expand`, PDF/WebP export,
PhotoCraft `info`/`run` chains, `prep_print_art`, and `craft_trace` end-to-end. Commands that
were not executed are called out inside the individual skills.
