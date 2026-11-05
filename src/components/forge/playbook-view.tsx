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

/**
 * Template shortlist computed from the full Fourthwall catalogue (623 templates,
 * 25 API pages). The vault note and the pipeline snapshot hold every row; these
 * are the five the pipeline can actually publish through the design-product API.
 *
 * A template is usable only when supportsBackendRendering is true and the
 * production method is not KNITTING: the provider's backend must render the
 * uploaded region itself. Knitwear has no such template today, so the route
 * stays blocked by a named refusal instead of a guessed id.
 */
const FOURTHWALL_ROUTES: ReadonlyArray<{
  readonly route: string;
  readonly template: string | null;
  readonly product: string;
  readonly method: string;
  readonly price: string;
  readonly note: string;
}> = [
  {
    route: "apparel",
    template: "pro_e4677535402b4eeb81",
    product: "Gildan Heavyweight T-Shirt",
    method: "DTG",
    price: "$9.50",
    note: "Cheapest backend-renderable tee; front region takes the trimmed PNG.",
  },
  {
    route: "knitwear",
    template: null,
    product: "No renderable knit template exists",
    method: "KNITTING",
    price: "—",
    note: "All 13 knit templates are KNITTING with backend rendering off. Leave the id unset; the factory BMP path is separate from POST /products.",
  },
  {
    route: "accessories",
    template: "pro_zvJp6rm7Rd2ILcwdxA16cA",
    product: "BagBase Cotton Color Tote Bag",
    method: "DTFX",
    price: "$9.98",
    note: "No crossbody template exists in the catalogue; the tote is the closest front-region bag.",
  },
  {
    route: "odd_3d",
    template: "pro_15bc29bc8a324d449d",
    product: "Enhanced Matte Paper Poster",
    method: "PRINTED",
    price: "$5.50",
    note: "Flat printable target for the tiled PDF output.",
  },
  {
    route: "stationery",
    template: "pro_JBZ8pRVlR-m84AwNl7WbnQ",
    product: "Spiral Bound Notebook - Graph",
    method: "PRINTED",
    price: "$10.95",
    note: "Cover-art notebook; backend rendering supported.",
  },
];

const CATALOGUE_NOTE = "/srv/vaults/storefront/30-reference/fourthwall/FOURTHWALL PRODUCTS AND INFO.md";
const CATALOGUE_SNAPSHOT = "/opt/pod-pipeline/config/fourthwall-product-templates.json";
const TEMPLATE_DETAILS = "/opt/pod-pipeline/config/fourthwall-template-details.json";
const ART_SOP = "/srv/vaults/storefront/10-sops/art-to-print-prep.md";
const ART_TOOL = "tools/prep_print_art.py";

/**
 * Art-to-print procedure, generalised from the first production run.
 * Thresholds shown are starting defaults; the tool measures the image and
 * refuses empty/full-frame masks instead of trusting them blind.
 */
