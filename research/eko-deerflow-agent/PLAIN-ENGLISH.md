# Plain English — what we have, what is wrong, and what we are building

This is the explanation for a human who does not want to read four hundred questions and a dozen
evidence files. It is intentionally blunt. If something is not built, it says so.

## 1. What we are trying to do

We want an AI worker that can make real print/vector artwork using the Craft apps that already run on
the server, check its own work with evidence, remember what worked, and get better under human
supervision. It should be able to take a brief like “make this badge trace-ready and print-safe,”
choose the right Craft commands, produce an SVG/PNG/PDF, verify the size/DPI/colors/gates, show the
result to a person, and only then publish.

That is the product. It is not “an AI that replaces the artist.” It is a reliable production
assistant with a paper trail.

## 2. What already exists

The server already runs **DeerFlow 2.2**, an agent runtime, with the **DeepSeek V4.1 Flash** model.
DeerFlow can hold conversations, run subagents, remember facts across sessions, and connect to tools.
That part is real.

The server also has **VectorCraft 0.21.1** and **PhotoCraft 0.20.2** installed. They are real Rust
apps with 918 and 965 commands and 33/26 MCP tools. They are independent apps, not Adobe clones.

There is a console at port 8091 and a small pipeline that is supposed to run the apps, verify the
image, and publish to Fourthwall. There are 39 skills, 400 research answers, 8 diagrams, and six
worked examples.

That is a lot of real material. But having the parts is not the same as having a working machine.

## 3. What is actually broken

The pipeline is connected to **fake launchers**: the scripts under `/opt/pod-pipeline/bin` are tiny
stubs that exit with code 127. The real Craft binaries are elsewhere and are never reached.

The Python `routes.py` also calls the apps with commands that do not exist. It pretends there is a
`trace` subcommand and an `--input` argument. The real apps use `run --in … --cmd … --export …`.
So even if the stubs were replaced, the arguments would still fail.

The Craft MCP servers work when you start them by hand, but DeerFlow is not registered to use them.
The only MCP server DeerFlow knows about is the old three-tool pipeline server.

The database is empty. There is no table that records an episode, a tool call, a gate result, a
critique, an evaluation, or a skill. So the system cannot learn from its runs, because it does not
remember them.

There is no approval queue. The storefront product ids still contain `REPLACE_WITH_TEMPLATE_ID`.
Publishing is therefore not safe and not configured.

Finally, the README says a live end-to-end run succeeded. That is not true today: the database is
empty and the last real run failed at the first stub. Treat that sentence as history, not current
status.

## 4. What we did about it

We did not start by rewriting the product. We did five things:

1. **Measured the real commands.** We ran the actual VectorCraft and PhotoCraft binaries and recorded
   the exact argv that works, including the fact that VectorCraft does not create export folders and
   PhotoCraft does.
2. **Designed the conductor.** We designed a third control plane, “Forge Conductor,” that sits beside
   the console and the pipeline. It owns planning, tool calls, evidence and learning; it does not own
   the Craft apps’ document truth or the model weights.
3. **Built executable evidence.** A 13-table Postgres schema, a 36-edge state machine, 33 Python
   tests, an adapter with 30 tests including a real crash/kill test, and a visual corpus with 15
   defects and 4 controls.
4. **Corrected our own mistakes.** The original promotion rule (“3 successes + Wilson 0.60”) cannot
   work: 3/3 gives a lower bound of 0.4385. The simulation replaced it with a horizon-based policy,
   and we wrote the correction into the skills instead of hiding it.
5. **Packaged everything.** The corpus, skills, examples and diagrams are in a 131-file Desktop
   folder and mirrored into the vault, with hashes and an index. Nothing was deleted.

## 5. The six integrations, in plain terms

**I1 — Fix the launchers and commands.** Point the pipeline at the real apps and use the commands that
actually exist. This is the first thing to build. Without it, nothing else can run.

**I2 — Connect the real Craft MCP servers.** Register VectorCraft and PhotoCraft with DeerFlow, give
them explicit read/write folders, and wait for each call to finish. PhotoCraft can interleave calls; a
dependent call must not be fired blindly.

**I3 — Add the conductor.** A small service that receives a task, makes a plan, runs the steps, records
everything, and can recover after a crash. It uses the new Postgres tables and a queue.

**I4 — Add the verifier and blind critic.** A step is not done because the command exited 0. The
verifier checks the file hash, dimensions, DPI, gates, a separate render, tile/crop differences, and
a critic that sees the image without knowing which version is supposed to be better. Missing evidence
means “unverified,” not “pass.”

