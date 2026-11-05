import { DOCKER_ARGV, NATIVE_ARGV, TREE } from "@/lib/blueprint/model";
import { CopyButton } from "@/components/forge/copy-button";

const LIMITS = [
  { name: "memory", value: "2g, and memory-swap equal to memory so the container cannot swap", where: "POD_DOCKER_MEMORY" },
  { name: "cpu", value: "1.5 cpus, cpu-shares 256 against a default 1024 web process", where: "POD_DOCKER_CPUS" },
  { name: "pids", value: "256", where: "runner.build_command" },
  { name: "network", value: "none. Craft cannot reach Fourthwall or the agent.", where: "--network none" },
  { name: "privileges", value: "cap-drop ALL, no-new-privileges, read-only root", where: "docker run" },
  { name: "tmp", value: "tmpfs /tmp, 512m, HOME=/tmp", where: "docker run" },
  { name: "mounts", value: "only that run's sandbox and build directories", where: "-v work -v build" },
  { name: "native", value: "nice -n 10 and ionice idle class. nice is not applied to the docker client.", where: "POD_NICE_LEVEL" },
  { name: "logs", value: "streamed. Disk cap 5 MiB. Agent digest 20 error lines, 12 tail lines, 2000 characters.", where: "logfilter.py" },
  { name: "postgres", value: "error_digest sliced to 8000 characters. Sync payloads capped at 32 KiB.", where: "db.py · schema.sql" },
];

const FAULTS = [
  { name: "trace exit 1", value: "Tier-1 raster fallback. trace_state becomes raster_fallback. The run continues." },
  { name: "other trace exit", value: "trace_state trace_failed. The run fails. No second tracer." },
  { name: "exit -9, -15, 137, 143, 75", value: "Transient. Retried up to POD max_attempts, default 2." },
  { name: "step timeout", value: "Process group SIGTERM, then SIGKILL. Docker container is killed by name. Transient." },
  { name: "validator reject", value: "Not retried. The same binary would write the same file." },
  { name: "flush timeout", value: "Output never settled for two polls. The step fails." },
  { name: "sha256 mismatch", value: "Asset quarantined before any Craft process starts." },
  { name: "Fourthwall 406", value: "publish_state needs_manual_upload. The run itself succeeds." },
  { name: "create 5xx", value: "Not retried. A retry could duplicate the product." },
  { name: "429", value: "Up to three retries using Retry-After. Upload-url is also capped at 20 per minute." },
  { name: "worker vanished", value: "recover_stale_runs sees a dead pid and puts the orchestrator row back to queued." },
];

export function SandboxView({ onOpen }: { onOpen: (path: string) => void }) {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-medium">Sandbox and faults</h2>
        <p className="mt-1 max-w-3xl text-sm text-pretty text-muted">
          Docker limits are what protect the web server. nice on the docker client would not reach processes the daemon starts.
        </p>
      </div>

      <section>
        <h3 className="text-base font-medium">Tree</h3>
        <pre className="mt-2 overflow-x-auto border border-fg/10 p-3 font-mono text-xs leading-relaxed text-fg">{TREE}</pre>
      </section>

      <section>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h3 className="text-base font-medium">Docker wrap</h3>
          <CopyButton text={DOCKER_ARGV} />
        </div>
        <pre className="mt-2 overflow-x-auto border border-fg/10 p-3 font-mono text-xs leading-relaxed text-fg">{DOCKER_ARGV}</pre>
        <p className="mt-2 text-sm text-muted">Native mode, when POD_USE_DOCKER is off: {NATIVE_ARGV}</p>
      </section>

      <section>
        <h3 className="text-base font-medium">Limits</h3>
        <ul className="mt-2 border border-fg/10">
          {LIMITS.map((row) => (
            <li key={row.name} className="grid gap-1 border-b border-fg/10 p-3 last:border-b-0 md:grid-cols-[8rem_1fr]">
              <span className="font-mono text-xs text-brass">{row.name}</span>
              <span className="text-sm">
                {row.value}
                <span className="mt-1 block font-mono text-xs text-muted">{row.where}</span>
              </span>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h3 className="text-base font-medium">What happens when a step fails</h3>
        <ul className="mt-2 border border-fg/10">
          {FAULTS.map((row) => (
            <li key={row.name} className="grid gap-1 border-b border-fg/10 p-3 last:border-b-0 md:grid-cols-[11rem_1fr]">
              <span className="font-mono text-xs text-brass">{row.name}</span>
              <span className="text-sm text-pretty">{row.value}</span>
            </li>
          ))}
        </ul>
        <button
          type="button"
          className="mt-3 h-11 border border-fg/15 px-3 text-sm text-fg hover:border-brass"
          onClick={() => onOpen("pod_pipeline/runner.py")}
        >
          Open runner.py
        </button>
      </section>
    </div>
  );
}
