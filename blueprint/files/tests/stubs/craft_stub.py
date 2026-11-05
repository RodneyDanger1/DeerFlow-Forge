"""Stand-in for the five Craft CLIs. Invoked through launcher scripts named photocraft-cli, vectorcraft-cli, ...
It checks that the orchestrator passes the flags the spec requires, then writes plausible output files.

Behaviour switches (environment variables):
  STUB_VECTOR_EXIT=<n>     vectorcraft-cli exits n after printing an error
  STUB_SLEEP=<seconds>     sleep before doing anything (timeout tests); also leaves a background child behind
  STUB_SPAM_MB=<n>         print ~n MB of progress noise, a few error lines mixed in
  STUB_FLAKY_MARK=<path>   first call exits 137 (OOM-style) and creates the marker; later calls succeed
  STUB_KNIT=ok|antialias|rgba32   what kind of BMP designcraft stitch_matrix writes
"""
import os
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw

PDF = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"


def args_to_dict(argv):
    out, i = {}, 0
    while i < len(argv):
        tok = argv[i]
        if tok.startswith("--"):
            if i + 1 < len(argv) and not argv[i + 1].startswith("--"):
                out.setdefault(tok, []).append(argv[i + 1])
                i += 2
                continue
            out.setdefault(tok, []).append(True)
        i += 1
    return out


def need(a, flag, value=None):
    if flag not in a:
        print(f"ERROR: stub requires {flag}", file=sys.stderr)
        sys.exit(64)
    if value is not None and a[flag][0] != value:
        print(f"ERROR: stub requires {flag} {value}, got {a[flag][0]}", file=sys.stderr)
        sys.exit(64)
    return a[flag][0]


def art(path, size=(120, 90), alpha=True):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((10, 10, size[0] - 10, size[1] - 10), fill=(200, 30, 30, 255))
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "PNG")


def main():
    tool = os.path.basename(sys.argv[0])
    a = args_to_dict(sys.argv[1:])
    if os.environ.get("STUB_SLEEP"):
        os.system("sleep 120 &")                      # grandchild that must be killed with the group
        time.sleep(float(os.environ["STUB_SLEEP"]))
    mark = os.environ.get("STUB_FLAKY_MARK")
    if mark and not os.path.exists(mark):
        Path(mark).write_text("x")
        print("ERROR: simulated OOM kill", file=sys.stderr)
        sys.exit(137)
    mb = float(os.environ.get("STUB_SPAM_MB", "0"))
    if mb:
        line = "progress tile 000000 of 999999 ........................................................\n"
        for i in range(int(mb * 1024 * 1024 / len(line))):
            sys.stdout.write(line.replace("000000", f"{i:06d}"))
            if i % 50000 == 0:
                sys.stdout.write(f"WARNING: slow tile {i}\n")

    if tool == "vectorcraft-cli":
        if sys.argv[1:2] == ["run"]:
            # Measured 0.21.1 contract: run --in F --cmd ... --export OUT [...]
            need(a, "--in")
            exports = a.get("--export", [])
            if not exports:
                print("ERROR: vectorcraft-cli run requires --export", file=sys.stderr)
                sys.exit(64)
            for export in exports:
                p = Path(export)
                p.parent.mkdir(parents=True, exist_ok=True)
                if p.suffix.lower() == ".svg":
                    p.write_text("<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10'/>")
                elif p.suffix.lower() == ".pdf":
                    p.write_bytes(PDF)
                else:
                    p.write_bytes(b"unsupported")
            return
        assert sys.argv[1] == "trace", "vectorcraft-cli needs 'run' (or legacy 'trace')"
        code = int(os.environ.get("STUB_VECTOR_EXIT", "0"))
        if code:
            print("ERROR: trace failed: path simplification diverged", file=sys.stderr)
            sys.exit(code)
        need(a, "--input")
        Path(need(a, "--svg-out")).write_text("<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10'/>")
        Path(need(a, "--pdf-out")).write_bytes(PDF)
    elif tool == "photocraft-cli":
        if sys.argv[1:2] == ["run"]:
            # Measured 0.20.2 contract: run FILE --cmd ... --out FILE
            out = Path(need(a, "--out"))
            out.parent.mkdir(parents=True, exist_ok=True)
            art(out)
            return
        out_dir = Path(need(a, "--out-dir"))
        need(a, "--input")
        if a.get("--trim-alpha", ["false"])[0] == "true":
            need(a, "--target-dpi", "300")
            need(a, "--color-profile", "srgb")
            need(a, "--dimensions", "14x16in")
            art(out_dir / "trimmed.png")
        else:
            need(a, "--target-dpi")
            art(out_dir / "raster_600dpi.png")
    elif tool == "effectcraft-cli":
        out = Path(need(a, "--output"))
        out.parent.mkdir(parents=True, exist_ok=True)
        if "--filter" in a:
            need(a, "--filter", "vintage_screen_300")
            art(out)
        else:
            need(a, "--cylinder-taper")
            need(a, "--input")
            out.write_bytes(PDF)
    elif tool == "designcraft-cli":
        out = Path(need(a, "--output"))
        out.parent.mkdir(parents=True, exist_ok=True)
        if a.get("--mode", [""])[0] == "stitch_matrix":
            need(a, "--palette-limit")
            cols, rows = [int(x) for x in need(a, "--grid-scale").lower().split("x")]
            mode = os.environ.get("STUB_KNIT", "ok")
            if mode == "ok":
                im = Image.new("P", (cols, rows), 0)
                im.putpalette([200, 30, 30, 20, 20, 160, 240, 240, 240, 10, 10, 10] + [0] * (768 - 12))
                ImageDraw.Draw(im).rectangle((2, 2, cols // 2, rows // 2), fill=1)
                ImageDraw.Draw(im).rectangle((cols // 2, rows // 2, cols - 3, rows - 3), fill=2)
                im.save(out, "BMP")
            elif mode == "antialias":
                im = Image.new("RGB", (cols, rows))
                for x in range(cols):
                    for y in range(rows):
                        im.putpixel((x, y), ((x * 7) % 256, (y * 5) % 256, (x + y) % 256))
                im.save(out, "BMP")
            else:
                Image.new("RGBA", (cols, rows), (10, 10, 10, 128)).save(out, "BMP")
        elif a.get("--mode", [""])[0] == "wrap_tile":
            need(a, "--bleed", "0.25")
            need(a, "--input")
            out.write_bytes(PDF)
        elif "--template" in a:
            need(a, "--layer")
            need(a, "--embed")
            out.write_bytes(PDF)
        else:
            need(a, "--input")
            need(a, "--embed")
            out.write_bytes(PDF)
    elif tool == "filmcraft-cli":
        need(a, "--template")
        need(a, "--render-preset")
        Path(need(a, "--output")).write_bytes(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom" + b"\x00" * 64)
    else:
        print(f"unknown tool {tool}", file=sys.stderr)
        sys.exit(65)


if __name__ == "__main__":
    main()
