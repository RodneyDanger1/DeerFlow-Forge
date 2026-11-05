# Promotion-policy simulation (`execution-wave/sim`)

Deterministic Monte-Carlo simulation of the Forge Conductor promotion policy
from `../wave2/06-LEARNING-LOOPS.md` §10. Pure Python standard library.

## Run

```powershell
cd "research/eko-deerflow-agent/execution-wave/sim"
python -m unittest -v test_promotion     # 23 tests
python simulate.py                       # writes ../04-PROMOTION.json
python simulate.py --trials 5000 --seed 7 --out .\out.json
```

`--trials` must be >= 100. Default: 20,000 trials, seed 20261105.

## Files

| File | Contents |
|---|---|
| `promotion.py` | Wilson lower bound, two-proportion z test, promotion rule, acceptance function, demotion monitor |
| `simulate.py` | nine scenarios (S1–S8 + power), JSON writer, console tables |
| `test_promotion.py` | unit tests for the arithmetic and failure paths |
| `../04-PROMOTION-SIM.md` | results, findings, calibration recommendation, limits |
| `../04-PROMOTION.json` | machine-readable results (generated) |

## Scope

This measures a **decision rule** under assumed success probabilities. It does
not measure Craft quality, model behaviour, gate reliability, or human taste,
and it does not call any model or service. See the report's non-claim.
