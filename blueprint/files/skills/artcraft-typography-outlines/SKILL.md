---
name: artcraft-typography-outlines
description: "Use when wordmarks, taglines or type need exact ArtCraft handling: create area/point type, styles, threading, fonts/missing fonts, text on a path, fit-headline, OpenType alternates, convert to outlines, convert area↔point, change case. Triggers: typography, text to outlines, wordmark, font substitution, missing fonts, area type, text on path, fit headline."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [artcraft, vectorcraft, typography, type, fonts, outlines, wordmark]
    related_skills: [brand-system, artcraft-vector-trace, artcraft-svg-production, artcraft-command-atlas]
---

# ArtCraft typography and outlines

Type is content + a licensed font + layout rules; outlines are a delivery format, not the master.
Every id below is from the installed catalogue; the full map is
`artcraft-command-atlas/references/vc-text-type.md`.

## When to use / not use

- Use to create/edit wordmarks, taglines, area paragraphs, threaded text or text on a path.
- Use when fonts are missing, must be replaced, or must be outlined for a provider.
- Use when converting area↔point type, changing case or applying OpenType features.
- Not for brand rules/palette (`brand-system`), raster lettering cleanup
  (`ai-diffusion-artifact-cleanup`), or embroidery lettering (`embroidery-art`).

## Inputs

- Exact text, brand name/tagline, and approved claims/copy.
- Font family/style + licence; fallback allowed? Outline or embed?
- Layout: point vs area type, width/height, alignment, leading/tracking, text-on-path.
- Output: live-text master, outlined SVG/PDF, or both; print width.

## Exact commands (Linux VPS)

```bash
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
# Linux VPS only. From Windows: ssh -i ~/.ssh/id_ed25519_hostinger root@179.197.88.181 'cd /opt/pod-pipeline && bash -s' < script.sh; stop if unavailable.
```

Families and ids (read params before use):

- Content/layout: `text.create`, `text.setText`, `text.setStyle`, `text.setFormat`, `text.areaOptions`,
  `text.reshapeArea`, `text.reshapePath`, `text.createInPath`, `text.fitHeadline`, `type.fitHeadline`.
- Fonts: `text.fontList`, `text.fonts`, `text.missingFonts`, `text.findFontFiles`, `text.addFontFiles`,
  `text.replaceFont`, `text.rescanFonts`.
- Ranges/styles: `text.getRange`, `text.setRangeStyle`, `text.editRange`, `text.startList`,
  `type.size.increase`, `.decrease`, `.increaseByFive`, `.decreaseByFive`, `type.resetTracking`,
  `type.resetHorizontalScale`.
- Conversion: `type.createOutlines`, `type.convertToAreaType`, `type.convertToPointType`,
  `type.changeCase`, `type.orientation.horizontal`, `.vertical`, `type.opticalMarginAlignment`.
- Threading: `text.thread.create`, `.add`, `.releaseSelection`, `.remove`, `.break`, `.info`.
- Tabs/lists: `text.tabs.set`, `.get`, `.clear`, `text.convertListToText`.
- Glyphs: `text.glyphAlternates`, `text.setGlyphAlternate`, `type.smartPunctuation`, `type.ruby`.

## Decision table

| Need | Use | Trap |
|---|---|---|
| Short label | point type via `text.create` | one line; no wrap |
| Paragraph/box | area type / `text.areaOptions` | area type can overflow/hide text |
| Text in a shape | `text.createInPath` / `text.reshapePath` | start offset/alignment |
| Headline fits box | `text.fitHeadline`/`type.fitHeadline` | auto-size may violate brand min size |
| Replace a family | `text.replaceFont` | check missing fonts/licence/fallback |
| Outline for delivery | `type.createOutlines` | irreversible; keep live master |
| Area↔point | `type.convertToAreaType`/`.convertToPointType` | wrapping changes |
| Case | `type.changeCase` | locale/typographic quotes |
| Vertical type | `type.orientation.vertical` | layout only |
| Missing font | `text.missingFonts` → `text.findFontFiles`/`replaceFont` | warning does not stop export |

## Workflow / state machine

`copy → create/import type → resolve fonts → style/layout → fit/thread/on-path → outline delivery copy → verify`.
Keep the live-text master until the outline is verified.

1. Copy source; record font family/style/licence; `text.fontList`/`text.fonts`.
2. Create type (`text.create`) or convert existing; set style/size/colour/alignment.
3. Resolve fonts (`text.missingFonts`, `text.replaceFont`); record fallback if unavoidable.
4. Set area/point, wrapping, leading/tracking, threading/on-path as needed.
5. Fit headline only within brand min/max sizes.
6. Outline a **delivery copy** with `type.createOutlines`; keep the live master.
7. Export; inspect counters/holes and compare against the live render; record font status.

## Acceptance gates

- Text is exact (copy, case, punctuation) and within its box/safe area.
- Font family/style is the licensed one; no silent fallback; status recorded.
- Outlined result has real paths, closed counters (O, R, A) and no lost thin strokes at 100 %.
- Line breaks/alignment match the live master; no clipped text in area type.
- On-path text follows the path without overlapping/flipping; start offset is intentional.
- Live master retained; delivery copy is a new path; export artifact verified.

## Refusals / failure modes

- Do not outline before resolving fonts; outlining a fallback bakes the wrong letterforms.
- Do not distribute outlined text as a brand asset without a live master/wordmark rule.
- Unlicensed fonts: stop; use an installed open family or obtain a licence. Never imply clearance.
- Do not trace AI-rendered lettering; erase/retype in the trace pipeline.
- Missing-font warnings are not success; they are a decision point.
- Do not claim text fits from the editor view; measure bounds/area.

## Worked recipes

**1. Wordmark master → outline delivery.** `text.create` → style/size → `text.missingFonts` →
`type.createOutlines` on a copy → export SVG/PDF → compare counters at 100 %; keep live master.

**2. Area paragraph.** `text.create` (area) → `text.areaOptions` (width/height/inset) →
`text.setStyle`/`setFormat` (leading/alignment) → `text.fitHeadline` if needed → export PNG/PDF.

**3. Text on a path.** Select path → `text.createInPath` → adjust start offset/alignment in params →
`type.createOutlines` delivery copy → verify no overlap.

**4. Threaded copy.** `text.thread.create` → `text.thread.add` frames → `text.thread.info` to verify
links → export each artboard/page; no dropped text.

**5. Missing font recovery.** `text.missingFonts` → `text.findFontFiles`/`text.addFontFiles` if the
licensed file exists → `text.replaceFont` → re-render → outline only after verification.

## Agent operating protocol

**Preflight:** copy; record fonts/licence/layout/output; read exact params; decide live vs delivered.

**Execution loop:** one type operation; inspect render/bounds; resolve fonts before outlining; stop on
unexpected overflow/missing glyphs.

**Evidence contract:** text string, family/style/licence, bounds, outline path, render comparison,
font status; exit 0 alone is not proof.

**Stop/escalate:** unlicensed/missing font; no approved copy; fit would violate minimum size; area
overflow; outline loses counters; missing path for on-path text.

**Never:** invent font names; outline the only master; claim licence; call a fallback "exact"; trace
raster lettering.

## Sources & verification

- **VERIFIED:** ids exist in the 918-row catalogue; `text.fontList` returns 45 families on this
  install; `text.create`/`type.createOutlines` JSON shapes; `type.createOutlines` is irreversible.
- **ATLAS:** `artcraft-command-atlas/references/vc-text-type.md`, `00-intent-map.md`.
- **DOCS:** local `typography-lettering.md`; official README; Adobe Illustrator type/outline concepts.
