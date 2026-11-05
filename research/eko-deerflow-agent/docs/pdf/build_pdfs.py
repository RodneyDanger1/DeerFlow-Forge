#!/usr/bin/env python3
"""Build the two born-digital PDF reading copies from Markdown.

Source Markdown is read-only. Outputs are new files under docs/pdf/.
This is a catalogue/build tool, not production pipeline code.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(r"C:\Users\Riley\Desktop\DeerFlow Forge\research\eko-deerflow-agent")
OUT = ROOT / "docs" / "pdf"
FONT = r"C:\Windows\Fonts\arial.ttf"
FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"

try:
    pdfmetrics.registerFont(TTFont("Arial", FONT))
    pdfmetrics.registerFont(TTFont("Arial-Bold", FONT_BOLD))
    BODY_FONT = "Arial"
    BOLD_FONT = "Arial-Bold"
except Exception:
    BODY_FONT = "Helvetica"
    BOLD_FONT = "Helvetica-Bold"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ascii_text(s: str) -> str:
    """Keep the PDF text layer clean; the Markdown sources keep full Unicode."""
    repl = {
        "\u2014": "-", "\u2013": "-", "\u2192": "->", "\u2190": "<-", "\u00b7": "-",
        "\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'", "\u2265": ">=",
        "\u2264": "<=", "\u00d7": "x", "\u2026": "...", "\u2022": "-", "\u00a0": " ",
    }
    for a, b in repl.items():
        s = s.replace(a, b)
    return s.encode("ascii", "replace").decode("ascii")


def flowables(text: str):
    text = ascii_text(text)
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "body", parent=styles["BodyText"], fontName=BODY_FONT, fontSize=9.4,
        leading=13.0, spaceAfter=5, splitLongWords=True,
    )
    h1 = ParagraphStyle("h1", parent=body, fontName=BOLD_FONT, fontSize=16, leading=20, spaceAfter=8)
    h2 = ParagraphStyle("h2", parent=body, fontName=BOLD_FONT, fontSize=12, leading=15, spaceAfter=6)
    h3 = ParagraphStyle("h3", parent=body, fontName=BOLD_FONT, fontSize=10.5, leading=13, spaceAfter=4)
    code = ParagraphStyle("code", parent=body, fontName="Courier", fontSize=7.4, leading=9.2,
                          leftIndent=8, spaceAfter=1)
    out = []
    in_code = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            in_code = not in_code
            out.append(Spacer(1, 3))
            continue
        if in_code:
            out.append(Paragraph(escape(line) if line else "&nbsp;", code))
            continue
        if not line.strip():
            out.append(Spacer(1, 3))
            continue
        if line.startswith("# "):
            out.append(Paragraph(escape(line[2:].strip()), h1))
        elif line.startswith("## "):
            out.append(Paragraph(escape(line[3:].strip()), h2))
        elif line.startswith("### "):
            out.append(Paragraph(escape(line[4:].strip()), h3))
        elif line.startswith("|") and line.endswith("|"):
            out.append(Paragraph(escape(line), code))
        else:
            out.append(Paragraph(escape(line), body))
    return out


def build(name: str, title: str, files: list[str]) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / name
    title = ascii_text(title)
    doc = SimpleDocTemplate(
        str(out), pagesize=A4, title=title, author="Ridgeboundia research",
        leftMargin=17 * mm, rightMargin=17 * mm, topMargin=17 * mm, bottomMargin=15 * mm,
    )
    story = [Paragraph(title, ParagraphStyle("t", fontName=BOLD_FONT, fontSize=18, leading=22)),
             Spacer(1, 8),
             Paragraph("Derived reading copy. Markdown remains the source of record. "
                       "No source file is modified by this build.", ParagraphStyle("n", fontName=BODY_FONT,
                       fontSize=8.5, leading=11, textColor="#555555")),
             PageBreak()]
    for i, rel in enumerate(files):
        p = ROOT / rel
        story += flowables(p.read_text(encoding="utf-8"))
        if i != len(files) - 1:
            story.append(PageBreak())
    doc.build(story)
    return {"name": name, "title": title, "sources": files, "bytes": out.stat().st_size,
            "sha256": sha256(out)}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    dossier = build(
        "Forge-Conductor-Dossier.pdf",
        "Forge Conductor — Dossier",
        ["README.md", "ARCHITECTURE.md", "GOAL-EVALUATION.md", "PLAIN-ENGLISH.md"],
    )
    plan = build(
        "Forge-Conductor-Plan.pdf",
        "Forge Conductor — Goals, Integrations and Decision Plan",
        ["GOALS.md", "INTEGRATIONS.mmd", "execution-wave/09-GOAL-GAP-PLAN.md"],
    )
    (OUT / "build-info.json").write_text(
        json.dumps({"built": "2026-11-05", "font": BODY_FONT, "pdfs": [dossier, plan]}, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({"dossier": dossier, "plan": plan}, indent=2))


if __name__ == "__main__":
    main()
