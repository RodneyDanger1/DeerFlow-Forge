import { sourceByPath } from "@/lib/blueprint/sources";
import { CopyButton, DownloadButton } from "@/components/forge/copy-button";

const STEPS = [
  "Place this tree at /opt/pod-pipeline on a Debian or Ubuntu VPS.",
  "Edit config/products.json. fourthwall_template_id comes from python -m pod_pipeline.worker --list-templates. knit_grid must be the factory COLSxROWS, or the BMP validator rejects the file.",
  "Run deploy/setup-pipeline.sh as root. It installs ImageMagick, Potrace, Ghostscript, ffmpeg, Docker, and a Postgres 16 container bound to 127.0.0.1:5432.",
  "The script writes config/pipeline.env with a database password and POD_CREDENTIAL_KEY, applies sql/schema.sql, and enables pod-mcp plus a one-minute drain timer.",
  "Insert a users_saas_accounts row. The Fourthwall secret is pgp_sym_encrypt'd with POD_CREDENTIAL_KEY. The comment at the top of schema.sql is the statement.",
  "Drop settled files into data/inbox/<account_id>/. The drain scans, or the agent calls trigger_pipeline_job.",
];

export function PlaybookView({ onOpen }: { onOpen: (path: string) => void }) {
  const setup = sourceByPath("deploy/setup-pipeline.sh");
  const schema = sourceByPath("sql/schema.sql");
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-medium">VPS playbook</h2>
        <p className="mt-1 max-w-3xl text-sm text-pretty text-muted">
          The Python package is the pipeline. This script is the machine around it. Re-running the script keeps an existing env file and any Craft binary already in bin/.
        </p>
      </div>
      <ol className="flex flex-col gap-3">
        {STEPS.map((step, index) => (
          <li key={step} className="grid grid-cols-[2rem_1fr] gap-3">
            <span className="font-mono text-xs text-brass tabular-nums">{String(index + 1).padStart(2, "0")}</span>
            <p className="text-sm text-pretty">{step}</p>
          </li>
        ))}
      </ol>
      <div className="flex flex-wrap gap-2">
        <button type="button" className="h-11 border border-fg/15 px-3 text-sm hover:border-brass" onClick={() => onOpen("pod_pipeline/mcp_server.py")}>
          MCP server
        </button>
        <button type="button" className="h-11 border border-fg/15 px-3 text-sm hover:border-brass" onClick={() => onOpen("config/products.json")}>
          products.json
        </button>
        <button type="button" className="h-11 border border-fg/15 px-3 text-sm hover:border-brass" onClick={() => onOpen("deploy/compose.yml")}>
          compose.yml
        </button>
      </div>
      <CodeBlock title={setup.path} source={setup.source} />
      <CodeBlock title={schema.path} source={schema.source} />
    </div>
  );
}

function CodeBlock({ title, source }: { title: string; source: string }) {
  const filename = title.split("/").pop() ?? title;
  return (
    <section>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-mono text-sm">{title}</h3>
        <div className="flex flex-wrap gap-2">
          <CopyButton text={source} />
          <DownloadButton filename={filename} text={source} />
        </div>
      </div>
      <pre className="mt-2 max-h-screen overflow-auto border border-fg/10 p-3 font-mono text-xs leading-relaxed text-fg">{source}</pre>
    </section>
  );
}
