# Console control inventory — 2026-11-05

Source: `src/components/forge/console.tsx`, tab components, and a Chrome/Playwright drive of
`http://127.0.0.1:8080` at desktop (1280×900) and mobile (390×844).

| Tab | Controls counted | What was exercised |
|---|---:|---|
| Board | 8 | 5 family radios, 2 toggles, Run/Run again |
| Routes | 5 | every family accordion, `aria-expanded` |
| Sandbox | 1 | Open runner.py |
| Playbook | 3 + 2 code blocks | MCP server, products.json, compose.yml; copy/download |
| Sources | 34 file buttons + copy/download + mobile select | launcher file, last source, copy, download, mobile select |
| Shell | 5 nav buttons | all five tabs, `aria-current` |

No console errors, page errors, failed requests, or horizontal overflow on either viewport.
Screenshots: `screenshots/console-<tab>-<viewport>.png` from `scripts/visual-console-smoke.mjs`.
