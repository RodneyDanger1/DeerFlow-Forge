# W1-C evidence — skill guidance patches

**Date:** 2026-11-05 · **Status:** complete for the three identified gaps; guidance only, not runtime enforcement.

## Patched

| File | Gap | Patch |
|---|---|---|
| `skills/forge-harness-architect/SKILL.md` | D7 still said “≥3 successes + Wilson” | Pre-declared horizon + LB above baseline; 3/3 gives LB 0.4385 and does not pass; simulation is input, not policy; demotion/suite tested |
| `skills/craft-mcp-drive/SKILL.md` | No explicit await rule | Read the matching JSON-RPC response by `id` before dependent calls; PhotoCraft can interleave; timeout is failure, not replay permission; `command_batch` preserves order |
| `skills/apparel-print-master/SKILL.md` | Owner approval not bound to bytes | Record artifact SHA-256 + canvas/DPI/template/area/width + gate-report hash; stale/reused approval refused; re-export voids approval |

No rewrite of `craft-agent-operator` or `harness-code-adapter`: their evidence and donor-provenance
sections already cover A1/A5.

## Verification

```text
39 skills checked | 39 passed | 0 failed
Runtime before install: DSH current=36 differs=3 | Hermes current=36 differs=3
check_skill_commands: 62 files scanned (39 SKILL.md + 23 references); 0 with unknown command ids
install_skills --targets both --force: installed
Runtime after install: DSH current=39 missing=0 differs=0 | Hermes current=39 missing=0 differs=0
```

## Limits

- These are **guidance** changes. They do not prove a runtime enforces the rules.
- No production or pipeline file was touched by W1-C.
- Independent review of this patch and G0 is still pending.
