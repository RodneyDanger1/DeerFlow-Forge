import assert from "node:assert/strict";
import { existsSync, mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { cleanBuildCaches } from "./build-vps.mjs";

test("cleanBuildCaches removes every preset-sensitive build cache", () => {
  const root = mkdtempSync(join(tmpdir(), "build-vps-"));
  const dirs = [".output", ".vercel", ".tanstack", "dist", "node_modules/.nitro", "node_modules/.vite"];
  for (const rel of dirs) {
    mkdirSync(join(root, rel), { recursive: true });
    writeFileSync(join(root, rel, "stale.txt"), "x");
  }
  const removed = cleanBuildCaches(root);
  assert.deepEqual([...removed].sort(), [...dirs].sort());
  for (const rel of dirs) assert.equal(existsSync(join(root, rel)), false, `${rel} survived the clean`);
});

test("cleanBuildCaches tolerates a tree with none of the caches", () => {
  const root = mkdtempSync(join(tmpdir(), "build-vps-empty-"));
  assert.deepEqual(cleanBuildCaches(root).length, 6);
});
