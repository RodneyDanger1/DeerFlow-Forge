---
name: skill-installer
description: Install, validate and update DeerFlow Forge skills in the DSH and Hermes runtimes — scan the skills tree, enforce the frontmatter and content gates, copy byte-identical files by SHA-256, never overwrite a different target without explicit approval, and regenerate the install manifest and skills index. Use when the user says install skills, sync skills, validate skills, update the skill runtime, check skill health, or add a skill to another agent runtime.
version: 1.0.0
author: Riley Christensen
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [skills, installer, validation, cross-platform, dsh, hermes, sha256]
    related_skills: [skills-index]
---

# Skill installer

Moves one reviewed source tree into two agent runtimes without divergence: the repo
is the source of truth, the runtime copies are byte-identical artifacts identified by
SHA-256, and every action is recorded in a manifest and a generated index.

## When to use

- Installing reviewed repo skills into DSH, Hermes, or both.
- Checking validity, or whether a runtime copy has drifted.
- Updating a runtime copy after the source changed (a deliberate, forced replace).
- Auditing the catalogue: what is installable, what is failing, where it is present.

Do not use it to edit skill content; edit the repo copy, validate, then install.

## Where skills live

| Layer | Path | Rule |
|---|---|---|
| Source of truth | `<repo>/blueprint/files/skills/<name>/SKILL.md` | edit here |
| DSH runtime | `%USERPROFILE%\.dsh\skills\<name>\SKILL.md` | generated copy |
| Hermes runtime | `%USERPROFILE%\.hermes\skills\<name>\SKILL.md` | generated copy |

On POSIX the runtime roots are `~/.dsh/skills` and `~/.hermes/skills`; override them
with `--dsh` and `--hermes`. On this machine `<repo>` is `C:\Users\Riley\Desktop\DeerFlow Forge`.

One skill is one directory holding one `SKILL.md`; directories without one (`_meta`)
are tooling and are never installed.

## Commands

Set the repo path once per shell:

```powershell
$SKILLS = "C:\Users\Riley\Desktop\DeerFlow Forge\blueprint\files\skills"
```

| Goal | Command |
|---|---|
| Validate everything | `python "$SKILLS\_meta\validate_skills.py"` |
| Validate with JSON | `python "$SKILLS\_meta\install_skills.py" --check --json` |
| Install all valid skills to both runtimes | `python "$SKILLS\_meta\install_skills.py" --targets both` |
| Install one skill to Hermes only | `python "$SKILLS\_meta\install_skills.py" --targets hermes --skills web-banner` |
| Check the Hermes superset | `python "$SKILLS\_meta\install_skills.py" --check --require-hermes --skills skill-installer` |
| Deliberately replace one target | `python "$SKILLS\_meta\install_skills.py" --skills web-banner --force` |

On POSIX use `python3` and forward slashes. `--check` creates no directories and
writes neither the manifest nor the index. Both tools are Python 3.8+, stdlib only.

## Add a skill

1. Create `blueprint/files/skills/<name>/SKILL.md`; directory name and frontmatter
   `name` must match exactly.
2. Write an 80–600 character description carrying the phrases a user would say,
   then the workflow, gates and refusal conditions.
3. Keep the file between 40 and 220 lines.
4. Run `validate_skills.py` until the row says PASS, then `install_skills.py --targets both`.
5. Confirm source and both runtime copies share one SHA-256; the installer
   regenerates `_meta/SKILLS-INDEX.md`, so never hand-edit either generated file.

## Update a skill

An update is a replace, not a merge: edit the source, validate, then run the installer
for that skill with `--force`. Without it a differing target is a conflict and is left
untouched (exit 2). Scope `--force` with `--skills` so one update never becomes a
blanket overwrite.

## Hash rules and no-overwrite

| Source vs target | Action |
|---|---|
| Target missing | Create the directory and copy the file |
| Hashes equal | Skip; no write, no timestamp change |
| Hashes differ, no `--force` | Refuse; report `conflict`; exit 2 |
| Hashes differ, `--force` | Replace atomically, then verify the written hash |
| Source fails validation | Never copied; target reported `skipped` |

- Writes go to a temporary file in the target directory, move into place with
  `os.replace`, then read back and hash. A mismatch is an error, not a pass.
- No frontmatter is rewritten, so one hash identifies the repo file and both runtime
  copies; the manifest is merged, so prior entries survive a partial run.

## Validation gates

| Gate | Rule |
|---|---|
| Frontmatter | Opens with `---` on line 1 and closes with `---` |
| Name | `name` equals the directory name |
| Description | 80–600 characters |
| Unfinished work | The banned-marker family in `BANNED_RE` is rejected with line numbers |
| Secrets | Private-key blocks and live-looking credential literals are rejected |
| Length | 40–220 lines |
| Hermes superset | With `--require-hermes`: `version`, `author`, `license`, `platforms`, `metadata.hermes` |

The exact marker and secret patterns live in `_meta/install_skills.py`; run `--check`
to see the offending line instead of guessing.

## Both-platform frontmatter template

The superset both runtimes accept; copy it and fill the values:

```yaml
---
name: <skill-name>
description: <80-600 characters of trigger phrases and scope>
version: 1.0.0
author: Riley Christensen
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [<topic>, <topic>]
    related_skills: [<skill-name>]
---
```

`name` and `description` are required everywhere; the other keys are the Hermes
superset template; the 8 original skills keep minimal frontmatter and are installed with `--require-hermes` scoped to the selected skills only. The generated index does not record `--require-hermes` mode; run `--check --require-hermes --skills <name>` for the strict verdict.

## Manifest and index

- `_meta/manifest.json` — per skill: source path and SHA-256, counts, validation
  errors, and each target's path, hash, action and timestamp.
- `_meta/SKILLS-INDEX.md` — generated catalogue with runtime parity per skill; read it
  for the current list and do not copy its counts into another document.
- `--check` writes neither file; only an install run updates them.

Exit codes: `0` success, `1` validation failure or run error, `2` refused conflict.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `name ... does not match directory` | Directory and frontmatter disagree | Rename one; keep lowercase-hyphenated |
| `description length ... outside` | Too short or too long | Rewrite to 80–600 characters |
| `frontmatter: ...` | Missing opener, closer, or bad key line | Repair the block; no tab indentation |
| `line count ... outside` | File too thin or too long | Add substance or split the workflow |
| `unfinished-work marker` | A banned marker is in the text | Replace it with the real instruction or remove it |
| `possible private key block` | A key-shaped block is in the file | Remove it; credentials never belong in a skill |
| `conflict` / exit 2 | Target differs from source | Inspect both hashes; use `--force` only when intended |
| `unknown skill name(s)` | Typo, or the skill is not in the tree | List the tree; install only reviewed directories |

## Non-negotiables

- Edit the repo source, never a runtime copy, and never install a skill that has not
  passed the validator in this run.
- Never use `--force` on a conflict you have not inspected; regenerate the manifest and index, never patch them.


Semantic command check: run `python "$SKILLS\_meta\check_skill_commands.py"` — it
validates every quoted command id against the snapshotted 918-command VectorCraft and
965-command PhotoCraft catalogues and exits 1 on an invented id.
