# Example 2 — Typed tool gateway for Craft CLI/MCP

> Extracted from `wave2/07-EXAMPLES.md` (task-7). Original code/design, validated as recorded there; not production code.

## 2. Example 2 — Typed tool gateway for Craft CLI/MCP

### 2.1 What it demonstrates

One gateway that every tool call must pass through, in this order: **schema → role allowlist →
root confinement → version probe/pin → idempotency → execution → artifact verification**. It
fails closed with a named refusal and never executes when a precondition is unmet. It also
explains the host fact that makes this layer necessary: the deployed `PATH` resolves
`*-cli` to 127-shims while the real binaries live under `/opt/craft` and are absent from every
service `PATH`, so tools must be resolved by **absolute path + version probe** (04 §2.3, §6.2).

The sketch is TypeScript + zod because the contracts are easier to keep honest with a schema
library; the runtime service may be Python, since the gateway's boundary is the JSON contract,
not the language. Either way, the registry is data, not code.

### 2.2 Contract

```jsonc
// Registry entry — the only way a tool becomes callable (04 §6.2)
{
  "tool_id": "craft.run",
  "app": "vectorcraft",
  "bin": "/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli",
  "version_probe": ["--version"],
  "version_regex": "^vectorcraft-cli (\\d+\\.\\d+\\.\\d+)$",
  "surface": "cli",
  "writes": true,
  "allow_roles": ["vector_operator"],
  "roots": {"read": ["inbox", "work/<episode>", "build/<episode>"],
            "write": ["work/<episode>", "build/<episode>"]},
  "timeout_s": 900,
  "idempotency": "required",
  "outputs": [{"kind": "svg", "requireMagic": "<svg"}]
}
```

The gateway's `paramSchemas` map holds one zod schema per exact `cmd_id`, drawn from the pinned
catalogue — never a prefix wildcard. `imageTrace.*` is forbidden; `imageTrace.make` is listed.

```sql
-- Idempotency is enforced by the database, not by application memory (04 §6.5).
CREATE UNIQUE INDEX forge_tool_call_idempotency ON forge_tool_call (idempotency_key);
```

### 2.3 Sketch

