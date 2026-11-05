# START HERE — Eko / Craft agent research

**Prepared 2026-11-05.** This folder answers the question: *can an existing agent harness drive the
Craft apps, and what must DeerFlow Forge add before it truly learns?*

## Read in this order

1. **[REPORT.md](REPORT.md)** — the 200-question dossier, executive decision, build-vs-integrate
   table, reference architecture, 90-day plan, claim register, evidence gaps and bibliography.
2. **Installed protocol:** `craft-agent-operator` skill (`SKILL.md` + `references/memory-ledger.md` +
   `references/evaluation.md`) — the loop an agent should follow, and the ledger/eval contracts it
   needs.
3. **Command layer:** `artcraft-command-atlas` (918 VectorCraft / 965 PhotoCraft commands, lookup,
   family indexes, recipes) and `craft-mcp-drive` (MCP transport and roots).
4. **Production gates:** `apparel-print-master`, `ai-art-vectorize-vectorcraft`,
   `artcraft-vector-trace`, `artcraft-image-cleanup`.

## The short answer

- **Eko** (FellouAI) is a real MIT JavaScript agent framework, but its memory is in-process context
  compression/snapshot, not durable learning.
- **Devain Eko** is an unrelated prompt-only thinking companion; **eko-agent-github** is a third-party
  GitHub-discovery demo.
- **DeerFlow Forge** is a console + deterministic Python pipeline with three MCP tools; it does not
  learn. The external DeerFlow 2.x harness has cross-session facts memory, not art-skill learning.
- **Craft apps are independent Rust implementations**, not 1:1 Adobe copies; Adobe tutorials transfer
  concepts, not exact commands.
- **Build the Craft Conductor + Experience Ledger + evaluation/promotion loop**, not a new generic
  agent framework and not a pixel-only computer-use agent.

## Evidence discipline

The report labels every claim `V` (verified source), `R` (local repo/catalogue), `I` (inference),
`U` (unverified/not found) or `H` (historical). It does **not** claim that any current system beats a
human designer, that Eko is a durable learning system, or that every Craft app/Adobe tutorial was
audited. Those gaps are listed in the report.
