/**
 * Interop contract for the stdio MCP bridge (blueprint/files/deploy/mcp-stdio.mjs).
 *
 * MCP's stdio transport is newline-delimited JSON. DeerFlow's client sends that
 * form; the Python server mirrors whatever framing it receives. A bridge that
 * replies with Content-Length frames to a newline-delimited client produces
 * bytes the client cannot parse, so the tool surface is unreachable — the
 * defect this file pins.
 */
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(dirname(fileURLToPath(import.meta.url))));
const BRIDGE = join(ROOT, "blueprint", "files", "deploy", "mcp-stdio.mjs");

/** Fake pipeline MCP server: echoes each JSON-RPC request back with result.handled=true. */
function startFakeServer() {
  const server = createServer((req, res) => {
    const chunks = [];
    req.on("data", (c) => chunks.push(c));
    req.on("end", () => {
      const msg = JSON.parse(Buffer.concat(chunks).toString("utf8"));
      res.writeHead(200, { "content-type": "application/json" });
      res.end(JSON.stringify({ jsonrpc: "2.0", id: msg.id, result: { handled: true, method: msg.method } }));
    });
  });
  return new Promise((resolve) => {
    server.listen(0, "127.0.0.1", () => {
      const { port } = server.address();
      resolve({ server, port });
    });
  });
}

function startBridge(port) {
  const child = spawn(process.execPath, [BRIDGE], {
    env: { ...process.env, POD_MCP_URL: `http://127.0.0.1:${port}/` },
    stdio: ["pipe", "pipe", "pipe"],
  });
  let out = Buffer.alloc(0);
  child.stdout.on("data", (c) => {
    out = Buffer.concat([out, c]);
  });
  let err = "";
  child.stderr.on("data", (c) => {
    err += String(c);
  });
  return {
    child,
    stdout: () => out,
    stderr: () => err,
    waitForBytes: async (predicate, timeoutMs = 4000) => {
      const started = Date.now();
      while (!predicate(out)) {
        if (Date.now() - started > timeoutMs) {
          throw new Error(`timed out waiting for bridge output; got ${JSON.stringify(out.toString("utf8"))} stderr=${err}`);
        }
        await new Promise((r) => setTimeout(r, 25));
      }
      return out;
    },
  };
}

test("newline-delimited input gets a newline-delimited reply (MCP stdio)", async () => {
  const { server, port } = await startFakeServer();
  const bridge = startBridge(port);
  try {
    const msg = { jsonrpc: "2.0", id: 1, method: "tools/list" };
    bridge.child.stdin.write(JSON.stringify(msg) + "\n");
    await bridge.waitForBytes((b) => b.includes(0x0a) && b.toString("utf8").includes('"handled":true'));
    const text = bridge.stdout().toString("utf8");
    assert.equal(
      text.includes("Content-Length:"),
      false,
      `bridge must mirror newline framing, got framed reply: ${JSON.stringify(text)}`,
    );
    const first = text.split("\n").filter(Boolean)[0];
    assert.deepEqual(JSON.parse(first), { jsonrpc: "2.0", id: 1, result: { handled: true, method: "tools/list" } });
  } finally {
    bridge.child.kill();
    server.close();
  }
});

test("Content-Length input still gets a Content-Length reply", async () => {
  const { server, port } = await startFakeServer();
  const bridge = startBridge(port);
  try {
    const msg = { jsonrpc: "2.0", id: 2, method: "ping" };
    const body = JSON.stringify(msg);
    bridge.child.stdin.write(`Content-Length: ${Buffer.byteLength(body)}\r\n\r\n${body}`);
    await bridge.waitForBytes((b) => b.toString("utf8").includes('"handled":true'));
    const text = bridge.stdout().toString("utf8");
    assert.match(text, /^Content-Length: \d+\r\n\r\n/);
    const payload = text.split("\r\n\r\n")[1];
    assert.deepEqual(JSON.parse(payload), { jsonrpc: "2.0", id: 2, result: { handled: true, method: "ping" } });
  } finally {
    bridge.child.kill();
    server.close();
  }
});

test("notifications (no id) are forwarded but produce no reply", async () => {
  const { server, port } = await startFakeServer();
  const bridge = startBridge(port);
  try {
    const note = { jsonrpc: "2.0", method: "notifications/initialized" };
    bridge.child.stdin.write(JSON.stringify(note) + "\n");
    // Follow with a request so we know the note was processed first.
    bridge.child.stdin.write(JSON.stringify({ jsonrpc: "2.0", id: 3, method: "ping" }) + "\n");
    await bridge.waitForBytes((b) => b.toString("utf8").includes('"id":3'));
    const text = bridge.stdout().toString("utf8");
    assert.equal(text.includes("notifications/initialized"), false);
    assert.equal(text.split("\n").filter(Boolean).length, 1);
  } finally {
    bridge.child.kill();
    server.close();
  }
});