<!-- Example 2 sketch — validated with tsc --noEmit (strict) -->
```typescript
/**
 * Example 2 - typed tool gateway for Craft CLI/MCP.
 *
 * Design-only mechanism sketch (TypeScript 5.x + zod 4). No process is spawned
 * when this module is imported; the gateway only executes inside call().
 */
import { createHash } from "node:crypto";
import { execFileSync, spawnSync } from "node:child_process";
import { readFileSync, realpathSync, statSync } from "node:fs";
import { dirname, isAbsolute, resolve, sep } from "node:path";
import { z } from "zod";

export const SURFACES = ["cli", "json", "mcp"] as const;
export const REFUSAL_CODES = [
  "E_COMMAND_UNKNOWN",
  "E_PARAM_REJECTED",
  "E_ROLE_FORBIDDEN",
  "E_ROOT_DENIED",
  "E_APP_DRIFT",
  "E_TOOL_TIMEOUT",
  "E_ARTIFACT_MISSING",
  "E_ARTIFACT_EMPTY",
  "E_APP_CRASH",
  "E_IDEMPOTENCY_CONFLICT",
] as const;

export type RefusalCode = (typeof REFUSAL_CODES)[number];

export interface Refusal {
  ok: false;
  code: RefusalCode;
  message: string;
  howToFix: string;
  terminal: boolean;
  evidenceRefs: string[];
}

export interface ToolSuccess {
  ok: true;
  toolId: string;
  episodeId: string;
  argv: string[];
  exitCode: number;
  durationMs: number;
  artifacts: ArtifactRecord[];
  replayOf: string | null;
}

export interface ArtifactRecord {
  path: string;
  sha256: string;
  bytes: number;
  format: string;
}

const RootPolicy = z.object({
  read: z.array(z.string().min(1)).min(1),
  write: z.array(z.string().min(1)),
});

export const OutputRule = z.object({
  kind: z.enum(["svg", "png", "json", "pdf"]),
  requireMagic: z.string().min(1).optional(),
});

/** One registry entry is the only way a tool becomes callable (design 04 section 6.2). */
export const RegistryEntry = z.object({
  toolId: z.string().min(1),
  app: z.string().min(1),
  bin: z.string().min(1),
  versionProbe: z.array(z.string().min(1)).min(1),
  versionRegex: z.string().min(1),
  surface: z.enum(SURFACES),
  writes: z.boolean(),
  allowRoles: z.array(z.string().min(1)).min(1),
  roots: RootPolicy,
  timeoutS: z.number().int().positive().max(3600),
  idempotency: z.enum(["required", "none"]),
  outputs: z.array(OutputRule).min(1),
});

export type RegistryEntry = z.infer<typeof RegistryEntry>;

export const ToolCallRequest = z.object({
  episodeId: z.string().uuid(),
  role: z.string().min(1),
  toolId: z.string().min(1),
  params: z.record(z.string(), z.unknown()),
  inputHashes: z.array(z.string().regex(/^sha256:[0-9a-f]{64}$/)),
  workdir: z.string().min(1),
});

export type ToolCallRequest = z.infer<typeof ToolCallRequest>;

export interface StoredCall {
  idempotencyKey: string;
  result: ToolSuccess;
  createdAt: string;
}

/** Implemented by the ledger repository (Example 3). */
export interface ToolCallStore {
  findByKey(key: string): Promise<StoredCall | null>;
  insert(call: StoredCall): Promise<void>;
}

export interface GatewayOptions {
  registry: RegistryEntry[];
  paramSchemas: Record<string, z.ZodType<Record<string, unknown>>>;
  store: ToolCallStore;
  pinnedVersions: Record<string, string>;
  hostRoots: string[];
}

function refusal(
  code: RefusalCode,
  message: string,
  howToFix: string,
  evidenceRefs: string[] = [],
  terminal = true,
): Refusal {
  return { ok: false, code, message, howToFix, terminal, evidenceRefs };
}

function canonicalJson(value: unknown): string {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  const entries = Object.keys(value as Record<string, unknown>)
    .sort()
    .map((key) => `${JSON.stringify(key)}:${canonicalJson((value as Record<string, unknown>)[key])}`);
  return `{${entries.join(",")}}`;
}

export function idempotencyKey(
  episodeId: string,
  toolId: string,
  params: Record<string, unknown>,
  inputHashes: string[],
): string {
  const material = [episodeId, toolId, canonicalJson(params), [...inputHashes].sort().join(",")].join("\u241f");
  return `sha256:${createHash("sha256").update(material, "utf8").digest("hex")}`;
}

function isInsideRoot(root: string, target: string): boolean {
  const rel = target.slice(root.length);
  return target === root || (target.startsWith(root) && rel.startsWith(sep));
}

/** Levenshtein distance, used only to suggest near ids, never to execute them. */
export function nearestIds(candidate: string, known: string[], limit = 5): string[] {
  const distance = (a: string, b: string): number => {
    const prev = Array.from({ length: b.length + 1 }, (_, j) => j);
    for (let i = 1; i <= a.length; i += 1) {
      let diagonal = prev[0];
      prev[0] = i;
      for (let j = 1; j <= b.length; j += 1) {
        const temp = prev[j];
        prev[j] = Math.min(
          prev[j] + 1,
          prev[j - 1] + 1,
          diagonal + (a[i - 1] === b[j - 1] ? 0 : 1),
        );
        diagonal = temp;
      }
    }
    return prev[b.length];
  };
  return [...known]
    .sort((a, b) => distance(candidate, a) - distance(candidate, b) || a.localeCompare(b))
    .slice(0, limit);
}

export class ToolGateway {
  private readonly entries: Map<string, RegistryEntry>;

  constructor(private readonly options: GatewayOptions) {
    this.entries = new Map(options.registry.map((entry) => [entry.toolId, RegistryEntry.parse(entry)]));
  }

  async call(request: ToolCallRequest): Promise<ToolSuccess | Refusal> {
    const parsed = ToolCallRequest.safeParse(request);
    if (!parsed.success) {
      return refusal(
        "E_PARAM_REJECTED",
        parsed.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; "),
        "rebuild the request from the tool contract",
      );
    }
    const req = parsed.data;
    const entry = this.entries.get(req.toolId);
    if (!entry) {
      return refusal(
        "E_COMMAND_UNKNOWN",
        `unknown toolId ${req.toolId}`,
        "query the pinned catalogue and use an exact id",
        nearestIds(req.toolId, [...this.entries.keys()]),
      );
    }
    if (!entry.allowRoles.includes(req.role)) {
      return refusal(
        "E_ROLE_FORBIDDEN",
        `${req.role} may not call ${entry.toolId}`,
        "use the role-scoped token for a role on the allowlist",
      );
    }
    const schema = this.options.paramSchemas[req.toolId];
    if (!schema) {
      return refusal(
        "E_COMMAND_UNKNOWN",
        `no parameter schema registered for ${req.toolId}`,
        "register the pinned catalogue schema before enabling the tool",
      );
    }
    const params = schema.safeParse(req.params);
    if (!params.success) {
      return refusal(
        "E_PARAM_REJECTED",
        params.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; "),
        "re-read the command schema; ranges are inclusive and enums are exact",
      );
    }

    const workdir = this.resolveWorkdir(entry, req.workdir);
    if (typeof workdir === "object") return workdir;

    const drift = this.probeVersion(entry);
    if (typeof drift === "object") return drift;

    const key = idempotencyKey(req.episodeId, req.toolId, params.data, req.inputHashes);
    const stored = entry.idempotency === "required" ? await this.options.store.findByKey(key) : null;
    if (stored) {
      return { ...stored.result, replayOf: stored.idempotencyKey };
    }

    const started = Date.now();
    const env = { ...process.env, PATH: dirname(entry.bin) };
    const run = spawnSync(entry.bin, this.argvFor(entry, params.data), {
      cwd: workdir,
      env,
      timeout: entry.timeoutS * 1000,
      killSignal: "SIGKILL",
      stdio: ["ignore", "pipe", "pipe"],
      encoding: "utf8",
    });
    const durationMs = Date.now() - started;

    if (run.error || run.signal) {
      return refusal(
        "E_TOOL_TIMEOUT",
        `${entry.toolId} did not finish within ${entry.timeoutS}s`,
        "split the batch or raise the declared deadline; the episode keeps no output",
        [],
        true,
      );
    }
    if (run.status !== 0) {
      return refusal(
        "E_APP_CRASH",
        `${entry.toolId} exited ${String(run.status)}`,
        "read stderr digest and map the code against the catalogue; never retry an unknown exit",
        [`stderr:${digestText(run.stderr ?? "")}`],
        true,
      );
    }

    const artifacts: ArtifactRecord[] = [];
    for (const match of matchArtifacts(run.stdout)) {
      const artifact = this.verifyArtifact(entry, req.workdir, match);
      if ("ok" in artifact) return artifact;
      artifacts.push(artifact);
    }
    if (artifacts.length === 0) {
      return refusal(
        "E_ARTIFACT_MISSING",
        `${entry.toolId} exited 0 but declared no artifact`,
        "treat exit 0 as a claim only; inspect the command contract for outputs",
        [`stdout:${digestText(run.stdout)}`],
      );
    }

    const result: ToolSuccess = {
      ok: true,
      toolId: req.toolId,
      episodeId: req.episodeId,
      argv: [entry.bin, ...this.argvFor(entry, params.data)],
      exitCode: run.status,
      durationMs,
      artifacts,
      replayOf: null,
    };
    if (entry.idempotency === "required") {
      await this.options.store.insert({
        idempotencyKey: key,
        result,
        createdAt: new Date().toISOString(),
      });
    }
    return result;
  }

  private resolveWorkdir(entry: RegistryEntry, requested: string): string | Refusal {
    let real: string;
    try {
      real = realpathSync.native(requested);
    } catch {
      return refusal("E_ROOT_DENIED", `workdir ${requested} does not exist`, "create the episode workdir first");
    }
    const allowed = entry.roots.write.length > 0 ? entry.roots.write : entry.roots.read;
    const rooted = allowed.map((root) => {
      try {
        return realpathSync.native(isAbsolute(root) ? root : resolve(this.options.hostRoots[0], root));
      } catch {
        return null;
      }
    });
    const inside = rooted.some((root) => root !== null && isInsideRoot(root, real));
    if (!inside) {
      return refusal(
        "E_ROOT_DENIED",
        `${real} is outside the declared roots for ${entry.toolId}`,
        "write only under work/<episode> and build/<episode>; symlink escapes are refused",
        allowed,
      );
    }
    return real;
  }

  private probeVersion(entry: RegistryEntry): true | Refusal {
    let output: string;
    try {
      output = execFileSync(entry.bin, entry.versionProbe, {
        encoding: "utf8",
        timeout: 15_000,
        stdio: ["ignore", "pipe", "pipe"],
      }).trim();
    } catch {
      return refusal(
        "E_APP_DRIFT",
        `${entry.bin} could not be probed`,
        "install the pinned build; a missing binary is drift, not a retry",
        [entry.bin],
      );
    }
    const match = new RegExp(entry.versionRegex).exec(output);
    if (!match || match[1] === undefined) {
      return refusal(
        "E_APP_DRIFT",
        `version probe for ${entry.toolId} did not match ${entry.versionRegex}`,
        "update the registry regex only after a catalogue refresh",
        [digestText(output)],
      );
    }
    const pinned = this.options.pinnedVersions[entry.toolId];
    if (pinned !== undefined && pinned !== match[1]) {
      return refusal(
        "E_APP_DRIFT",
        `${entry.toolId} reports ${match[1]}, episode pinned ${pinned}`,
        "refresh the catalogue, re-run goldens, repin the episode",
        [entry.bin, pinned, match[1]],
      );
    }
    return true;
  }

  private argvFor(entry: RegistryEntry, params: Record<string, unknown>): string[] {
    // Contract: params carry {subcommand: string[], flags: Record<string, string|number|boolean>}.
    const subcommand = Array.isArray(params.subcommand) ? params.subcommand : [];
    const flags = (params.flags ?? {}) as Record<string, string | number | boolean>;
    const argv = [...subcommand.map(String)];
    for (const key of Object.keys(flags).sort()) {
      const value = flags[key];
      if (value === false) continue;
      argv.push(`--${key}`);
      if (value !== true) argv.push(String(value));
    }
    return argv;
  }

  private verifyArtifact(
    entry: RegistryEntry,
    workdir: string,
    match: string,
  ): ArtifactRecord | Refusal {
    const absolute = isAbsolute(match) ? match : resolve(workdir, match);
    let real: string;
    try {
      real = realpathSync.native(absolute);
    } catch {
      return refusal("E_ARTIFACT_MISSING", `declared artifact ${match} does not exist`, "treat the batch as failed");
    }
    const rootOk = entry.roots.write.some((root) => {
      try {
        return isInsideRoot(realpathSync.native(isAbsolute(root) ? root : resolve(this.options.hostRoots[0], root)), real);
      } catch {
        return false;
      }
    });
    if (!rootOk) {
      return refusal("E_ROOT_DENIED", `artifact ${match} resolved outside roots`, "discard the batch");
    }
    const stat = statSync(real);
    if (stat.size === 0) {
      return refusal("E_ARTIFACT_EMPTY", `${match} is zero bytes`, "re-run the producing step on a copy");
    }
    const bytes = readFileSync(real);
    const head = bytes.subarray(0, 512).toString("utf8");
    const rule = entry.outputs[0];
    if (rule.requireMagic && !head.includes(rule.requireMagic)) {
      return refusal(
        "E_ARTIFACT_EMPTY",
        `${match} does not contain ${rule.requireMagic}`,
        "verify the export format; a truncated file is not a pass",
      );
    }
    return {
      path: real,
      sha256: `sha256:${createHash("sha256").update(bytes).digest("hex")}`,
      bytes: stat.size,
      format: rule.kind,
    };
  }
}

function digestText(text: string): string {
  return createHash("sha256").update(text, "utf8").digest("hex");
}

/** The CLI contract says one JSON object per line carrying an "artifact" field. */
function matchArtifacts(stdout: string): string[] {
  const found: string[] = [];
  for (const line of stdout.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed.startsWith("{")) continue;
    try {
      const parsed = JSON.parse(trimmed) as { artifact?: unknown };
      if (typeof parsed.artifact === "string" && parsed.artifact.length > 0) {
        found.push(parsed.artifact);
      }
    } catch {
      continue;
    }
  }
  return found;
}
```

