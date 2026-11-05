# DeerFlow Forge skills index

Generated **2026-11-05T08:38:38Z** by `install_skills.py` 1.0.0. Counts and runtime states are computed at generation time; read this file instead of assuming a fixed catalogue.

- Source of truth: `C:\Users\Riley\Desktop\DeerFlow Forge\blueprint\files\skills`
- DSH runtime: `C:\Users\Riley\.dsh\skills`
- Hermes runtime: `C:\Users\Riley\.hermes\skills`

**22 skill directories scanned | 22 installable | 0 failing validation.**

Runtime parity for installable skills: DSH current=22, missing=0, differs=0; Hermes current=22, missing=0, differs=0.

## Installable skills

| Skill | What it does (trigger summary) | Lines | Version | DSH | Hermes | SHA-256 |
|---|---|---|---|---|---|---|
| `ad-creative` | Produce social and paid-ad creatives at exact pixel canvases (1080 square, 1080x1350, 1080x1920) with safe margins, one message, readable type and… | 120 | — | current | current | `b555a1261b12` |
| `ai-art-vectorize-vectorcraft` | AI illustration to clean vector print art with VectorCraft imageTrace.make: pre-cutout, erase and retype AI text, custom limited-palette trace,… | 160 | 1.0.0 | current | current | `1b1d2255fbd8` |
| `ai-diffusion-artifact-cleanup` | Diagnose and remove AI diffusion artefacts before tracing or print export — soft/blurred edges, halo or drop-shadow around lettering, speckle and… | 159 | 1.0.0 | current | current | `a6f19cace7bd` |
| `ai-image-upscale-print` | Decide and execute the print-resolution step for AI/raster art: 150 vs 300 DPI pixel math, the 2.5x upscale gate, when upscaling is acceptable… | 157 | 1.0.0 | current | current | `347658beffd5` |
| `apparel-print-master` | Build a provider-ready DTG print master at 300 DPI on the exact Fourthwall area geometry — trace or raster route, retype AI text, compose, run the… | 139 | — | current | current | `447d50ca5780` |
| `artcraft-command-catalog` | Query and execute the ArtCraft command catalogues: 918 VectorCraft commands in 64 groups and the 965-row PhotoCraft engine registry. Use when the… | 160 | 1.0.0 | current | current | `dc842db127e1` |
| `artcraft-image-cleanup` | PhotoCraft raster cleanup in the Photoshop order — crop, retouch, colour, sharpen last, export at the right DPI — plus the strict white cutout when… | 140 | — | current | current | `58a0bc7089f8` |
| `artcraft-vector-trace` | Trace raster logos, badges and AI illustration into clean editable SVG with ArtCraft VectorCraft (Illustrator Image Trace equivalent) — white… | 140 | — | current | current | `4214e6d3f598` |
| `brand-system` | Assemble a usable brand kit — logo variants (primary, inverse, mono, icon), palette hex, type pairing with licences, clear-space and minimum-size… | 140 | — | current | current | `052c6f199e11` |
| `craft-mcp-drive` | Drive VectorCraft and PhotoCraft over MCP: start the stdio server headless or connected, initialize and list tools, map design jobs to the 33… | 159 | 1.0.0 | current | current | `0d6433c643df` |
| `embroidery-art` | Produce stitch-legal embroidery artwork (caps, patches, beanies) with measured cap heights, minimum stroke widths and a thread-colour limit —… | 140 | — | current | current | `3835eaa9ea17` |
| `fourthwall-beanie-embroidery` | Produce the exact Fourthwall Otto Knit Beanie embroidery master for template pro_12abde5f29c34ffbb2 — embroidery_front 5x1.75 in, 1500x525 at 300… | 160 | 1.0.0 | current | current | `2f970dc336e4` |
| `fourthwall-catalog-audit` | Independently audit what is actually live in the Ridgeboundia Fourthwall store — Open API state/access/price/image readback, local DB whitelist and… | 157 | 1.0.0 | current | current | `b0a483632828` |
| `fourthwall-hoodie-vector` | Produce the exact Fourthwall Gildan Classic Hoodie master for template pro_gUu4CvXsRm-BxogjB89KzA — front 14x14 in, 4200x4200 at 300 DPI, 8.5 in… | 158 | 1.0.0 | current | current | `d630d766d759` |
| `fourthwall-product-publish` | Publish, replace or retire a Ridgeboundia Fourthwall design product through the exact live pipeline — hidden create, PUBLIC, hide the old… | 159 | 1.0.0 | current | current | `a6e7083670fa` |
| `fourthwall-tee-vector` | Produce the exact Fourthwall Gildan Heavyweight Tee master for template pro_e4677535402b4eeb81 — front_large 15x18 in, 4500x5400 at 300 DPI, 8 in… | 156 | 1.0.0 | current | current | `0c56dc49b7a9` |
| `merch-mockup-proof` | Pull a live Ridgeboundia product's mockups from its product page and Fourthwall CDN into a dated proof folder, inspect placement/colour/cut-off… | 160 | 1.0.0 | current | current | `8f0b3f630e39` |
| `print-mockup-composite` | Compose a finished print master or design onto a garment/product canvas or a flat mockup for review: exact canvas sizes, integer centring math,… | 158 | 1.0.0 | current | current | `53ca2bffb10a` |
| `shipping-card-tag` | Lay out thank-you cards, package inserts, hang tags and product/QR cards with bleed, safe margins and 300 DPI, exported as print PDF or PNG. Use… | 123 | — | current | current | `dac8a4a85bf4` |
| `skill-installer` | Install, validate and update DeerFlow Forge skills in the DSH and Hermes runtimes — scan the skills tree, enforce the frontmatter and content… | 160 | 1.0.0 | current | current | `8e293b0c0df7` |
| `skills-index` | Route work to the right DeerFlow Forge skill — read the generated catalogue instead of guessing, match the user's wording to trigger descriptions,… | 150 | 1.0.0 | current | current | `0a1ec9daf54a` |
| `web-banner` | Produce website hero and banner art at desktop (1920x600-800) and mobile (800x1000) sizes, keeping type as HTML wherever possible and exporting… | 134 | — | current | current | `10b18d93096f` |

## Present but not installable

None at generation time.

Directories without a SKILL.md (tooling, not skills): `_meta`.

## Regenerate

This file is generated; do not edit it by hand. Rebuild it and the runtime copies with:

```powershell
python "C:\Users\Riley\Desktop\DeerFlow Forge\blueprint\files\skills\_meta\install_skills.py" --targets both
```

Use `--check` for validation only. Every copied SKILL.md is byte-identical to its source, so the source SHA-256 identifies both runtime copies.
