---
name: artcraft-svg-production
description: "Use when producing a production SVG for web or print handoff: trace/outline/simplify, choose SVG options, remove embedded rasters, handle text/fonts, add links/accessibility, then validate XML, viewBox, size and rendering. Exact ArtCraft ids and verification commands. Triggers: production SVG, SVG export, optimize SVG, SVG validation, text in SVG, responsive SVG, accessible SVG."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [artcraft, vectorcraft, svg, export, validation, accessibility, web]
    related_skills: [artcraft-document-export-formats, artcraft-vector-trace, artcraft-path-geometry, artcraft-command-atlas]
---

# Production SVG from ArtCraft

An SVG is production-ready when it renders correctly, has the intended geometry/text, has no
unexpected raster or private data, and is verified as XML/rendered output. Full map:
`artcraft-command-atlas/references/vc-file-document-export.md`.

## When to use / not use

- Use for web SVG, icon sets, brand marks, print handoff that expects SVG, or accessible/interactive
  SVG.
- Use when a traced/vector file needs simplification, text treatment, embedded-image cleanup or
  validation before delivery.
- Not for PDF/EPS/PNG delivery (`artcraft-document-export-formats`), raster cleanup
  (`artcraft-image-cleanup`), or physical print proof.

## Inputs

- Vector source and intended use (web/print/handoff), target dimensions/viewBox.
- Text policy: live text (with fonts) vs outlined paths; accessibility labels/links.
- Colour profile, transparency/background, max file size, browser/consumer constraints.
- Source copy and a delivery path.

## Exact commands (Linux VPS)

```bash
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
# Linux VPS only. From Windows: ssh -i ~/.ssh/id_ed25519_hostinger root@179.197.88.181 'cd /opt/pod-pipeline && bash -s' < script.sh; stop if unavailable.
```

Geometry: `imageTrace.make`, `imageTrace.expand`, `object.path.simplify`, `object.path.cleanUp`,
`object.pathfinder.unite` (only when flattening is intended), `type.createOutlines`.
Document: `document.inspect`, `document.formats`, `document.json`, `document.export`,
`document.exportForWeb`, `document.exportSettings`, `file.export`.
SVG options in `document.export`: `format:"svg"`, `svg` object (e.g. `decimals`, `outlineText`,
`embedFonts`, `responsive`, `objectIds`, `minify`, `useArtboards`, `preserveEditing`, `metadata`).
Interactivity: `svgInteractivity.*` (web-only); `webExport.settings`.

## Decision table

| Need | Use | Trap |
|---|---|---|
| SVG from traced art | trace → expand → simplify → export | too many paths/bytes |
| SVG from live text | keep live + embed/outline; `svg.outlineText` | outlining loses editability |
| Exact number precision | `svg.decimals` | too low distorts curves |
| Responsive SVG | `svg.responsive`/viewBox | CSS sizing may override |
| Accessibility/links | `svgInteractivity.*`/metadata | not print-relevant |
| Optimise bytes | simplify/cleanup/minify | over-simplification loses detail |
| Handoff to another app | `preserveEditing`/object IDs | larger file |

## Workflow / state machine

`inspect → copy → geometry cleanup → text policy → export options → validate XML/render → deliver`.
Verify the SVG as a consumer would, not only as an editor view.

1. Copy source; `document.inspect` and decide viewBox/artboard.
2. Trace (if raster) and expand; clean/simplify with counts; keep detail.
3. Decide text: live+embedded/outlined; outline only a delivery copy.
4. Export with explicit `svg` options; check file size and structure.
5. Validate XML (`python xml.etree`/`xmllint`) and render at target size (`rsvg-convert`).
6. Inspect for embedded rasters, unwanted metadata, missing fonts/IDs; deliver with source.

## Acceptance gates

- XML parses; root `svg` has a viewBox; width/height or responsive sizing as intended.
- Real paths/shapes; no unexpected `<image>` raster fallback.
- Text is either live with resolved/embedded fonts or outlined; no missing glyphs.
- Colours/transparency match the design; no external file dependencies.
- Path/byte counts reasonable for the use; no broken links/IDs.
- Render at target size matches the master; source retained.
- Report command/settings and verification outputs.

## Refusals / failure modes

- Do not claim SVG is font-safe without embedding or outlining; live text depends on the consumer.
- Do not outline the only master; keep live text.
- Do not use `minify`/low decimals without a visual diff; curves can distort.
- Do not include private editor metadata/asset paths in a public SVG; inspect.
- MCP/interactivity features are web-only; do not claim print behaviour.
- Browser rendering is not verified here; use rsvg/XML and state the limitation.

## Worked recipes

**1. Traced logo → SVG.** `imageTrace.make` → `expand` → `object.path.simplify` → `document.export`
`svg` with `decimals:3` → XML parse + `rsvg-convert` render; check hole counters and path count.

**2. Live text → outline delivery.** Keep live master → `type.createOutlines` on copy → export with
`svg:{outlineText:true}` → verify paths and compare against live render.

**3. Responsive icon.** Set viewBox/artboard → export `svg:{responsive:true}` → check width/height and
CSS sizing; render at 16/32/256 px.

**4. Interactive web SVG.** Apply `svgInteractivity.*` → export → verify links/IDs; do not use for
print.

## Agent operating protocol

**Preflight:** copy; inspect/viewBox; decide text policy/options; read `document.export` params.

**Execution loop:** geometry cleanup → export probe → XML/render verify → final export; stop on
missing fonts/rasters.

**Evidence contract:** export settings, SVG path/byte counts, XML/render results, text policy;
screen-only claims flagged.

**Stop/escalate:** missing font/licence; embedded raster not intended; invalid XML; no viewBox;
consumer constraint unknown; source would be overwritten.

**Never:** invent SVG option names; outline master; claim browser support; skip XML/render checks.

## Sources & verification

- **VERIFIED:** `document.export` accepts nested `svg` options; output SVG parse/render checks;
  `document.formats`; `imageTrace`/path ids.
- **ATLAS:** `artcraft-command-atlas/references/vc-file-document-export.md`,
  `recipes-vectorcraft.md`, `command-tips.md`.
- **DOCS:** local ArtCraft docs; SVG/Adobe export concepts; no browser test claimed.
