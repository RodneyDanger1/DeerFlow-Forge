# VectorCraft recipes

## Verification status

- **VERIFIED end-to-end here:** `imageTrace.make`/`expand` + SVG export, `object.path.simplify`,
  `document.export` at ppi, `file.place` with `rect`, `file.new`/text create.
- **SCHEMA-VERIFIED only:** ids and params exist in the catalogue, but these exact sequences were not
  executed: boolean recipes, recolor, artboards, variables, stroke/effect combinations. Probe one step
  first; do not quote an output that was not run.
- All ids are checked by `check_skill_commands.py`/`check_atlas.py`; that is not behavioural proof.

Each recipe is a runnable sequence on the Linux VPS. Read the full params text for every id before
running; ids are verified against the 918-command snapshot. Always work on a copy and export to a new
path.

## 0. Probe before chaining

```bash
VC=/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli
$VC commands | python3 -c 'import json,sys; c=json.load(sys.stdin); print(next(x["params"] for x in c if x["id"]=="document.export"))'
$VC run --in /tmp/source.svg --cmd select.all --cmd object.path.simplify --params '{"level":40}' --export /tmp/probe.svg
```

Read the JSON result per step, then `identify`/XML-check the artifact.

## 1. Trace a flat logo → SVG

```bash
# 1) white cutout on the VPS
python -m tools.prep_print_art --input /tmp/logo.png --output /tmp/logo_cut.png \
  --width-px 1024 --height-px 1024 --dpi 300 --mode white --clean-rim \
  --min-component 60 --edge-clean-px 26 --edge-clean-lum 140 --margin-px 0 \
  --print-width-in 3.413333 --report-json /tmp/logo_cut.json

cat > /tmp/trace.json <<'JSON'
[{"command":"select.all"},
 {"command":"imageTrace.make","params":{"enhanced":false,"params":{
   "mode":"color","palette":"limited","colors":8,"paths":70,"corners":45,
   "noise":10,"method":"abutting","ignoreWhite":true,"fills":true,
   "strokes":false,"shapes":false,"autoGrouping":false,"gradients":false}}},
 {"command":"imageTrace.expand"},
 {"command":"document.export","params":{"path":"/tmp/logo.svg","format":"svg","svg":{"decimals":3}}}]
JSON
$VC run --in /tmp/logo_cut.png --commands /tmp/trace.json
rsvg-convert -w 2400 -o /tmp/logo_2400.png /tmp/logo.svg
```

Check: path count, fills 2–40, no key-colour fringe, holes intact at 100 %.

## 2. Retext a wordmark (live text → outlines)

```bash
cat > /tmp/text.json <<'JSON'
[{"command":"file.new","params":{"width":1200,"height":400,"units":"Pixels","backgroundContents":"transparent"}},
 {"command":"text.create","params":{"x":40,"y":280,"text":"RIDGEBOUNDIA","font":"FreeSans","style":"Bold","size":120,"color":"#33614a"}},
 {"command":"type.createOutlines","params":{}},
 {"command":"document.export","params":{"path":"/tmp/wordmark.svg","format":"svg","svg":{"outlineText":true,"decimals":3}}}]
JSON
$VC run --commands /tmp/text.json
```

`type.createOutlines` is irreversible. Keep the live-text document if edits are expected. Verify the
outline result has real paths (`grep -c '<path'`), not an embedded raster.

## 3. Simplify and clean a traced path set

```bash
cat > /tmp/paths.json <<'JSON'
[{"command":"select.all"},
 {"command":"object.path.cleanUp","params":{}},
 {"command":"object.path.simplify","params":{"level":45}},
 {"command":"document.export","params":{"path":"/tmp/paths.svg","format":"svg"}}]
JSON
$VC run --in /tmp/logo.svg --commands /tmp/paths.json
```

Compare path/anchor counts and visual 100 % crops. `cleanUp` can remove intentional tiny details;
`simplify` can round sharp corners. Neither is a substitute for a proper trace.

## 4. Boolean badge from shapes

