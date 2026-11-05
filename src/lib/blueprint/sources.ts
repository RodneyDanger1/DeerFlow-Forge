import initPy from "../../../blueprint/files/pod_pipeline/__init__.py?raw";
import configPy from "../../../blueprint/files/pod_pipeline/config.py?raw";
import dbPy from "../../../blueprint/files/pod_pipeline/db.py?raw";
import ingestPy from "../../../blueprint/files/pod_pipeline/ingest.py?raw";
import routesPy from "../../../blueprint/files/pod_pipeline/routes.py?raw";
import runnerPy from "../../../blueprint/files/pod_pipeline/runner.py?raw";
import validatorsPy from "../../../blueprint/files/pod_pipeline/validators.py?raw";
import logfilterPy from "../../../blueprint/files/pod_pipeline/logfilter.py?raw";
import orchestratorPy from "../../../blueprint/files/pod_pipeline/orchestrator.py?raw";
import fourthwallPy from "../../../blueprint/files/pod_pipeline/fourthwall.py?raw";
import workerPy from "../../../blueprint/files/pod_pipeline/worker.py?raw";
import mcpPy from "../../../blueprint/files/pod_pipeline/mcp_server.py?raw";
import schemaSql from "../../../blueprint/files/sql/schema.sql?raw";
import productsJson from "../../../blueprint/files/config/products.json?raw";
import envExample from "../../../blueprint/files/config/pipeline.env.example?raw";
import requirements from "../../../blueprint/files/requirements.txt?raw";
import setupSh from "../../../blueprint/files/deploy/setup-pipeline.sh?raw";
import composeYml from "../../../blueprint/files/deploy/compose.yml?raw";
import dockerfile from "../../../blueprint/files/deploy/Dockerfile?raw";
import mcpMjs from "../../../blueprint/files/deploy/mcp-stdio.mjs?raw";
import mcpService from "../../../blueprint/files/deploy/systemd/pod-mcp.service?raw";
import workerService from "../../../blueprint/files/deploy/systemd/pod-worker.service?raw";
import workerTimer from "../../../blueprint/files/deploy/systemd/pod-worker.timer?raw";
import vectorBin from "../../../blueprint/files/deploy/craft-bin/vectorcraft-cli?raw";
import photoBin from "../../../blueprint/files/deploy/craft-bin/photocraft-cli?raw";
import designBin from "../../../blueprint/files/deploy/craft-bin/designcraft-cli?raw";
import effectBin from "../../../blueprint/files/deploy/craft-bin/effectcraft-cli?raw";
import filmBin from "../../../blueprint/files/deploy/craft-bin/filmcraft-cli?raw";
import conftest from "../../../blueprint/files/tests/conftest.py?raw";
import craftStub from "../../../blueprint/files/tests/stubs/craft_stub.py?raw";
import dockerignore from "../../../blueprint/files/.dockerignore?raw";

export type SourceGroup = "package" | "sql" | "config" | "deploy" | "tests";

export type SourceFile = {
  path: string;
  group: SourceGroup;
  source: string;
};

export const SOURCE_GROUPS: { id: SourceGroup; label: string }[] = [
  { id: "package", label: "Package" },
  { id: "sql", label: "Schema" },
  { id: "config", label: "Config" },
  { id: "deploy", label: "Deploy" },
  { id: "tests", label: "Tests" },
];

export const SOURCES: SourceFile[] = [
  { path: "pod_pipeline/__init__.py", group: "package", source: initPy },
  { path: "pod_pipeline/config.py", group: "package", source: configPy },
  { path: "pod_pipeline/db.py", group: "package", source: dbPy },
  { path: "pod_pipeline/ingest.py", group: "package", source: ingestPy },
  { path: "pod_pipeline/routes.py", group: "package", source: routesPy },
  { path: "pod_pipeline/runner.py", group: "package", source: runnerPy },
  { path: "pod_pipeline/validators.py", group: "package", source: validatorsPy },
  { path: "pod_pipeline/logfilter.py", group: "package", source: logfilterPy },
  { path: "pod_pipeline/orchestrator.py", group: "package", source: orchestratorPy },
  { path: "pod_pipeline/fourthwall.py", group: "package", source: fourthwallPy },
  { path: "pod_pipeline/worker.py", group: "package", source: workerPy },
  { path: "pod_pipeline/mcp_server.py", group: "package", source: mcpPy },
  { path: "sql/schema.sql", group: "sql", source: schemaSql },
  { path: "config/products.json", group: "config", source: productsJson },
  { path: "config/pipeline.env.example", group: "config", source: envExample },
  { path: "requirements.txt", group: "config", source: requirements },
  { path: "deploy/setup-pipeline.sh", group: "deploy", source: setupSh },
  { path: "deploy/compose.yml", group: "deploy", source: composeYml },
  { path: "deploy/Dockerfile", group: "deploy", source: dockerfile },
  { path: "deploy/mcp-stdio.mjs", group: "deploy", source: mcpMjs },
  { path: "deploy/systemd/pod-mcp.service", group: "deploy", source: mcpService },
  { path: "deploy/systemd/pod-worker.service", group: "deploy", source: workerService },
  { path: "deploy/systemd/pod-worker.timer", group: "deploy", source: workerTimer },
  { path: "deploy/craft-bin/vectorcraft-cli", group: "deploy", source: vectorBin },
  { path: "deploy/craft-bin/photocraft-cli", group: "deploy", source: photoBin },
  { path: "deploy/craft-bin/designcraft-cli", group: "deploy", source: designBin },
  { path: "deploy/craft-bin/effectcraft-cli", group: "deploy", source: effectBin },
  { path: "deploy/craft-bin/filmcraft-cli", group: "deploy", source: filmBin },
  { path: ".dockerignore", group: "deploy", source: dockerignore },
  { path: "tests/conftest.py", group: "tests", source: conftest },
  { path: "tests/stubs/craft_stub.py", group: "tests", source: craftStub },
];

export function sourceByPath(path: string): SourceFile {
  const found = SOURCES.find((file) => file.path === path);
  if (!found) throw new Error(path);
  return found;
}