const ART_STEPS = [
  "Pick the mask mode from the art: glow (colourful subject on dark), lineart --invert (ink on light) or none (deliberate full bleed).",
  "Take geometry from the provider: areas come from config/fourthwall-template-details.json (areaGeometry has inches, pixels and DPI per region).",
  "Run tools/prep_print_art.py: measured mask, crop, optional bloom, centre on a 300 DPI canvas, previews on black and white, JSON report.",
  "Check the gates in the report: coverage 0.005–0.62, non-empty bbox, upscale warning above 2.5x, canvas matches the provider area.",
  "Upload through the storefront's own Fourthwall client, create hidden, publish with a separate state change, then run the catalogue sync.",
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
      <section className="flex flex-col gap-3 border-t border-fg/10 pt-6">
        <div>
          <h3 className="text-lg font-medium">Fourthwall template shortlist</h3>
          <p className="mt-1 max-w-3xl text-sm text-pretty text-muted">
            Computed from the full provider catalogue (623 templates over 25 API pages). A template is publishable only when
            backend rendering is on and the production method is not KNITTING. Every row lives in the vault note and the
            pipeline snapshot below.
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left text-sm">
            <thead>
              <tr className="border-b border-fg/15 font-mono text-xs uppercase tracking-wide text-muted">
                <th className="py-2 pr-4">Route</th>
                <th className="py-2 pr-4">Template id</th>
                <th className="py-2 pr-4">Product</th>
                <th className="py-2 pr-4">Method</th>
                <th className="py-2">Note</th>
              </tr>
            </thead>
            <tbody>
              {FOURTHWALL_ROUTES.map((entry) => (
                <tr key={entry.route} className="border-b border-fg/10 align-top">
                  <td className="py-2 pr-4 font-mono text-xs">{entry.route}</td>
                  <td className="py-2 pr-4 font-mono text-xs">{entry.template ?? "—"}</td>
                  <td className="py-2 pr-4">
                    {entry.product}
                    <span className="ml-2 text-xs text-muted">{entry.price}</span>
                  </td>
                  <td className="py-2 pr-4 font-mono text-xs">{entry.method}</td>
                  <td className="py-2 max-w-xl text-xs text-pretty text-muted">{entry.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <dl className="grid gap-2 text-xs sm:grid-cols-2">
          <div>
            <dt className="font-mono text-muted">full catalogue</dt>
            <dd className="font-mono break-all">{CATALOGUE_NOTE}</dd>
          </div>
          <div>
            <dt className="font-mono text-muted">pipeline snapshot (JSON)</dt>
            <dd className="font-mono break-all">{CATALOGUE_SNAPSHOT}</dd>
          </div>
        </dl>
        <p className="max-w-3xl text-xs text-pretty text-muted">
          Create products hidden (<span className="font-mono">publishOnCreate:false</span>) and publish with a separate state
          change. The shop&apos;s rate limits are shared with the storefront&apos;s Imagineer agent: 5 product creates per minute,
          20 upload URLs per minute.
        </p>
      </section>
      <section className="flex flex-col gap-3 border-t border-fg/10 pt-6">
        <div>
          <h3 className="text-lg font-medium">Art-to-print prep</h3>
          <p className="mt-1 max-w-3xl text-sm text-pretty text-muted">
            Raster art → provider-ready print master, with measured masks and hard gates instead of magic numbers. The full
            procedure, traps and worked example live in the vault SOP below.
          </p>
        </div>
        <ol className="flex flex-col gap-2">
          {ART_STEPS.map((step, index) => (
            <li key={step} className="grid grid-cols-[2rem_1fr] gap-3">
              <span className="font-mono text-xs text-brass tabular-nums">{String(index + 1).padStart(2, "0")}</span>
              <p className="text-sm text-pretty">{step}</p>
            </li>
          ))}
        </ol>
        <pre className="overflow-x-auto border border-fg/10 p-3 font-mono text-xs leading-relaxed">{`cd /opt/pod-pipeline
set -a; . config/pipeline.env; set +a
.venv/bin/python -m tools.fetch_fourthwall_details
.venv/bin/python -m tools.prep_print_art \\
  --input data/ai-uploads/art.jpg \\
  --template pro_e4677535402b4eeb81 --area front_large --dpi 300 \\
  --mode glow --brightness 1.18 --saturation 1.25 --bloom 6 \\
  --output data/ai-uploads/print_master.png \\
  --report-json data/ai-uploads/print_master.report.json \\
  --preview-dir data/ai-uploads/previews`}</pre>
        <dl className="grid gap-2 text-xs sm:grid-cols-2">
          <div>
            <dt className="font-mono text-muted">procedure / traps (vault)</dt>
            <dd className="font-mono break-all">{ART_SOP}</dd>
          </div>
          <div>
            <dt className="font-mono text-muted">tool + template geometry</dt>
            <dd className="font-mono break-all">{ART_TOOL} · {TEMPLATE_DETAILS}</dd>
          </div>
        </dl>
        <p className="max-w-3xl text-xs text-pretty text-muted">
          Traps encoded in the SOP: provider mockups are decorative and never prove print scale; potrace flattens glow into a
          silhouette so PNG at 300 DPI is the print artifact; transparent padding shrinks the design; licensed wordmarks must not
          be sold.
        </p>
      </section>
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
