# Diagrams — validated

All eight `.mmd` sources were rendered through Kroki on 2026-11-05. SVG and PNG exist for each; the
sequence diagram (`03`) initially failed on a semicolon in message text and was corrected/revalidated.
The three highest-risk diagrams were visually inspected for clipping/crowding:
`01-goal-gap.png`, `04-forge-architecture.png`, `06-evidence-ladder.png`.

| # | Source | SVG | PNG | Purpose |
|---|---|---|---|---|
| 1 | `01-goal-gap.mmd` | `01-goal-gap.svg` | `.png` | goals → code gaps → phases |
| 2 | `02-runtime-topology.mmd` | `.svg` | `.png` | VPS services, ports, planes |
| 3 | `03-craft-command-path.mmd` | `.svg` | `.png` | operator → gateway → CLI → verifier |
| 4 | `04-forge-architecture.mmd` | `.svg` | `.png` | roles, memory, tools, data |
| 5 | `05-learning-state.mmd` | `.svg` | `.png` | episode/skill/rollback states |
| 6 | `06-evidence-ladder.mmd` | `.svg` | `.png` | why each proof rung matters |
| 7 | `07-decision-tree.mmd` | `.svg` | `.png` | build-vs-buy/scope decisions |
| 8 | `08-roadmap.mmd` | `.svg` | `.png` | phase gates/time (estimate) |

## Re-render

```bash
mmdc -i 04-forge-architecture.mmd -o 04-forge-architecture.png -w 2048 --backgroundColor white
# or no-browser:
curl -X POST -H "Content-Type: text/plain" --data-binary @04-forge-architecture.mmd \
  https://kroki.io/mermaid/png -o 04-forge-architecture.png
```

## Notes

- PNGs are raster previews; SVGs are the editable/zoomable source.
- `08-roadmap.mmd` dates are an estimate, not a measured schedule.
- A diagram is a model, not evidence of implementation. See `../GOALS.md` for status.
