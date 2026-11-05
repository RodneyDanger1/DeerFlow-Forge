# Examples — six original mechanisms

Each file is extracted intact from `wave2/07-EXAMPLES.md` (task-7), with its contract, code sketch,
inputs/outputs, failure path and VERIFIED-vs-PROPOSED section. They are **design examples**, not
production code.

| File | Mechanism | Runtime |
|---|---|---|
| `01-supervisor-loop-with-specialist-roles-and-typed-handoffs.md` | Supervisor + specialists + typed handoffs | Python |
| `02-typed-tool-gateway-for-craft-cli-mcp.md` | Typed gateway, allowlist, roots, idempotency, refusals | TypeScript/zod |
| `03-episode-ledger-hash-chain-write-path-and-retrieval.md` | Hash-chained episode ledger + retrieval | Python/SQL |
| `04-visual-critic-artifact-rendered-images-diagnostics-rubric.md` | Blind critic + render/metrics + rubric | Python |
| `05-skill-promotion-and-rollback-candidate-active-evidence-version-pin.md` | Candidate → active + rollback | Python |
| `06-rl-shaped-eval-loop-with-verifiable-gates-and-anti-reward-hacking.md` | Eval/RL-shaped loop + anti-hacking | Python |

Task-7 validation: 5 Python sketches + embedded blocks `py_compile` exit 0; TS `tsc --noEmit` strict
exit 0; 35/35 scratch checks; no placeholder/secret hits. **SQL/DB, real CLI/MCP parity, vision quality,
retrieval lift and real promotion are unverified.**

For the 200 questions and design context see `../wave2/08-200-QUESTIONS.md` and `../wave2/04-HARNESS-DESIGN.md`.