**I5 — Add human approval before publish.** Approval is tied to the exact artifact hash. A stale
approval cannot be reused. The storefront product/template is checked before any write. No autonomous
publishing.

**I6 — Add learning and evaluation.** Episodes become searchable cases; repeated success can become a
versioned skill; a skill is promoted only after a declared number of trials, a Wilson lower bound above
baseline, a golden regression check, and human approval. A null A/B result disables the memory. No
fine-tuning or RL on this server.

## 6. The eight Python changes, in plain terms

1. Rewrite `routes.py` to call the measured commands.
2. Add a preflight that checks “is the app installed, is the version/catalogue pinned?” and refuses by
   name if not.
3. Fix `craft_trace` so the text check cannot pass on zero boxes and the artifact is not saved before
   the gate passes.
4. Fix `prep_print_art` so `ok:true` is not treated as a pass and a 3.6× upscale is not silently
   called print-safe.
5. Hash the source before and after; fail if the run mutated the original.
6. Add idempotency and duplicate replay to the tool gateway/DB.
7. Add a worker lease and reaper so a crash requeues work exactly once.
8. Record token/cost per step and enforce a cap.

These are small, testable changes. They are not a rewrite.

## 7. The eight agent/skill changes, in plain terms

1. The Craft operator must attach evidence, not say “looks good.”
2. The learning skill must use calibrated promotion and tested demotion, not 3/3.
3. The visual critic must use the five-check composite and render on black and white.
4. The harness architect must check which apps exist before designing for them.
5. The code adapter must record donor provenance and not copy code verbatim.
6. The research navigator must point to the right slice of the 400 answers without flooding context.
7. The MCP skill must wait for dependent calls and be honest about stdio vs HTTP.
8. The print/publish skill must bind approval to the artifact hash and check rights/templates.

## 8. What the goals are — and where they stand

- **Execute Craft work:** blocked. The stubs and wrong arguments stop it.
- **Use native tools:** partial. The MCP servers exist; they are not registered.
- **Verify quality:** partial. Gates exist but can lie; the critic is not wired in.
- **Learn:** not started. There is no episode/eval/skill data.
- **Host on the VPS:** feasible. The runtime and model are there; it is constrained.
- **Publish safely:** blocked. No approval, no template ids.
- **Be truthful:** improving. We have a claim register and an errata file; the old README sentence
  still needs correcting in the product docs.

## 9. What is possible, and what is best

**Possible now:** fix the execution path, run one real trace and one real retouch, record the evidence,
build the ledger and queue, run the visual critic on the synthetic corpus, and validate the key
without spending money.

**Not possible now:** all five Craft apps (three are absent), autonomous publishing, training new
model weights, RL, GUI-first automation (no display), or proving “better than a human.”

**Best path:** fix I1 and I2 first, then I3 and I4. Do not start with a GUI agent, a training run, or a
redesign. The bottleneck is the execution path, not the model.

## 10. What we need from Riley

1. Approve Phase 0 and let the repair be applied to a **staging copy** first.
2. Approve the zero-spend key check (`/user/balance`, `/models`); do not use a chat completion as a
   key test.
3. Decide whether FilmCraft/DesignCraft/EffectCraft will be purchased; until then they are out of
   scope.
4. Set the Fourthwall template/area ids or confirm publish stays disabled.
5. Choose the promotion baseline (`p0`), the evaluation horizon (`n`) and the false-promotion budget;
   the simulation is a suggestion, not a policy.
6. Name the human approver for taste/print/publish.

## 11. The honest bottom line

We have a strong research base, a real runtime, a real command catalogue, a real execution plan, and
working prototype tests. We do **not** have a working end-to-end Craft agent yet. The first honest
milestone is one real trace and one real retouch, recorded with evidence. After that, the learning
and publishing layers are worth building.

## 12. Where to read more

- [`README.md`](README.md) — the map and the plans.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — the system design.
- [`GOALS.md`](GOALS.md) — goals and non-goals.
- [`GOAL-EVALUATION.md`](GOAL-EVALUATION.md) — goal-by-goal status.
- [`execution-wave/09-GOAL-GAP-PLAN.md`](execution-wave/09-GOAL-GAP-PLAN.md) — the decision-complete plan.
- [`execution-wave/10-CLAIM-REGISTER.md`](execution-wave/10-CLAIM-REGISTER.md) — what is proven.
- [`diagrams/index.html`](diagrams/index.html) — eight pictures.
- [`PDF-CATALOGUE.md`](PDF-CATALOGUE.md) — the PDF reading copies.
