export type FamilyId = "apparel" | "knitwear" | "accessories" | "odd_3d" | "stationery";

export type RouteStep = {
  name: string;
  module: string;
  command: string;
  output: string;
  validator: string | null;
  timeout: string | null;
};

export type Family = {
  id: FamilyId;
  name: string;
  blanks: string;
  focus: string;
  upload: string;
  note: string;
  traceExtra: string;
  steps: RouteStep[];
};

export const FAMILIES: Family[] = [
  {
    id: "apparel",
    name: "Apparel",
    blanks: "Shaka Wear tees, Shaka Wear hoodies, Bella+Canvas shorts",
    focus: "PhotoCraft and EffectCraft",
    upload: "{build}/apparel_final.png",
    note: "",
    traceExtra: "",
    steps: [
      {
        name: "photocraft_trim",
        module: "photocraft",
        command:
          "photocraft-cli run {art} --cmd image.trim --params '{\"basedOn\":\"transparent\"}' --cmd image.imageSize --params '{\"width\":4200,\"height\":4800,\"resolution\":300,\"resample\":\"lanczos\"}' --cmd edit.convertToProfile --params '{\"profile\":\"srgb\"}' --out {work}/trimmed.png",
        output: "{work}/trimmed.png",
        validator: null,
        timeout: null,
      },
      {
        name: "effectcraft_distress",
        module: "effectcraft",
        command:
          'effectcraft-cli --input {work}/trimmed.png --filter vintage_screen_300 --output {build}/apparel_final.png',
        output: "{build}/apparel_final.png",
        validator: "png_with_alpha",
        timeout: null,
      },
    ],
  },
  {
    id: "knitwear",
    name: "Knitwear",
    blanks: "Knit crewnecks, cardigans, vests",
    focus: "DesignCraft and VectorCraft",
    upload: "{build}/knitwear_final.bmp",
    note: "A BMP stitch grid may be refused by the image library. The run then ends needs_manual_upload and still counts as processed.",
    traceExtra: "",
    steps: [
      {
        name: "designcraft_stitch_matrix",
        module: "designcraft",
        command:
          "designcraft-cli --mode stitch_matrix --input {art} --palette-limit {cfg[palette_limit]} --grid-scale {cfg[knit_grid]} --output {build}/knitwear_final.bmp",
        output: "{build}/knitwear_final.bmp",
        validator: "knit_bmp",
        timeout: null,
      },
    ],
  },
  {
    id: "accessories",
    name: "Accessories",
    blanks: "AS Colour caps, crossbody bags, Under Armour backpacks",
    focus: "DesignCraft",
    upload: "{build}/accessory_final.pdf",
    note: "Safe-zone bounding boxes and kerning live inside DesignCraft. The orchestrator only checks that the PDF has a header and a trailer.",
    traceExtra: "",
    steps: [
      {
        name: "designcraft_template",
        module: "designcraft",
        command:
          'designcraft-cli --template {cfg[template]} --layer artwork --embed {art} --layer care_label --text "{cfg[care_text]}" --output {build}/accessory_final.pdf',
        output: "{build}/accessory_final.pdf",
        validator: "pdf",
        timeout: null,
      },
    ],
  },
  {
    id: "odd_3d",
    name: "Odd / 3D",
    blanks: "Sublimation socks, Arctic Zone tumblers",
    focus: "DesignCraft and EffectCraft",
    upload: "{build}/odd_final.pdf",
    note: "Bleed is 0.25 in. Cylinder taper is a separate EffectCraft step so a bad wrap never reaches the tumbler deform.",
    traceExtra: "",
    steps: [
      {
        name: "designcraft_wrap_tile",
        module: "designcraft",
        command:
          "designcraft-cli --mode wrap_tile --bleed {cfg[bleed_in]} --input {art} --output {work}/odd/tiled.pdf",
        output: "{work}/odd/tiled.pdf",
        validator: "pdf",
        timeout: null,
      },
      {
        name: "effectcraft_cylinder_taper",
        module: "effectcraft",
        command:
          "effectcraft-cli --cylinder-taper --input {work}/odd/tiled.pdf --output {build}/odd_final.pdf",
        output: "{build}/odd_final.pdf",
        validator: "pdf",
        timeout: null,
      },
    ],
  },
  {
    id: "stationery",
    name: "Stationery",
    blanks: "Karst bound notebooks",
    focus: "DesignCraft and FilmCraft",
    upload: "{build}/print_ready_stationery.pdf",
    note: "The reel is a marketing file, not the Fourthwall upload. Packing slips are not built on this route — a cover exists before any order does.",
    traceExtra: "",
    steps: [
      {
        name: "designcraft_cover",
        module: "designcraft",
        command:
          "designcraft-cli --input {cfg[cover_template]} --embed {art} --output {build}/print_ready_stationery.pdf",
        output: "{build}/print_ready_stationery.pdf",
        validator: "pdf",
        timeout: null,
      },
      {
        name: "filmcraft_reel",
        module: "filmcraft",
        command:
          "filmcraft-cli --template {cfg[reel_template]} --asset-layer product_front --input {build}/print_ready_stationery.pdf --render-preset {cfg[reel_preset]} --output {build}/promo_reel.mp4",
        output: "{build}/promo_reel.mp4",
        validator: "mp4",
        timeout: "1800s",
      },
    ],
  },
];

