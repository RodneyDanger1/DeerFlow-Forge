# DeerFlow Forge / Ridgeboundia design skills

Reusable agent skills for the ArtCraft design apps (VectorCraft/PhotoCraft), the Ridgeboundia
print pipeline, and the exact Fourthwall merch catalogue. One source of truth in this folder;
installed into **both** agent runtimes:

- DeepSeek Harness (DSH): `%USERPROFILE%\.dsh\skills\<name>\SKILL.md`
- Hermes Desktop: `%USERPROFILE%\.hermes\skills\<name>\SKILL.md`

## Install / update / validate

```powershell
python "blueprint/files/skills/_meta/install_skills.py" --check                 # validate only
python "blueprint/files/skills/_meta/install_skills.py" --targets both          # install/update both runtimes
python "blueprint/files/skills/_meta/install_skills.py" --targets both --force  # replace changed copies
python "blueprint/files/skills/_meta/validate_skills.py"                        # structural table + non-zero on failure
python "blueprint/files/skills/_meta/check_skill_commands.py"                   # semantic: every quoted command id exists
```

The installer refuses to overwrite a differing target unless `--force`, skips unchanged files by
SHA-256, and regenerates `_meta/manifest.json` + `_meta/SKILLS-INDEX.md`. New skills use the
Hermes-superset frontmatter (name, description, version, author, license, platforms,
`metadata.hermes`); the eight original skills keep minimal frontmatter and are still installable.

## Catalogue (22 skills)

| Skill | Family | Use it for |
|---|---|---|
| `artcraft-vector-trace` | ArtCraft | trace raster logos/badges to clean SVG |
| `artcraft-image-cleanup` | ArtCraft | PhotoCraft raster cleanup in Photoshop order |
| `ai-art-vectorize-vectorcraft` | AI art | AI illustration → clean vector print art |
| `ai-diffusion-artifact-cleanup` | AI art | deblur/dehalo/despeckle AI-diffusion artefacts |
| `ai-image-upscale-print` | AI art | 150/300 DPI and 2.5x upscale decisions |
| `print-mockup-composite` | AI art | compose a master onto proof/mockup canvases |
| `apparel-print-master` | Apparel | provider-ready DTG master + 10 gates |
| `fourthwall-tee-vector` | Fourthwall | exact Gildan tee product/area/master |
| `fourthwall-hoodie-vector` | Fourthwall | exact Gildan hoodie product/area/master |
| `fourthwall-beanie-embroidery` | Fourthwall | stitch-legal beanie wordmark (art only) |
| `fourthwall-product-publish` | Fourthwall | hidden create → publish → hide old → sync → verify |
| `fourthwall-catalog-audit` | Fourthwall | live provider/DB/storefront audit |
| `merch-mockup-proof` | Fourthwall | pull + judge live mockups; sample checklist |
| `embroidery-art` | Apparel | caps/strokes/thread-count rules |
| `shipping-card-tag` | Brand/marketing | thank-you cards, hang tags, labels |
| `ad-creative` | Brand/marketing | 1:1, 4:5, 9:16 ad canvases |
| `web-banner` | Brand/marketing | hero/banner desktop + mobile crops |
| `brand-system` | Brand/marketing | logo variants, palette, type, rules |
| `artcraft-command-catalog` | Engine | find/execute any of 918 commands in 64 groups |
| `craft-mcp-drive` | Engine | drive VectorCraft/PhotoCraft over MCP (33+26 tools) |
| `skill-installer` | Meta | install/validate skills on DSH + Hermes |
| `skills-index` | Meta | discover/route skills and chains |

## Chains

1. **Art → product:** `ai-diffusion-artifact-cleanup` → `ai-art-vectorize-vectorcraft` /
   `artcraft-vector-trace` → `apparel-print-master` (or product-specific skill) →
   `fourthwall-product-publish` → `merch-mockup-proof`.
2. **Supplied raster:** `artcraft-image-cleanup` → `ai-image-upscale-print` → trace/master.
3. **Embroidery:** `embroidery-art` → `fourthwall-beanie-embroidery` → external digitizer for DST/PES.
4. **Brand/marketing:** `brand-system` → `ad-creative` / `web-banner` / `shipping-card-tag`.
5. **Audit/repair:** `fourthwall-catalog-audit` → `skill-installer` / `skills-index`.

## Non-negotiable facts (learned the hard way)

- Every neutral white is transparent; keep cream lettering.
- Providers print DTG rows at 150 DPI native (tee 2250×2700, hoodie 2100×2100); our masters are
  300 DPI (4500×5400, 4200×4200) — never upload a half-size canvas.
- AI text must be erased and retyped; tracing cannot repair diffusion erosion/shadow.
- VectorCraft WebP export is **lossless-only** (the `quality` knob is a no-op); use
  `photocraft-cli convert --quality` for lossy WebP, and check bytes.
- VectorCraft presets overfit AI art (Flat Logo 3,982 paths); use the custom limited-palette params.
- A mockup is placement/cut-off proof, not print proof — order a sample.
- `file.place` uses a raster's **physical size at its ppi**, not its pixel count: 2000×1500 @300 ppi
  lands 480×360 centred at (300,360) on a 1080 canvas; @72 ppi it lands 2000×1500 at (−460,−210).
  Use `rect` or pre-resize with `magick -resize WxH^ -extent WxH`.
- VectorCraft WebP is lossless-only (quality ignored); use PhotoCraft `convert --quality` for lossy
  WebP — and compare bytes, because q82 can be larger than lossless on flat art (2,718 vs 1,372 B).
- Vector art is not a stitch file; `.DST/.PES/.EXP` needs a digitizer.
- The live tee master predates the zero-speck gate: regenerate before claiming 10/10.
- `document.export` accepts nested `svg {decimals,…}`, `pdf`, and `ppi`; PhotoCraft `run` takes the file
  positionally and `--quality` makes lossy WebP; `batch --recursive` flattens names (use `--naming`).

## Quality evidence

- `_meta/validate_skills.py`: **22 checked / 22 passed**, DSH 22 current, Hermes 22 current.
- `_meta/manifest.json` + `_meta/SKILLS-INDEX.md` are generated from the live scan.
- Independent audit: vault `30-reference/art-learning/19-SKILLS-QUALITY-AUDIT.md` (snapshot at
  08:32Z found 5 blockers; all 5 were fixed and the validator re-run — see the resolution log in
  that note; the snapshot verdicts are historical).