### 2.4 Inputs and outputs

| Direction | Value |
|---|---|
| In | `ToolCallRequest {episodeId, role, toolId, params, inputHashes, workdir}` |
| Out | `ToolSuccess {ok:true, argv, exitCode, durationMs, artifacts[], replayOf}` **or** `Refusal {ok:false, code, message, howToFix, terminal, evidenceRefs}` |
| Persisted | One `forge_tool_call` row per executed call (unique idempotency key); result replayable |
| Never | A bare exit code, prose-only success, or a path outside the declared roots |

### 2.5 Failure path

| Failure | Where it stops | Refusal code | Terminal |
|---|---|---|---|
| Malformed request | request schema | `E_PARAM_REJECTED` | yes |
| `cmd_id` not in pinned catalogue | registry | `E_COMMAND_UNKNOWN` + 5 nearest ids, **no execution** | yes |
| Role not on the tool's allowlist | allowlist | `E_ROLE_FORBIDDEN` (proposed code) | yes |
| Params outside schema/range | per-command schema | `E_PARAM_REJECTED` | yes |
| Workdir escapes roots via `..` or symlink | `realpath` root check | `E_ROOT_DENIED` | yes |
| Version ≠ episode pin | version probe | `E_APP_DRIFT` | yes (human repin) |
| Binary missing/not probeable | version probe | `E_APP_DRIFT` | yes |
| Timeout / signal | spawn | `E_TOOL_TIMEOUT` | yes |
| Non-zero exit | spawn | `E_APP_CRASH` + stderr digest | yes |
| Exit 0 but no artifact | output scan | `E_ARTIFACT_MISSING` (exit 0 is a claim, not an effect) | retry once if transient, else fail |
| Zero-byte or wrong-magic artifact | artifact verification | `E_ARTIFACT_EMPTY` | yes |
| Duplicate idempotency key | store lookup | returns stored result, `replayOf` set — **the tool is not re-run** | n/a |
| Artifact mutated after write | caller re-hashes before use | `E_ARTIFACT_MISMATCH` (proposed; design's `E_SOURCE_MUTATED` covers inputs) | quarantine |

`E_ROLE_FORBIDDEN` is an extension: 04 §6.6 lists role allowlists but no dedicated code. It is
labelled `[I]` and must be added to the refusal table before implementation so agents get one
vocabulary, not two.

### 2.6 VERIFIED vs PROPOSED

| Claim | Label | Source / status |
|---|---|---|
| Real binaries live under `/opt/craft/...`; bare names on service PATH resolve to 127 shims | `[V]` | 04 §2.3 (host probe) |
| VectorCraft 0.21.1 / PhotoCraft 0.20.2 installed; catalogues exist | `[V]` | 04 §2.3 |
| Roots, allowlist, idempotency, refusal-code design | `[R]` | 04 §6.2–6.6 |
| Idempotency key formula | `[R]` | 04 §6.5 (same construction) |
| The TypeScript sketch typechecks under `strict` | `[V]` (this task) | `tsc --noEmit` exit 0 |
| Actual CLI JSON envelope field names (`artifact`, stdout lines) | `[U]` | **Assumed by the sketch**; 04 §15 lists "Craft CLI JSON envelope stability" as an open unknown. Probe 20 commands before relying on it. |
| Role-token mechanism | `[I]` | `forge_role_token` is proposed; no token issuer exists yet |
| zod parameter schemas generated from the catalogue | `[I]` | Requires a catalogue→schema generator, not written |
| MCP transport variant | `[U]` | The sketch shows the CLI path; MCP parity is asserted by the design but not exercised here |

---
