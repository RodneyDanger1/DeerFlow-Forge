#!/usr/bin/env node
/**
 * Production build for a plain Node host (VPS), not Vercel.
 *
 * Switching Nitro presets reuses caches that embed the *previous* build's
 * hashed client asset names: node_modules/.nitro keeps the client manifest, so
 * a node-server build can stamp a CSS filename that this build did not emit and
 * the deployed page renders unstyled (verified: /assets/styles-*.css -> 404).
 * Clear every build cache first, then build with the node-server preset.
 *
 *   npm run build:vps
 *   PORT=8090 HOST=127.0.0.1 node .output/server/index.mjs
 */
import { spawnSync } from "node:child_process";
import { rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const CACHES = [".output", ".vercel", ".tanstack", "dist", "node_modules/.nitro", "node_modules/.vite"];

export function cleanBuildCaches(root = ROOT) {
  const removed = [];
  for (const rel of CACHES) {
    const target = join(root, rel);
    rmSync(target, { recursive: true, force: true });
    removed.push(rel);
  }
  return removed;
}

/**
 * How to re-invoke npm from Node.
 *
 * A bare spawn of `npm.cmd` fails on Windows with EINVAL (Node cannot execute a
 * batch shim without a shell). npm sets npm_execpath when it runs this script,
 * so prefer `node <npm-cli.js> run build` and fall back to a shell only when the
 * variable is missing (invoked directly with `node scripts/build-vps.mjs`).
 */
function npmInvocation() {
  const execPath = process.env.npm_execpath;
  if (execPath) return { cmd: process.execPath, args: [execPath, "run", "build"], shell: false };
  const npm = process.platform === "win32" ? "npm.cmd" : "npm";
  return { cmd: npm, args: ["run", "build"], shell: process.platform === "win32" };
}

const isMain = process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1];
if (isMain) {
  const removed = cleanBuildCaches();
  process.stderr.write(`[build-vps] cleared ${removed.join(", ")}\n`);
  const { cmd, args, shell } = npmInvocation();
  const result = spawnSync(cmd, args, {
    cwd: ROOT,
    stdio: "inherit",
    shell,
    env: { ...process.env, NITRO_PRESET: "node-server" },
  });
  if (result.error) {
    process.stderr.write(`[build-vps] failed to start npm: ${result.error.message}\n`);
    process.exit(1);
  }
  process.exit(result.status ?? 1);
}
