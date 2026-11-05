# Command tips, tricks and failure modes

Practical rules distilled from the installed catalogues, CLI help, tool source and official docs.
They supplement — never replace — the exact `params` text in the catalogue.

## 1. Find the command, then read it

```bash
$VC commands | python3 -c 'import json,sys,collections; c=json.load(sys.stdin); print(len(c), len({x["id"].split(".")[0] for x in c}))'
$VC commands | python3 -c 'import json,sys; c=json.load(sys.stdin); [print(x["id"], "—", x["label"]) for x in c if x["id"].startswith("object.path")]'
$VC commands | python3 -c 'import json,sys; c=json.load(sys.stdin); print(next(x["params"] for x in c if x["id"]=="object.path.simplify"))'
$PC commands --json | python3 -c 'import json,sys; c=json.load(sys.stdin); print(next(x["params"] for x in c if x["id"]=="image.crop"))'
```

The catalogue `params` string is prose, not JSON Schema. Read it in full: required fields, defaults,
ranges and mutually exclusive options are in that sentence. `enabled:false` means state-dependent
(usually no document), not a missing id. PhotoCraft adds `needsDocument` and `disabledReason`.

## 2. State and selection

- Open a document first: `file.new`, `file.open`, `file.place`, or VectorCraft `run --in FILE`.
- `select.all` is mandatory before trace and many path/effect commands. A "nothing selected" error is
  the most common failure.
- Selection survives some commands and is replaced by others. Re-select deliberately.
- `ids` parameters override the current selection for commands that accept them.
- `layer.setCurrent` decides where new art lands; check it before drawing/importing.
- Commands are ordered. Undo is not a transaction; run destructive chains on a copy.
- No `--dry-run` exists in either CLI. Use a copy, a new output path, then inspect.

## 3. Params and units

- `--params` binds to the preceding `--cmd` / `-p`; reordering silently binds them to the wrong step.
- VectorCraft document units matter: `file.new` can be Pixels/Points/Picas/Inches/mm/cm, and many
  numeric params follow document units. Confirm with `document.inspect` or `document.inspect`.
- Points vs pixels: at 72 ppi, 1 pt = 1 px. At 300 ppi, 1 in = 300 px = 216 pt. `document.export`
  `ppi` wins over `scale`; `px = pt ÷ 72 × ppi`.
- PhotoCraft image sizes are pixels; `resolution` is metadata unless a resample command uses it.
- `file.place` uses the raster's **physical size at its ppi** (else 72), not pixel count. A 2000×1500
  image at 300 ppi lands 480×360 pt; at 72 ppi it lands 2000×1500 pt. Use `rect` for exact fit.
- `image.imageSize` with width/height resamples; `keepPrintSize` decides whether print size changes
  with resolution. Compute the target/crop ratio before committing.
- `image.crop` is destructive unless pixels are retained. Verify x/y/width/height against the source.
- Colours: screen hex is not a press value. CMYK/spot/Lab conversions need a proof and recorded
  equivalents; do not claim colour accuracy from an RGB render.
- Fonts: `text.fontList` lists installed families, not licences. Missing families fall back with a
  warning; `text.missingFonts`/`text.resolveMissingFonts` are the explicit path. Outline only after
  resolving fonts, and keep the live text master.

## 4. Geometry, paths and booleans

- Pathfinder/boolean operations flatten objects and can flatten the palette. Work on a copy and check
  object/colour counts. Stacking order decides `minusFront`/`minusBack`; `unite` destroys the inputs.
- `object.pathfinder.divide` splits overlaps into faces — great for recolouring, but object count can
  explode. `object.pathfinder.trim`/`merge`/`crop`/`outline` behave differently; read each params text.
- Outline strokes before booleans that expect filled regions (`object.path.outlineStroke`).
- `object.path.simplify` (level 0–100) is not the same as `object.path.cleanUp` (stray/empty/unpainted
  removal) or `object.path.smooth` (curve fitting). Compare anchor counts before/after.
- `object.path.offsetPath` creates a new contour; joins/miter limits change sharp corners. It is not a
  stroke-width edit.
- Compound paths (`object.compoundPath.make`) create holes; release before editing the child paths.
- Text outlines (`type.createOutlines`) are irreversible and drop live-text editability/hinting. Keep a
  live master; outline a delivery copy.
- Effects are live until expanded; expand before exporters/path operations that cannot read them.
- Opacity masks/clipping are compositing operations, not path booleans. Check the result on a real
  background.

## 5. Export and delivery

- `document.export` is the main delivery path. Options include `format`, `path`, `ppi`, `scale`,
  `artboard(s)`, `selectedOnly`, `includeArtboardFill`, `background`, `quality`, `colorModel`, and
  nested `svg`/PDF options. `document.formats` shows supported formats.
