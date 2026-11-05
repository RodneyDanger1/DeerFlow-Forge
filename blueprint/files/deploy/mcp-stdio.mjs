#!/usr/bin/env node
// stdio MCP bridge. DeerFlow speaks Content-Length frames (or one JSON object
// per line) on stdin. Each message is POSTed to the Python server and the
// response is written back as a Content-Length frame.
//
// Tools live in pod_pipeline/mcp_server.py:
//   list_pending_assets, trigger_pipeline_job, get_fourthwall_status
//
//   node deploy/mcp-stdio.mjs
//   POD_MCP_URL defaults to http://127.0.0.1:8765/

import { Buffer } from "node:buffer";

const url = process.env.POD_MCP_URL ?? "http://127.0.0.1:8765/";

function createReader(stream) {
  let buf = Buffer.alloc(0);
  let ended = false;
  /** @type {Array<() => void>} */
  const pending = [];

  stream.on("data", (chunk) => {
    buf = Buffer.concat([buf, chunk]);
    while (pending.length) {
      const wake = pending.shift();
      if (wake) wake();
    }
  });
  stream.on("end", () => {
    ended = true;
    while (pending.length) {
      const wake = pending.shift();
      if (wake) wake();
    }
  });

  function wait() {
    return new Promise((resolve) => {
      pending.push(resolve);
    });
  }

  function take(n) {
    const out = Buffer.from(buf.subarray(0, n));
    buf = buf.subarray(n);
    return out;
  }

  async function fill(n) {
    while (buf.length < n) {
      if (ended) return false;
      await wait();
    }
    return true;
  }

  return {
    async readMessage() {
      if (!(await fill(1))) return null;
      if (buf[0] === 0x7b) {
        while (buf.indexOf(0x0a) < 0) {
          if (!(await fill(buf.length + 1))) return null;
        }
        const line = take(buf.indexOf(0x0a));
        take(1);
        return JSON.parse(line.toString("utf8"));
      }
      while (buf.indexOf("\r\n\r\n") < 0 && buf.indexOf("\n\n") < 0) {
        if (!(await fill(buf.length + 1))) return null;
      }
      let sep = buf.indexOf("\r\n\r\n");
      let sepLen = 4;
      if (sep < 0) {
        sep = buf.indexOf("\n\n");
        sepLen = 2;
      }
      const header = take(sep + sepLen).toString("utf8");
      const match = /content-length:\s*(\d+)/i.exec(header);
      if (!match) throw new Error("missing Content-Length");
      const n = Number(match[1]);
      if (!(await fill(n))) return null;
      return JSON.parse(take(n).toString("utf8"));
    },
  };
}

function writeFrame(obj) {
  const body = Buffer.from(JSON.stringify(obj));
  process.stdout.write(`Content-Length: ${body.length}\r\n\r\n`);
  process.stdout.write(body);
}

async function main() {
  const reader = createReader(process.stdin);
  for (;;) {
    const msg = await reader.readMessage();
    if (msg == null) return;
    /** @type {unknown} */
    let out;
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(msg),
      });
      if (res.status === 204) continue;
      out = await res.json();
    } catch (err) {
      out = {
        jsonrpc: "2.0",
        id: msg.id ?? null,
        error: { code: -32000, message: err instanceof Error ? err.message : "bridge failed" },
      };
    }
    if (msg.id === undefined) continue;
    writeFrame(out);
  }
}

main().catch((err) => {
  process.stderr.write(`${err instanceof Error ? err.stack : String(err)}\n`);
  process.exit(1);
});
