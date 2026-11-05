#!/usr/bin/env node
/**
 * Visual/forensic smoke test for the console.
 *
 * Drives the real page in Chrome (Playwright with the installed channel, no
 * browser download), walks every section, captures screenshots, and fails on
 * console errors, page errors, failed requests, missing content, or horizontal
 * overflow at phone width.
 *
 *   NITRO_PRESET=node-server npm run build
 *   PORT=8090 node .output/server/index.mjs &
 *   node scripts/visual-console-smoke.mjs http://127.0.0.1:8090
 *
 * Output: screenshots/console-<section>-<viewport>.png + a JSON verdict on stdout.
 */
import { mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const SHOTS = join(ROOT, "screenshots");
const URL_UNDER_TEST = process.argv[2] ?? "http://127.0.0.1:8090";
const SECTIONS = ["Board", "Routes", "Sandbox", "Playbook", "Sources"];
const VIEWPORTS = [
  { name: "desktop", width: 1280, height: 800 },
  { name: "mobile", width: 390, height: 844 },
];

mkdirSync(SHOTS, { recursive: true });

const verdict = { url: URL_UNDER_TEST, viewports: {}, ok: true, failures: [] };

function fail(viewport, message) {
  verdict.ok = false;
  verdict.failures.push(`${viewport}: ${message}`);
}

const browser = await chromium.launch({ channel: "chrome", headless: true });
try {
  for (const vp of VIEWPORTS) {
    const context = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
    const page = await context.newPage();
    const consoleErrors = [];
    const pageErrors = [];
    const failedRequests = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });
    page.on("pageerror", (err) => pageErrors.push(err.message));
    page.on("requestfailed", (req) => failedRequests.push(`${req.method()} ${req.url()} ${req.failure()?.errorText ?? ""}`));

    const response = await page.goto(URL_UNDER_TEST, { waitUntil: "networkidle", timeout: 30000 });
    if (!response || response.status() !== 200) fail(vp.name, `homepage status ${response?.status()}`);

    await page.getByRole("heading", { level: 1, name: "Forge" }).waitFor({ timeout: 15000 });
    const heading = await page.getByRole("heading", { level: 1 }).innerText();
    if (!heading.includes("Forge")) fail(vp.name, `heading text was ${JSON.stringify(heading)}`);

    const sections = {};
    for (const label of SECTIONS) {
      const button = page.getByRole("button", { name: label, exact: true });
      if ((await button.count()) !== 1) {
        fail(vp.name, `nav button ${label} not found exactly once`);
        continue;
      }
      await button.click();
      await page.waitForTimeout(150);
      const current = await button.getAttribute("aria-current");
      if (current !== "page") fail(vp.name, `${label} did not become the current section`);

      const main = page.locator("main");
      const text = (await main.innerText()).trim();
      if (text.length < 40) fail(vp.name, `${label} rendered almost nothing (${text.length} chars)`);
      sections[label] = { chars: text.length, firstLine: text.split("\n")[0].slice(0, 120) };

      const shot = join(SHOTS, `console-${label.toLowerCase()}-${vp.name}.png`);
      await page.screenshot({ path: shot, fullPage: false });
    }

    // Back to Board for a stable "home" screenshot per viewport.
    await page.getByRole("button", { name: "Board", exact: true }).click();
    await page.waitForTimeout(150);

    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    if (overflow > 1) fail(vp.name, `horizontal overflow of ${overflow}px`);

    if (consoleErrors.length) fail(vp.name, `console errors: ${consoleErrors.join(" | ")}`);
    if (pageErrors.length) fail(vp.name, `page errors: ${pageErrors.join(" | ")}`);
    if (failedRequests.length) fail(vp.name, `failed requests: ${failedRequests.join(" | ")}`);

    verdict.viewports[vp.name] = {
      status: response?.status() ?? null,
      title: await page.title(),
      overflowPx: overflow,
      consoleErrors,
      pageErrors,
      failedRequests,
      sections,
    };
    await context.close();
  }
} finally {
  await browser.close();
}

process.stdout.write(JSON.stringify(verdict, null, 2) + "\n");
if (!verdict.ok) {
  process.stderr.write(`visual smoke FAILED: ${verdict.failures.join("; ")}\n`);
  process.exit(1);
}
