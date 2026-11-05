# DeerFlow Forge skills index

Generated **2026-11-05T14:24:59Z** by `install_skills.py` 1.0.0. Counts and runtime states are computed at generation time; read this file instead of assuming a fixed catalogue.

- Source of truth: `C:\Users\Riley\Desktop\DeerFlow Forge\blueprint\files\skills`
- DSH runtime: `C:\Users\Riley\.dsh\skills`
- Hermes runtime: `C:\Users\Riley\.hermes\skills`

**22 skill directories scanned | 22 installable | 0 failing validation.**

Runtime parity for installable skills: DSH current=22, missing=0, differs=0; Hermes current=22, missing=0, differs=0.

## Installable skills

| Skill | What it does (trigger summary) | Lines | Version | DSH | Hermes | SHA-256 |
|---|---|---|---|---|---|---|
| `ad-creative` | Use when a feed, portrait or story/reel ad still is needed at a standard canvas (1080×1080, 1080×1350, 1080×1920): brand kit, safe margins, one… | 188 | 1.1.0 | current | current | `76d7de29a700` |
| `ai-art-vectorize-vectorcraft` | Use for the production path from an AI-generated illustration to a clean vector print master: strict white cutout, AI text erased and retyped,… | 220 | 1.1.0 | current | current | `69df50523801` |
| `ai-diffusion-artifact-cleanup` | Use when an AI-diffusion render looks dirty at print size: soft/haloed edges, grey rim, speckle, semi-transparent fringe or JPEG blocking. Measures… | 200 | 1.1.0 | current | current | `1ec61a2876bf` |
| `ai-image-upscale-print` | Decide and execute the print-resolution step for AI/raster art: 150 vs 300 DPI pixel math, the 2.5x upscale gate, when upscaling is acceptable… | 157 | 1.0.0 | current | current | `347658beffd5` |
| `apparel-print-master` | Build a provider-ready DTG print master at 300 DPI on the exact Fourthwall area geometry — trace or raster route, retype AI text, compose, run the… | 139 | — | current | current | `447d50ca5780` |
| `artcraft-command-catalog` | Use when you need the exact ArtCraft command id, params or CLI flags for a design job — trace, type, path, colour, layer, artboard, export,… | 220 | 1.0.0 | current | current | `8c1a88836840` |
| `artcraft-image-cleanup` | Use when a supplied photo, scan or AI raster needs cleanup before print or web: crop, dust/scratches, noise, colour cast, levels/curves,… | 212 | 1.0.0 | current | current | `3890787cf300` |
| `artcraft-vector-trace` | Use when a raster logo, badge, crest or illustration must become a clean SVG master plus a rendered check PNG: strict white cutout, VectorCraft… | 212 | 1.1.0 | current | current | `f53484177939` |
| `brand-system` | Use to assemble a usable brand kit from a mark and palette: four lockups, palette hex + print equivalents, type with licences, clear-space/min-size… | 208 | 1.2.0 | current | current | `d9cc21dcf36d` |
| `craft-mcp-drive` | Drive VectorCraft and PhotoCraft over MCP: start the stdio server headless or connected, initialize and list tools, map design jobs to the 33… | 159 | 1.0.0 | current | current | `0d6433c643df` |
| `embroidery-art` | Produce stitch-legal embroidery artwork (caps, patches, beanies) with measured cap heights, minimum stroke widths and a thread-colour limit —… | 140 | — | current | current | `3835eaa9ea17` |
| `fourthwall-beanie-embroidery` | Produce the exact Fourthwall Otto Knit Beanie embroidery master for template pro_12abde5f29c34ffbb2 — embroidery_front 5x1.75 in, 1500x525 at 300… | 160 | 1.0.0 | current | current | `2f970dc336e4` |
| `fourthwall-catalog-audit` | Independently audit what is actually live in the Ridgeboundia Fourthwall store — Open API state/access/price/image readback, local DB whitelist and… | 157 | 1.0.0 | current | current | `b0a483632828` |
| `fourthwall-hoodie-vector` | Produce the exact Fourthwall Gildan Classic Hoodie master for template pro_gUu4CvXsRm-BxogjB89KzA — front 14x14 in, 4200x4200 at 300 DPI, 8.5 in… | 158 | 1.0.0 | current | current | `d630d766d759` |
| `fourthwall-product-publish` | Publish, replace or retire a Ridgeboundia Fourthwall design product through the exact live pipeline — hidden create, PUBLIC, hide the old… | 159 | 1.0.0 | current | current | `c2d09bf576ff` |
| `fourthwall-tee-vector` | Produce the exact Fourthwall Gildan Heavyweight Tee master for template pro_e4677535402b4eeb81 — front_large 15x18 in, 4500x5400 at 300 DPI, 8 in… | 156 | 1.0.0 | current | current | `0c56dc49b7a9` |
| `merch-mockup-proof` | Pull a live Ridgeboundia product's mockups from its product page and Fourthwall CDN into a dated proof folder, inspect placement/colour/cut-off… | 160 | 1.0.0 | current | current | `8f0b3f630e39` |
| `print-mockup-composite` | Compose a finished print master or design onto a garment/product canvas or a flat mockup for review: exact canvas sizes, integer centring math,… | 158 | 1.0.0 | current | current | `c6300d75ab87` |
| `shipping-card-tag` | Lay out thank-you cards, package inserts, hang tags and product/QR cards with bleed, safe margins and 300 DPI, exported as print PDF or PNG. Use… | 122 | — | current | current | `fcaf557b3fcc` |
| `skill-installer` | Install, validate and update DeerFlow Forge skills in the DSH and Hermes runtimes — scan the skills tree, enforce the frontmatter and content… | 165 | 1.0.0 | current | current | `3807955dc0fb` |
| `skills-index` | Route work to the right DeerFlow Forge skill — read the generated catalogue instead of guessing, match the user's wording to trigger descriptions,… | 150 | 1.0.0 | current | current | `0a1ec9daf54a` |
| `web-banner` | Produce website hero and banner art at desktop (1920x600-800) and mobile (800x1000) sizes, keeping type as HTML wherever possible and exporting… | 134 | — | current | current | `157593e26abb` |

## Present but not installable

None at generation time.

Directories without a SKILL.md (tooling, not skills): `_meta`.

## Regenerate

This file is generated; do not edit it by hand. Rebuild it and the runtime copies with:

```powershell
python "C:\Users\Riley\Desktop\DeerFlow Forge\blueprint\files\skills\_meta\install_skills.py" --targets both
```

Use `--check` for validation only. Every copied SKILL.md is byte-identical to its source, so the source SHA-256 identifies both runtime copies.
