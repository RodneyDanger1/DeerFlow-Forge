#!/usr/bin/env python3
"""Fast command lookup for the ArtCraft atlas.

Designed for an AI agent: search by intent text, id, or group without loading the
600 KB of family indexes into context. Stdlib only. The catalogues shipped next to
this script are the same snapshot used to generate the indexes.

Examples (run from this references/ directory, or with an absolute path):
    python command_lookup.py "outline text"
    python command_lookup.py --id type.createOutlines
    python command_lookup.py --group object.pathfinder --app vc
    python command_lookup.py "unsharp mask" --app pc --limit 3
    python command_lookup.py --stats
    python command_lookup.py "recolour" --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

BASE = Path(__file__).resolve().parent
CAT = BASE / "catalogues"
FILES = {
    "vc": CAT / "vectorcraft-commands.json",
    "pc": CAT / "photocraft-commands.json",
}
APPS = {"vc": "VectorCraft", "pc": "PhotoCraft"}

# Common intents map to a known starting command. Aliases are exact ids verified
# against the shipped catalogues; they do not replace reading the full params.
ALIASES = {
    "trace image": ["imageTrace.make"], "image to svg": ["imageTrace.make"],
    "vectorize": ["imageTrace.make"], "trace logo": ["imageTrace.make"],
    "outline text": ["type.createOutlines"], "text to outlines": ["type.createOutlines"],
    "convert text to outlines": ["type.createOutlines"], "outline the text": ["type.createOutlines"],
    "simplify paths": ["object.path.simplify"], "simplify path": ["object.path.simplify"],
    "clean up paths": ["object.path.cleanUp"], "clean path": ["object.path.cleanUp"],
    "outline stroke": ["object.path.outlineStroke"], "offset path": ["object.path.offsetPath"],
    "compound path": ["object.compoundPath.make"], "make holes": ["object.compoundPath.make"],
    "group": ["object.group"], "ungroup": ["object.ungroup"],
    "clipping mask": ["layer.clippingMask.toggle"], "clip": ["layer.clippingMask.toggle"],
    "align": ["object.align"], "distribute": ["object.distribute"],
    "new layer": ["layer.new"], "new artboard": ["artboard.new"], "new symbol": ["symbol.new"],
    "recolor": ["recolor.colors"], "recolour": ["recolor.colors"],
    "new swatch": ["swatch.new"], "apply swatch": ["paint.setFill"],
    "gradient": ["gradient.presets.apply"], "opacity mask": ["transparency.makeOpacityMask"],
    "export svg": ["document.export"], "export pdf": ["document.exportPdf"],
    "export png": ["document.export"], "export image": ["document.export"],
    "place image": ["file.place"], "new document": ["file.new"], "save copy": ["file.saveCopy"],
    "crop": ["image.crop"], "resize image": ["image.imageSize"], "resize": ["image.imageSize"],
    "levels": ["image.adjustments.levels"], "curves": ["image.adjustments.curves"],
    "hue saturation": ["image.adjustments.hueSaturation"],
    "black and white": ["image.adjustments.blackWhite"],
    "unsharp mask": ["filter.sharpen.unsharpMask"], "sharpen": ["filter.sharpen.unsharpMask"],
    "reduce noise": ["filter.noise.reduceNoise"], "denoise": ["filter.noise.reduceNoise"],
    "dust": ["filter.noise.dustAndScratches"],
    "select subject": ["select.subject"], "cut out subject": ["select.subject"],
    "refine edge": ["select.refineEdge"], "layer mask": ["layer.layerMask.revealSelection"],
    "save selection": ["select.saveSelection"], "load selection": ["select.loadSelection"],
    "cmyk": ["image.mode.cmyk"], "lab": ["image.mode.lab"], "grayscale": ["image.mode.grayscale"],
    "lut": ["file.export.colorLookupTables"], "export layers": ["file.export.layersToFiles"],
    "text on path": ["text.createInPath"], "replace font": ["text.replaceFont"],
    "area type": ["type.convertToAreaType"], "point type": ["type.convertToPointType"],
}


def load(app: str) -> list[dict]:
    path = FILES[app]
    if not path.is_file():
        raise SystemExit(f"missing catalogue: {path}; run build_command_guide.py from the repo")
    return json.loads(path.read_text(encoding="utf-8"))


def state(row: dict) -> str:
    parts = []
    if "enabled" in row:
        parts.append(f"enabled={row['enabled']}")
    if "needsDocument" in row:
        parts.append(f"needsDocument={row['needsDocument']}")
    if row.get("disabledReason"):
        parts.append(f"disabledReason={row['disabledReason']}")
    return ", ".join(parts) or "—"


def matches(row: dict, query: str) -> tuple[int, str]:
    q = query.lower().strip()
    if not q:
        return (0, "")
    rid = row.get("id", "").lower()
    label = str(row.get("label", "")).lower()
    menu = " ".join(row.get("menu") or []).lower()
    params = str(row.get("params", "")).lower()
    words = [w for w in q.split() if w]
    surface = f"{rid} {label} {menu}"
    surface_words = [w for w in words if w in surface]
    if rid == q:
        return (100, "id exact")
    if rid.startswith(q):
        return (90, "id prefix")
    if q in rid:
        return (80, "id contains")
    if q in label:
        return (70, "label")
    if q in menu:
        return (50, "menu")
    if q in params:
        return (30, "params")
    # an id word beats a label/menu word; a params-only hit is weakest.
    if any(w in rid for w in words):
        return (78, "word in id")
    if any(w in label for w in words):
        return (62, "word in label")
    if any(w in menu for w in words):
        return (55, "word in menu")
    if words and all(w in surface for w in words):
        return (80, "words on id/label/menu")
    hay = f"{rid} {label} {menu} {params}"
    if words and all(w in hay for w in words):
        return (20, "words in params")
    return (0, "")


def print_row(app: str, row: dict, why: str = "", max_params: int = 700) -> None:
    menu = " > ".join(row.get("menu") or [])
    print(f"[{APPS[app]}] {row['id']}  —  {row.get('label','')}")
    if menu:
        print(f"  menu:   {menu}")
    if why:
        print(f"  match:  {why}")
    print(f"  state:  {state(row)}")
    params = str(row.get("params", "")).strip()
    if not params:
        print("  params: {}")
    elif max_params > 0 and len(params) > max_params:
        print(f"  params: {params[:max_params]}…")
        print(f"          ({len(params)} chars; use --id {row['id']} --full-params for the full schema)")
    else:
        print("  params: " + params)
    print()


def main() -> int:
    _utf8_stdio()
    parser = argparse.ArgumentParser(description="Search the ArtCraft command catalogues by intent/id/group.")
    parser.add_argument("query", nargs="?", default="", help="free text (id/label/menu/params)")
    parser.add_argument("--app", choices=("vc", "pc", "both"), default="both")
    parser.add_argument("--id", help="exact command id (overrides query search)")
    parser.add_argument("--group", help="list all commands whose id starts with this group prefix")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--max-params", type=int, default=700, help="truncate params (0 = full)")
    parser.add_argument("--full-params", action="store_true", help="print full params (overrides --max-params)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--stats", action="store_true", help="counts per app/group, no search")
    args = parser.parse_args()

    apps = ["vc", "pc"] if args.app == "both" else [args.app]
    data = {app: load(app) for app in apps}

    if args.stats:
        payload = {}
        for app, rows in data.items():
            groups: dict[str, int] = {}
            for row in rows:
                groups[row["id"].split(".")[0]] = groups.get(row["id"].split(".")[0], 0) + 1
            payload[app] = {"total": len(rows), "groups": len(groups), "byGroup": dict(sorted(groups.items()))}
        print(json.dumps(payload, indent=2) if args.json else "\n".join(
            f"{APPS[a]}: {v['total']} commands / {v['groups']} groups" for a, v in payload.items()
        ))
        return 0

    if args.group:
        prefix = args.group.strip()
        rows = [(app, row) for app, rs in data.items() for row in rs if row["id"].startswith(prefix)]
        if not rows:
            print(f"no commands under group prefix {prefix!r}", file=sys.stderr)
            return 1
        payload = [{"app": app, **row} for app, row in rows]
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            for app, row in rows:
                print_row(app, row, "", 0 if args.full_params else args.max_params)
        return 0

    if args.id:
        found = [(app, row) for app, rs in data.items() for row in rs if row["id"] == args.id]
        if not found:
            print(f"unknown id {args.id!r}; try a query search instead", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps([{"app": app, **row} for app, row in found], indent=2))
        else:
            for app, row in found:
                print_row(app, row, "id exact", 0 if args.full_params else args.max_params)
        return 0

    if not args.query.strip():
        print("give a query, or use --id/--group/--stats", file=sys.stderr)
        return 1

    alias_ids = ALIASES.get(" ".join(args.query.lower().split()), [])
    if alias_ids:
        hits = []
        for app, rows in data.items():
            for row in rows:
                if row["id"] in alias_ids:
                    hits.append((200, app, row, "alias"))
        if hits:
            hits.sort(key=lambda item: (alias_ids.index(item[2]["id"]), item[1]))
            if args.json:
                print(json.dumps([{"score": s, "app": a, "why": w, **r} for s, a, r, w in hits], indent=2))
            else:
                print(f"alias match for {args.query!r}; read the full params before running.\n")
                for _score, app, row, why in hits:
                    print_row(app, row, why, 0 if args.full_params else args.max_params)
            return 0

    scored = []
    for app, rows in data.items():
        for row in rows:
            score, why = matches(row, args.query)
            if score:
                scored.append((score, app, row, why))
    scored.sort(key=lambda item: (-item[0], len(item[2]["id"]), item[1], item[2]["id"]))
    limit = max(1, args.limit)
    scored = scored[:limit]
    if not scored:
        print(f"no match for {args.query!r}; try a shorter phrase or --stats", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps([{"score": s, "app": a, "why": w, **r} for s, a, r, w in scored], indent=2))
    else:
        print(f"{len(scored)} match(es) for {args.query!r}; read the full params before running.\n")
        for score, app, row, why in scored:
            print_row(app, row, why, 0 if args.full_params else args.max_params)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
