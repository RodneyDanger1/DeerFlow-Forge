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
const ART_LEARNING = "/srv/vaults/storefront/30-reference/art-learning/00-ART-LEARNING-INDEX.md";
const ART_TOOL = "tools/prep_print_art.py";
const VECTOR_TOOL = "tools/vectorize_art.py";
const CRAFT_TRACE_TOOL = "tools/craft_trace.py";
const VECTORCRAFT_CLI = "/opt/craft/vectorcraft/vectorcraft-0.21.1-linux-x86_64/bin/vectorcraft-cli";
const ARTCRAFT_ATLAS = "/srv/vaults/storefront/30-reference/art-learning/07-ARTCRAFT-COMMAND-ATLAS.md";
const ARTCRAFT_WORKFLOWS = "/srv/vaults/storefront/30-reference/art-learning/09-WORKFLOWS.md";
const SKILLS_DIR = "blueprint/files/skills";
const SKILLS_RUNTIMES = "DSH: %USERPROFILE%\\.dsh\\skills · Hermes: %USERPROFILE%\\.hermes\\skills";
const IMAGINEER_TEMPLATES = "/srv/vaults/storefront/30-reference/art-learning/10-IMAGINEER-PROMPT-TEMPLATES.md";

/**
 * Art-to-print procedure, generalised from the first production run.
 * Thresholds shown are starting defaults; the tool measures the image and
 * refuses empty/full-frame masks instead of trusting them blind.
 */
