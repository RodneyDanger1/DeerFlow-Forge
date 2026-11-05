---
name: artcraft-batch-automation
description: "Use when many PhotoCraft images or layers need repeatable processing: action lists, batch folders, naming/serial tokens, droplets, stop-on-error, per-layer/artboard/data-set export, and verification counts. Exact CLI syntax, action-file formats, collision traps. Triggers: batch resize, batch convert, action list, droplet, bulk export, layer export, naming tokens, batch automation."
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [photocraft, batch, actions, droplet, automation, export, naming]
    related_skills: [artcraft-image-cleanup, artcraft-photocraft-adjustments-filters, artcraft-document-export-formats, artcraft-command-atlas]
---

# PhotoCraft batch automation

Batch work is production code: inputs, a repeatable action list, collision-safe outputs, a stop
condition, and per-file verification. Full command map:
`artcraft-command-atlas/references/pc-batch-automation.md`.

## When to use / not use

- Use for many images with the same crop/resize/retouch/export steps, or for per-layer/artboard/data-set
  exports.
- Use when an action list/droplet must be reviewed, named and verified.
- Not for one-off edits (use the CLI `run` chain), vector work, or a batch you cannot verify by sample.

## Inputs

- Input directory/file list and a separate output directory.
- Action list or droplet + the exact action name for multi-action sets.
- Naming template (`{name}`, `{serial}`, `{date}`, `{ext}`), serial start.
- Failure policy (`--stop-on-error`), sample size, expected file count/dimensions.
- Rights and a source backup.

## Exact CLI (Linux VPS)

```bash
PC=/opt/craft/photocraft/photocraft-0.20.2-linux-x86_64/bin/photocraft-cli
cd /opt/pod-pipeline
# Linux VPS only. From Windows: ssh -i ~/.ssh/id_ed25519_hostinger root@179.197.88.181 'cd /opt/pod-pipeline && bash -s' < script.sh; stop if unavailable.
$PC batch --help
$PC droplet --help
```

Commands/ids used by automation:

- CLI: `batch`, `droplet`, `run`, `convert`, `info`, `serve`, `mcp`, `commands`.
- Engine: `file.automate.batch`, `file.automate.createDroplet`, `file.automate.runDroplet`,
  `file.scripts.imageProcessor`, `file.export.layersToFiles`, `file.export.artboardsToFiles`,
  `file.export.layerCompsToFiles`, `file.export.dataSetsAsFiles`, `file.export.quickExport`,
  `file.export.presets.*`, `file.export.exportPreferences`, `file.export.saveForWebLegacy`.

Action-list forms accepted by `batch` (from CLI help): JSON steps as `{"command":id,"params":{…}}`
objects, `[id, params]` pairs, or bare ids; a list may be wrapped in `{"actions":…}`/`{"steps":…}` or
a droplet; an Actions set is `{"actions":[{"name","steps"}…]}` and needs `--action NAME` when it holds
more than one action.

## Decision table

| Task | Use | Trap |
|---|---|---|
| Same pipeline over a folder | `batch --actions … --in DIR --out DIR` | output must differ from input unless `--in-place` |
| Recursive folders | `--recursive` | results flatten; name collisions overwrite |
| Collision-safe names | `--naming '{name}-{serial}'` | check tokens/start serial |
| Stop at first failure | `--stop-on-error` | otherwise later files still process |
| Play one action from a set | `--action NAME` | required for multi-action sets |
| Recorded automation | `droplet FILE|DIR` | validate scope/action |
| Per-layer files | `file.export.layersToFiles` | hidden/empty layers may be skipped |
| Per-artboard files | `file.export.artboardsToFiles` | artboard order/names |
| Per-data-set files | `file.export.dataSetsAsFiles` | row count vs output count |
| One-off chain | `run FILE --cmd … --out` | positional file; no dry-run |

## Workflow / state machine

`inventory → action file → dry sample → batch → count/verify → report`.
There is no dry-run flag; the safe dry run is one file into a scratch directory.

1. Inventory inputs (count, formats, dimensions); back up the source.
2. Write/obtain the action list; read each command's params; validate ids.
3. Run one input into a scratch output; inspect the result and the step JSON.
4. Run the batch with `--stop-on-error` and a collision-safe `--naming`.
5. Compare output count to input count; inspect samples from each subfolder; check dimensions/format.
6. Record the action file, command version, input/output counts and failures.

## Acceptance gates

- Output directory is distinct from input (unless deliberately `--in-place`).
- Output count matches expectations; no silent overwrites (check naming/serials).
- Sample outputs have the expected dimensions/format/mode and no corruption.
- Every action step id/params exists in the current registry; no deprecated/unknown ids.
- Batch stopped on first error as requested; failure log names the input.
- Source files unchanged; backup exists; report lists counts and paths.
- Droplet/action scope matches the files you intended.

## Refusals / failure modes

- Do not run a batch over the only copy; back up/inventory first.
- `--recursive` flattens into one output directory; same names can overwrite. Always use `--naming`
  or separate output trees.
- `--in-place` replaces originals; require explicit approval and a backup.
- Actions recorded against an older registry may contain unknown ids/params; validate first.
- A batch exit code is not proof every file is correct; count and sample.
- Do not claim unattended production if you did not inspect a sample from each input class.

## Worked recipes

**1. Batch resize.** Action file:
`[{"command":"image.imageSize","params":{"width":1600,"height":1600,"units":"px","keepPrintSize":false,"resample":"lanczos"}}]`
→ `$PC batch --actions /tmp/resize.json --in /tmp/raw --out /tmp/out --recursive --stop-on-error
--naming '{name}-{serial}'` → count/inspect.

**2. Batch convert.** `$PC batch --actions /tmp/convert.json --in /tmp/raw --out /tmp/webp
--recursive --naming '{name}' --format webp --quality 82` (verify flags via `batch --help`).

**3. Per-layer export.** `$PC run /tmp/source.psd --cmd file.export.layersToFiles
--params '{"path":"/tmp/layers","format":"png"}'` → inspect naming and skipped-layer behaviour.

**4. Droplet.** `$PC droplet /tmp/in --out /tmp/droplet_out` → validate the recorded action scope and
output count.

**5. Failure drill.** Include one corrupt file in a scratch batch; confirm `--stop-on-error` stops and
names it; fix/skip deliberately.

## Agent operating protocol

**Preflight:** inventory/backup; action-file validation; distinct output dir; naming/stop policy;
sample plan.

**Execution loop:** scratch sample → inspect → batch → count/sample → report; stop on failure.

**Evidence contract:** action file, CLI command, input/output counts, sample dimensions/format,
failures, version; exit 0 alone is not proof.

**Stop/escalate:** overwrite risk; unknown action ids; output=input; no sample verification; rights
unclear; batch scope ambiguous.

**Never:** use `--in-place` without explicit approval; run recursive batches without naming; claim all
files correct from exit 0; run untrusted action files outside an isolated account.

## Sources & verification

- **VERIFIED (help/source):** `batch`/`droplet`/`run`/`convert`/`info` subcommands; batch requires
  `--actions/--in/--out`; refuses output=input unless `--in-place`; `--recursive`, `--naming`,
  `--start-serial`, `--stop-on-error`, `--action`; naming tokens `{name}`, `{serial}`, `{date}`, `{ext}`
  from help; action-list forms from help; `file.export.*` ids from the 965-row registry.
- **NOT EXECUTED:** full production batch runs; this skill's batch commands are schema/help verified,
  not run on a real folder here.
- **ATLAS:** `artcraft-command-atlas/references/pc-batch-automation.md`, `command-tips.md`;
  official CLI book (see `sources.md`).
