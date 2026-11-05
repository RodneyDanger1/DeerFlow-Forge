# Sources and verification

## Primary command sources (authoritative for ids/params)

- **VectorCraft command registry**, `vectorcraft-cli commands`, 918 commands / 64 groups, snapshot
  2026-11-05. Machine copy: `_meta/catalogues/vectorcraft-commands.json`.
- **PhotoCraft command registry**, `photocraft-cli commands --json`, 965 commands / 38 groups,
  snapshot 2026-11-05. Machine copy: `_meta/catalogues/photocraft-commands.json`.
- **CLI help** (executed): `vectorcraft-cli --help`, `vectorcraft-cli run --help`,
  `photocraft-cli --help`, `run|convert|batch|info|commands --help`.
- **Installed docs**: `/opt/craft/artcraft-docs/architecture.md`, `development.md`,
  `image-trace-adjustments.md`, `image-trace-quality.md`, `mcp.md`, `print-tiling.md`,
  `typography-lettering.md`.
- **Gate/tool source**: `/opt/pod-pipeline/tools/prep_print_art.py`, `craft_trace.py`,
  `vectorize_art.py`, `artcraft.py`.

## Official product documentation (web, fetched or cited)

- VectorCraft README: <https://github.com/storytold/vectorcraft> ·
  <https://raw.githubusercontent.com/storytold/vectorcraft/main/README.md> (fetched 2026-11-05).
- PhotoCraft README: <https://github.com/storytold/photocraft> ·
  <https://raw.githubusercontent.com/storytold/photocraft/main/README.md> (fetched 2026-11-05).
- PhotoCraft CLI book, `book/src/automation/cli.md` (fetched 2026-11-05):
  <https://github.com/storytold/photocraft/blob/5f65579ecb44047c2a619036c18ff273202e1389/book/src/automation/cli.md>
- PhotoCraft MCP/CLI guide (fetched):
  <https://photocraft.im/zh/guides/mcp-cli>
- Adobe Illustrator, **Image Trace panel options** (fetched 2026-11-05):
  <https://helpx.adobe.com/illustrator/desktop/manage-objects/traces-mockups-symbols/image-trace-panel-options.html>
- Adobe Photoshop, **Batch-process files** (official help; cited):
  <https://helpx.adobe.com/photoshop/desktop/automate-tasks/process-a-batch-of-files/batch-process-files.html>
- Adobe Photoshop, **Actions overview** (official help; cited):
  <https://helpx.adobe.com/photoshop/desktop/automate-tasks/automation-settings-and-presets/actions-overview.html>

## Claim labels used in this atlas

- **VERIFIED**: read from the installed catalogue/CLI/tool source or executed on the VPS.
- **DOCS**: stated by the official README/book/MCP guide or local ArtCraft docs.
- **ADOBE-CONCEPT**: Adobe explains the concept (trace options, batch/actions); ArtCraft ids/params
  still come from the local catalogue, not Adobe.
- **UNVERIFIED**: not executed here (e.g. physical print colour, MCP tool calls beyond list/probe,
  every PhotoCraft filter on every mode).

## What is not claimed

- This atlas does not prove that every command's behaviour matches its label in every document state.
- It does not prove print colour, physical output, font licensing, or platform policy compliance.
- It does not replace reading the catalogue's params text at run time; the snapshot can go stale.
