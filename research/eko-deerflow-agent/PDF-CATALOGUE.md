# PDF catalogue and audit trail

**Status:** generated from the frozen Markdown; Markdown remains the source of record.
**Date:** 2026-11-05. **Tooling:** pypdf 6.21.1, reportlab 5.0.1, PDF skills at
`C:\Users\Riley\Desktop\Divorce\knowledge\11-knowledge-book\12-SKILLS\pdf-documents`.

## Why a PDF layer

The corpus is Markdown because it is editable and diffable. A PDF is a stable reading copy for a human
reviewer: fixed pagination, a binder, page ranges, and a text layer that can be checked independently.
The PDF is **derived**; the source Markdown is never replaced or edited by this process.

## Artifacts

| Artifact | Purpose |
|---|---|
| `docs/pdf/Forge-Conductor-Dossier.pdf` | README + ARCHITECTURE + GOAL-EVALUATION + PLAIN-ENGLISH |
| `docs/pdf/Forge-Conductor-Plan.pdf` | GOALS + INTEGRATIONS + `09-GOAL-GAP-PLAN` (decision plan) |
| `docs/pdf/Forge-Conductor-Binder.pdf` | both PDFs, bookmarked, page-numbered |
| `docs/pdf/binder-index.md` | source → binder page ranges |
| `docs/pdf/Forge-Conductor-Dossier.txt` | extracted text + page audit |
| `docs/pdf/Forge-Conductor-Plan.txt` | extracted text + page audit |
| `docs/pdf/compare-report.txt` | byte/text comparison of original vs copy |
| `docs/pdf/PDF-RUN-LOG.txt` | exact commands and outputs |

All outputs live in **new** paths. No input is deleted, moved, redacted or overwritten.

## Procedure (per skill)

1. **Build** the PDFs from Markdown with reportlab. Source files are read-only.
2. **Extract** text with `mn-pdf-text-extract` (`text_extract.py`); record pages/chars/thin pages.
3. **Compare** the original PDF with a byte copy using `mn-pdf-compare` (`compare.py`); expect SAME.
4. **Bind** the two PDFs with `mn-pdf-review-binder` (`review_binder.py`); verify
   `total_pages = sum(inputs)` and `outline_items = 2`.
5. Record the exact commands, exit codes, hashes and counts in `PDF-RUN-LOG.txt`.

## Rules

- Do not quote a thin/blank page as if it had text.
- Do not treat a text diff as proof of legal/visual revision.
- The binder is a working copy; the Markdown + original PDFs remain the record.
- No OCR is needed for these born-digital PDFs; if a future scan is added, chain
  `mn-pdf-ocr-fallback` rather than inventing text.
- No redaction, Bates stamping or metadata scrubbing is performed here; those are separate,
  human-approved operations.

## Results

Measured 2026-11-05 with pypdf 6.21.1 and the three PDF skills:

| Artifact | Result |
|---|---|
| Dossier PDF | 19 pages, 40,106 extracted characters, sha256 `86a87b07…` |
| Plan PDF | 10 pages, 21,109 extracted characters, sha256 `2b19d2e5…` |
| Original vs byte copy | SAME; 19/19 pages; ratio 1.0000; 0 diff lines; identical text layer |
| Binder | **29 pages = 19 + 10**; **2 bookmarks**; index ranges `1-19`, `20-29` |
| Text extraction | 19 and 10 page markers; no thin pages; exit 0 both PDFs |

The first build had a PDF **text-layer encoding defect**: Unicode em dashes extracted as mojibake
(`â€”`). The source Markdown was correct; the build copy was rebuilt with normalized ASCII text so the
extracted layer matches the visible page. The defect and the fix are recorded rather than hidden.
The Markdown sources remain the source of record; the PDFs are derived reading copies.

**Proof path:** `docs/pdf/PDF-RUN-LOG.txt` (exact commands/outputs), `binder-index.md` (page ranges),
`Forge-Conductor-Dossier.txt` + `Forge-Conductor-Plan.txt` (page-level text), `compare-report.txt`
(empty because SAME), and `build-info.json` (hashes). The PDFs are **not** a pixel-perfect proof of
the product; they are a stable, page-indexed reading copy.