export const ASSUMPTIONS = [
  "The VectorCraft contract is no longer invented. It is the measured 0.21.1 run contract: run --in --cmd select.all --cmd imageTrace.make --params ... --cmd imageTrace.expand --export.",
  "Exit code 1 on that trace is the only automatic fallback. Any other trace exit fails the run.",
  "The raster fallback is PhotoCraft run --cmd image.imageSize --cmd edit.convertToProfile --out; it writes one flat PNG.",
  "Knitwear's factory palette cap is carried inside the trace JSON colors value; there is no --palette-limit CLI flag.",
  "The stationery cover adds --embed and drops --variable-data order_id. There is no order yet.",
  "VectorCraft and PhotoCraft are installed; DesignCraft, EffectCraft and FilmCraft are absent and are named refusals until installed.",
  "The console is a viewer; it does not execute the pipeline or claim that the displayed commands have run.",
];

const CFG: Record<string, string> = {
  palette_limit: "6",
  trace_mode: "color",
  trace_palette: "limited",
  trace_colors: "12",
  trace_paths: "65",
  trace_corners: "45",
  trace_noise: "16",
  knit_grid: "112x140",
  template: "fourthwall_crossbody_v1",
  care_text: "100% Polyester",
  bleed_in: "0.25",
  cover_template: "notebook_cover_template",
  reel_template: "reel_promo_9_16",
  reel_preset: "tiktok_1080p",
  fallback_dpi: "600",
};

export const RUN_ID = "8f3c1a9b-4e20-4c11-9a77-0b1d2e3f4a5b";
export const ROOT = "/opt/pod-pipeline";

export const TREE = `/opt/pod-pipeline
├── bin/                         Craft CLIs, first on PATH
├── config/pipeline.env          systemd EnvironmentFile
├── config/products.json         template ids, knit grid, care text
├── data/inbox/<account_id>/     scan_inbox, after the file settles
├── sandbox/<run_id>/            scratch; deleted when the run succeeds
├── build/<run_id>/              fsynced finals, kept
├── logs/jobs/<run_id>/          one capped log per attempt
├── sql/schema.sql
├── pod_pipeline/                orchestrator, MCP, Fourthwall client
├── tests/stubs/craft_stub.py    test double only
└── deploy/                      setup-pipeline.sh, compose, systemd`;

export const DOCKER_ARGV = `docker run --rm --init --name pod-<id> \\
  --memory 2g --memory-swap 2g \\
  --cpus 1.5 --cpu-shares 256 \\
  --pids-limit 256 --network none \\
  --cap-drop ALL --security-opt no-new-privileges \\
  --read-only --tmpfs /tmp:rw,size=512m -e HOME=/tmp \\
  --user <uid>:<gid> \\
  -v <work>:<work>:rw -v <build>:<build>:rw -w <work> \\
  pod-craft-runner:latest \\
  <craft argv>`;

export const NATIVE_ARGV = "nice -n 10 ionice -c 3 <craft argv>";

export type PlanStep = {
  id: string;
  module: string;
  title: string;
  command: string;
  sandbox: string;
  note: string;
  result: string;
  failed: boolean;
};

function resolve(template: string, vars: Record<string, string>): string {
  return template.replace(/\{cfg\[(\w+)\]\}|\{(\w+)\}/g, (full, cfgKey: string | undefined, key: string | undefined) => {
    if (cfgKey) return vars[cfgKey] ?? full;
    if (key) return vars[key] ?? full;
    return full;
  });
}

function sandboxFor(kind: "db" | "craft" | "net", docker: boolean): string {
  if (kind === "db") return "postgres";
  if (kind === "net") return "host network";
  return docker ? "docker 2g · 1.5 cpu · net none" : "nice -n 10 · ionice idle";
}

export function familyById(id: FamilyId): Family {
  const found = FAMILIES.find((family) => family.id === id);
  if (!found) throw new Error(id);
  return found;
}