- SVG options (`svg.decimals`, `outlineText`, `embedFonts`, `responsive`, etc.) are nested under
  `svg` or accepted flat; verify the generated SVG, not just the command result.
- PDF/EPS: check fonts, transparency flattening and colour space. Do not call a screen PDF a press
  proof.
- PhotoCraft export commands: `file.export.quickExport`, `file.export.presets.*`,
  `file.export.layersToFiles`, `file.export.artboardsToFiles`, `file.export.artboardsToPdf`,
  `file.export.pathsToIllustrator`, `file.export.saveForWebLegacy`.
- Batch naming tokens are `{name}`, `{serial}`, `{date}`, `{ext}`; `--start-serial` sets the first
  number. With `--recursive`, results flatten into the output directory — same-named inputs overwrite
  unless `--naming` distinguishes them.
- Batch refuses an output directory equal to its input unless `--in-place`. `--stop-on-error` is the
  safe default for production batches; verify every output, not just exit code.
- Lossy WebP/JPEG can be **larger** than lossless on flat art. Compare bytes and dimensions; pick the
  smaller acceptable file, not the higher "quality" blindly.
- Never export over a source/master. Use a new path and hash/compare the result.

## 6. CLI and MCP

- VectorCraft: `vectorcraft-cli run --in FILE --commands FILE --export FILE`, or repeated
  `--cmd/--params`. `--commands -` reads stdin; `--scale` applies a raster scale. No dry-run.
- PhotoCraft: `photocraft-cli run FILE [--cmd ID --params JSON]... --out FILE`; the file is
  positional. `convert IN OUT`, `info FILE --compact`, `batch --actions FILE --in DIR --out DIR`,
  `droplet`, `serve`, `mcp`, `commands`.
- Exit codes: 0 success, 1 command/gate failure, 2 usage/refusal (PhotoCraft CLI); read stderr for
  the named step (`step N (id)`).
- MCP: start with `photocraft-cli mcp` / the VectorCraft MCP server, call `initialize`, `tools/list`,
  then `tools/call`. Tool names and schemas are the contract; do not assume a CLI name equals a tool
  name. The MCP guide is cited in `sources.md`.
- Paths: CLI paths are ordinary OS paths and are not sandboxed. Run untrusted action files in an
  isolated account. Do not log credentials; there are none in normal usage.

## 7. Mapping tips

- Start with the **output** (SVG/PDF/PNG/PSD/print), then choose the app and commands backwards.
- Prefer one high-level export command over a chain of format-specific hacks.
- A menu label may cover several ids (e.g. many `filter.*` variants); searching the label/menu is
  more reliable than guessing the id.
- Keep IDs case-exact: `imageTrace` (camelCase), `object.path.simplify` (lowercase), `image.imageSize`.
- If a command has `preset`/`presetId`, query `*.presets.list` or `*presets.list` first; do not invent
  preset names.
- If the job needs a capability with no command, record it as missing. Do not substitute a
  visually similar command that changes data shape (e.g. pathfinder instead of clipping).
- Verify with an independent artifact: `identify`, SVG XML parsing, PDF text extraction, file hash.

## 8. Common failure map

| Symptom | Likely cause | Fix |
|---|---|---|
| "nothing selected" | no selection before trace/effect | `select.all` or explicit `ids` |
| params applied to wrong step | `--params` order | pair each `--params` with its preceding `--cmd` |
| output missing/zero bytes | path directory absent or export refused | create dir; new path; read JSON result |
| image smaller/larger than expected | ppi physical-size placement | use `rect` or pre-resize at 72 ppi |
| colours changed after export | CMYK/spot conversion or profile | record conversion; use a proof |
| text shifted/missing | font fallback or outline order | resolve fonts; outline delivery copy |
| art flattened unexpectedly | pathfinder/merge/flatten | work on a copy; keep layered master |
| batch overwrote files | recursive flattening without naming | `--naming '{name}-{serial}'` |
| WebP larger after quality | lossy on flat art | compare with lossless; choose smaller |
| SVG huge | trace paths/presets overfit | simplify, lower paths/colours, check XML |
| PDF looks different in print | fonts/transparency/CMYK | package/outline; vendor proof |

## 9. Research basis

- Command ids/params: installed catalogues (918/965), 2026-11-05.
- CLI behaviour: local `--help` for both CLIs, plus the official PhotoCraft CLI book
  (`book/src/automation/cli.md`) and MCP guide.
- Illustrator/Photoshop semantics: Adobe Image Trace panel options and batch/actions help pages
  (URLs in `sources.md`). Those pages explain concepts; ArtCraft's own catalogue controls ids/params.