const ART_STEPS = [
  "Pick the mask mode from the art: glow (colourful subject on dark), lineart --invert (ink on light), white (remove every neutral white, keep cream lettering) or alpha (input already cut out).",
  "Take geometry from the provider: areas come from config/fourthwall-template-details.json (areaGeometry has inches, pixels and DPI per region).",
  "Run tools/prep_print_art.py: measured mask, rim/speck/edge-fleck cleanup, crop, saturation and unsharp restore, 300 DPI canvas, previews, JSON report.",
  "Flat art: run tools/vectorize_art.py (binary alpha -> magenta key -> vtracer -> rsvg at print pixels). Textured/painterly art: do not auto-trace, use a high-res raster or regenerate.",
  "Check the gates in the report: coverage 0.005–0.62, non-empty bbox, upscale warning above 2.5x, canvas matches the provider area.",
  "Check the provider's artwork rules for the method: PNG/JPG only, DTG solid shapes, embroidery minimums (see traps).",
  "Upload hidden, publish with a separate state change, hide older versions, wait for the storefront cache, sync, then verify /shop and every product page. Order a sample before calling it print-verified.",
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
            <dt className="font-mono text-muted">tools + template geometry</dt>
            <dd className="font-mono break-all">{ART_TOOL} · {VECTOR_TOOL} · {TEMPLATE_DETAILS}</dd>
          </div>
          <div>
            <dt className="font-mono text-muted">full knowledge base (vault)</dt>
            <dd className="font-mono break-all">{ART_LEARNING}</dd>
          </div>
          <div>
            <dt className="font-mono text-muted">agent instructions</dt>
            <dd className="font-mono break-all">30-reference/art-learning/05-IMAGINEER-INSTRUCTIONS.md</dd>
          </div>
        </dl>
        <p className="max-w-3xl text-xs text-pretty text-muted">
          Verified against Fourthwall&apos;s artwork docs (2026-11-05): uploads must be PNG or JPG — SVG, AI, PDF, PSD and TIFF
          are rejected; DTG wants solid shapes with strong outlines, not glow or semi-transparent effects; embroidery allows at
          most 6 thread colours with capitals at least 0.3 in, lowercase 0.25 in and strokes at least 0.05 in; apparel needs at
          least 150 DPI at print size (300 for posters, stickers and mugs). White removal: remove every neutral white pixel, not
          just the border, unless the owner says otherwise. Vectorise flat art (tools/vectorize_art.py) and render at print size;
          automated tracing of textured or painterly art degrades (banding, key-colour edge specks) — regenerate that art at a
          higher resolution instead. The mockup is a cut-off check, not a print-size proof — order a sample before launch.
          Licensed wordmarks must not be sold.
        </p>
      </section>
      <section className="flex flex-col gap-3 border-t border-fg/10 pt-6">
        <div>
          <h3 className="text-lg font-medium">ArtCraft Image Trace (the real Adobe counterpart)</h3>
          <p className="mt-1 max-w-3xl text-sm text-pretty text-muted">
            VectorCraft and PhotoCraft are the open-source, agent-drivable counterparts to Illustrator and
            Photoshop: 918 VectorCraft commands plus a 84 KB PhotoCraft engine, each callable from the headless
            CLI, MCP server or JSON control channel. Its <span className="font-mono">imageTrace.make</span> is
            Illustrator&apos;s Image Trace panel (mode, palette, colours, paths, corners, noise, method,
            ignore white, fills/strokes, snap shapes). Use it for the illustration; retype AI lettering with a
            real font — tracing cannot repair diffusion-eroded text.
          </p>
        </div>
        <pre className="overflow-x-auto border border-fg/10 p-3 font-mono text-xs leading-relaxed">{`# VectorCraft Image Trace, driven by CLI steps (Illustrator-compatible params)
${'"'}{"command":"select.all"}},
{"command":"imageTrace.make","params":{"params":{
  "mode":"color","palette":"limited","colors":12,"paths":65,"corners":45,
  "noise":16,"ignoreWhite":true,"method":"abutting","fills":true,"strokes":false}}},
{"command":"imageTrace.expand"}

# full production master (cutout -> trace -> retype -> 300 DPI canvas -> 10 checks)
cd /opt/pod-pipeline
.venv/bin/python -m tools.craft_trace \\
  --input data/ai-uploads/art.jpg --template <id> --area front_large --dpi 300 --print-width-in 8 \\
  --retype-json config/<design>-retype.json \\
  --output data/ai-uploads/master.png --svg data/ai-uploads/master.svg \\
  --report-json data/ai-uploads/master.json --preview-dir data/ai-uploads/previews_master`}</pre>
        <dl className="grid gap-2 text-xs sm:grid-cols-2">
          <div>
            <dt className="font-mono text-muted">VectorCraft CLI</dt>
            <dd className="font-mono break-all">{VECTORCRAFT_CLI}</dd>
          </div>
          <div>
            <dt className="font-mono text-muted">production tool</dt>
            <dd className="font-mono break-all">{CRAFT_TRACE_TOOL}</dd>
          </div>
          <div>
            <dt className="font-mono text-muted">command atlas (918 + PC)</dt>
            <dd className="font-mono break-all">{ARTCRAFT_ATLAS}</dd>
          </div>
          <div>
            <dt className="font-mono text-muted">workflows + Imagineer templates</dt>
            <dd className="font-mono break-all">{ARTCRAFT_WORKFLOWS} · {IMAGINEER_TEMPLATES}</dd>
          </div>
          <div>
            <dt className="font-mono text-muted">agent skills (22, DSH + Hermes)</dt>
            <dd className="font-mono break-all">{SKILLS_DIR} · {SKILLS_RUNTIMES}</dd>
          </div>
        </dl>
        <p className="max-w-3xl text-xs text-pretty text-muted">
          Coordinate trap that cost a day: prep crops to the subject bbox and re-centres, and the traced SVG keeps the
          full canvas, so every box measured on the original art must be transformed through the prep report before
          erasing or retyping text. The 10 gates: white residual, specks, coverage, 300 DPI, canvas geometry, fill
          colour count, edge definition, hard alpha edges, transparent corners, retyped text present. A failed gate is
          a failed run. Full command atlas (918 commands in 64 groups), the execute-verified command/MCP playbook
          (VectorCraft 33 + PhotoCraft 26 MCP tools), 1,016 canonical tutorial URLs (18 pages fetched and read),
          the seven core workflows plus apparel/embroidery/vectorising/ads/shipping-insert workflows, and the 22
          agent skills in WORKFLOW_SKILLS live in the vault Art Learning folder; see 15-APPAREL-PRINT-MARKETING-WORKFLOWS.md,
          16-TUTORIAL-WAVE4.md, 17-CRAFT-COMMAND-PLAYBOOK.md, 18-KNOWLEDGE-MAP-AND-AUDIT.md, 19-SKILLS-QUALITY-AUDIT.md and 20-SKILLS-CATALOG.md.
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