export function buildPlan(familyId: FamilyId, traceFails: boolean, docker: boolean): PlanStep[] {
  const family = familyById(familyId);
  const work = `${ROOT}/sandbox/${RUN_ID}`;
  const build = `${ROOT}/build/${RUN_ID}`;
  const src = `${work}/input.png`;
  const art = traceFails ? `${work}/raster.png` : `${work}/traced.svg`;
  const vars: Record<string, string> = { ...CFG, src, art, work, build, run_id: RUN_ID, fallback_dpi: CFG.fallback_dpi };
  const steps: PlanStep[] = [];
  const push = (step: PlanStep) => steps.push(step);

  // Family-specific trace colours: knitwear must honour the factory palette cap.
  const traceColors = familyId === "knitwear" ? CFG.palette_limit : CFG.trace_colors;
  const traceParams = JSON.stringify({
    params: {
      mode: CFG.trace_mode,
      palette: CFG.trace_palette,
      colors: Number(traceColors),
      paths: Number(CFG.trace_paths),
      corners: Number(CFG.trace_corners),
      noise: Number(CFG.trace_noise),
      ignoreWhite: true,
      method: "abutting",
      fills: true,
      strokes: false,
      shapes: false,
      autoGrouping: false,
      gradients: false,
    },
  });

  push({
    id: "claim",
    module: "db",
    title: "claim_run",
    command: "UPDATE processing_jobs SET status=running, pid, started_at WHERE status=queued FOR UPDATE SKIP LOCKED",
    sandbox: sandboxFor("db", docker),
    note: "The MCP child and the minute drain cannot take the same run.",
    result: "claimed orchestrator row",
    failed: false,
  });
  push({
    id: "stage",
    module: "ingest",
    title: "stage_input",
    command: `sha256 copy ${src}`,
    sandbox: sandboxFor("db", docker),
    note: "A hash mismatch quarantines the asset. Craft is not called.",
    result: "sha256 matches ingested_assets",
    failed: false,
  });

  const trace = [
    "vectorcraft-cli run",
    `--in ${src}`,
    "--cmd select.all",
    "--cmd imageTrace.make",
    `--params '${traceParams}'`,
    "--cmd imageTrace.expand",
    `--export ${work}/traced.svg`,
    `--export ${work}/traced.pdf`,
  ];
  push({
    id: "trace",
    module: "vectorcraft",
    title: "vector_trace",
    command: trace.join(" "),
    sandbox: sandboxFor("craft", docker),
    note: "Tier 0. Only exit code 1 switches to the raster fallback.",
    result: traceFails
      ? "exit 1 · ERROR: trace failed: path simplification diverged"
      : `exit 0 · fsync ${work}/traced.svg`,
    failed: traceFails,
  });

  if (traceFails) {
    push({
      id: "fallback",
      module: "photocraft",
      title: "raster_fallback",
      command: [
        "photocraft-cli run",
        src,
        "--cmd image.imageSize",
        `--params '{"resolution":${CFG.fallback_dpi},"resample":"lanczos"}'`,
        "--cmd edit.convertToProfile",
        `--params '{"profile":"srgb"}'`,
        `--out ${work}/raster.png`,
      ].join(" "),
      sandbox: sandboxFor("craft", docker),
      note: "Tier 1. trace_state becomes raster_fallback. Later steps receive the PNG as {art}.",
      result: `exit 0 · fsync ${work}/raster.png`,
      failed: false,
    });
  }

  for (const step of family.steps) {
    const bits = [
      step.validator ? `validator ${step.validator}` : "no validator",
      "fsync file + directory",
    ];
    if (step.timeout) bits.push(`timeout ${step.timeout}`);
    push({
      id: step.name,
      module: step.module,
      title: step.name,
      command: resolve(step.command, vars),
      sandbox: sandboxFor("craft", docker),
      note: bits.join(" · "),
      result: `exit 0 · fsync ${resolve(step.output, vars)}`,
      failed: false,
    });
  }

  const upload = resolve(family.upload, vars);
  push({
    id: "upload-url",
    module: "fourthwall",
    title: "media.upload_url",
    command: `POST /open-api/v1.0/media/upload-url  ${upload}`,
    sandbox: sandboxFor("net", docker),
    note: "Body is fileName, contentType, size. The client allows 20 of these per minute.",
    result: "201 · uploadUrl + fileUrl",
    failed: false,
  });
  push({
    id: "gcs",
    module: "fourthwall",
    title: "media.gcs_put",
    command: "PUT <uploadUrl>  Content-Type + x-goog-content-length-range",
    sandbox: sandboxFor("net", docker),
    note: "No Fourthwall credentials on this hop. The storage host must not see the API secret.",
    result: "200 · bytes match the signed size",
    failed: false,
  });
  push({
    id: "register",
    module: "fourthwall",
    title: "media.register",
    command: "POST /open-api/v1.0/media/images  {fileUrl, width, height}",
    sandbox: sandboxFor("net", docker),
    note: "The returned id is the imageId stored on fourthwall_products.media_id.",
    result: "200 · imageId",
    failed: false,
  });
  push({
    id: "create",
    module: "fourthwall",
    title: "product.create",
    command: "POST /open-api/v1.0/products  type=design  publishOnCreate=false",
    sandbox: sandboxFor("net", docker),
    note: "Not retried on 5xx. An empty fourthwall_template_id fails the run before this call.",
    result: "201 · productId · publish_state draft",
    failed: false,
  });
  push({
    id: "finish",
    module: "db",
    title: "finish_run",
    command: "orchestrator row succeeded · asset processed · sandbox removed",
    sandbox: sandboxFor("db", docker),
    note: traceFails ? "trace_state stays raster_fallback." : "trace_state stays traced.",
    result: "build/ kept · auto_publish is false, so the product stays draft",
    failed: false,
  });

  return steps;
}