```bash
cat > /tmp/badge.json <<'JSON'
[{"command":"file.new","params":{"width":800,"height":800,"units":"Pixels","backgroundContents":"transparent"}},
 {"command":"shape.rectangle","params":{"x":100,"y":100,"width":600,"height":600}},
 {"command":"select.all"},
 {"command":"object.pathfinder.unite","params":{}},
 {"command":"document.export","params":{"path":"/tmp/badge.svg","format":"svg"}}]
JSON
$VC run --commands /tmp/badge.json
```

Bolleans flatten inputs. Keep the source shapes/duplicate before unite; use `divide` only when you
want separate faces, and check object/colour counts.

## 5. Recolour a brand variant

```bash
cat > /tmp/recolor.json <<'JSON'
[{"command":"select.all"},
 {"command":"recolor.colors","params":{"colors":["#33614a","#d9caa4","#efe6cf"]}},
 {"command":"recolor.apply","params":{}},
 {"command":"document.export","params":{"path":"/tmp/brand_variant.svg","format":"svg"}}]
JSON
$VC run --in /tmp/logo.svg --commands /tmp/recolor.json
```

`recolor.colors` maps to the nearest palette; verify every resulting hex against the brand table and
fix drift deliberately. `recolor.reduce` reduces the palette; `recolor.randomize` is for exploration
only.

## 6. Artboard export pack

```bash
cat > /tmp/export.json <<'JSON'
[{"command":"document.export","params":{"path":"/tmp/board1.svg","format":"svg","artboard":0}},
 {"command":"document.export","params":{"path":"/tmp/board1@2x.png","format":"png","artboard":0,"ppi":144}},
 {"command":"document.export","params":{"path":"/tmp/board1.pdf","format":"pdf","artboard":0}}]
JSON
$VC run --in /tmp/source.svg --commands /tmp/export.json
identify -format '%f %wx%h %x %y\n' /tmp/board1@2x.png /tmp/board1.pdf 2>/dev/null || true
```

Artboard index/name must exist; `document.inspect`/`document.json` shows the list. `document.export`
`ppi` wins over `scale`; check the SVG has real paths and the PDF embeds/outlines fonts.

## 7. Place a raster at an exact box

```bash
cat > /tmp/place.json <<'JSON'
[{"command":"file.new","params":{"width":1080,"height":1080,"units":"Pixels","backgroundContents":"transparent"}},
 {"command":"file.place","params":{"path":"/tmp/art.png","rect":[80,80,920,920]}},
 {"command":"document.export","params":{"path":"/tmp/placed.png","format":"png","ppi":72}}]
JSON
$VC run --commands /tmp/place.json
```

`file.place` uses physical size (ppi) by default; `rect` forces the box (aspect kept). Check the
result bounds/size, not just that place succeeded.

## 8. Apply a command list from a file

```bash
cat > /tmp/steps.json <<'JSON'
[{"command":"select.all"},
 {"command":"object.path.simplify","params":{"level":35}},
 {"command":"stroke.set","params":{"width":2,"color":"#101312"}},
 {"command":"document.export","params":{"path":"/tmp/out.svg","format":"svg"}}]
JSON
$VC run --in /tmp/source.svg --commands /tmp/steps.json
```

`--commands -` reads stdin. Keep steps atomic; one failed step stops the chain at that point. There is
no dry-run: use a copy and a new export path.

## 9. Variable/data-driven art

```bash
# query first: variable.define, variable.bind, dataset.new, dataset.set
$VC commands | python3 -c 'import json,sys; c=json.load(sys.stdin); [print(x["id"],x["label"]) for x in c if x["id"].startswith(("variable.","dataset."))]'
```

Create variables, bind them to text/image objects, load a dataset, step/export each record. Validate
every output file, not only the dataset row count.

## 10. Delivery checks

- `document.export` result bytes > 0 and `identify`/XML parse succeeds.
- SVG: real `<path>` elements, expected viewBox, no embedded raster unless intentional.
- PNG: exact pixel dimensions and ppi; transparency at corners where expected.
- PDF: fonts embedded/outlined; page size; no clipped art.
- Report the command ids, catalogue lines read, artifact paths/sizes and any gate values.
