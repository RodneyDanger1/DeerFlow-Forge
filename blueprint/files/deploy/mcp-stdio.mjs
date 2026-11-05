#!/usr/bin/env node
// stdio MCP bridge. The client (DeerFlow) may speak either Content-Length
// frames or one JSON object per line; the Python server mirrors the framing it
// receives. This bridge must mirror too: replying to a newline-delimited client
// with a Content-Length frame is unparseable on the client side.
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
      const framed = buf[0] !== 0x7b;
      if (!framed) {
        while (buf.indexOf(0x0a) < 0) {
          if (!(await fill(buf.length + 1))) return null;
        }
        const line = take(buf.indexOf(0x0a));
        take(1);
        return { msg: JSON.parse(line.toString("utf8")), framed };
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
      return { msg: JSON.parse(take(n).toString("utf8")), framed };
    },
  };
}

/**
 * Reply in the framing the client used: a newline-delimited client gets one
 * JSON line, a Content-Length client gets a Content-Length frame.
 */
function writeReply(obj, framed) {
  const body = Buffer.from(JSON.stringify(obj));
  if (!framed) {
    process.stdout.write(body);
    process.stdout.write("\n");
    return;
  }
  process.stdout.write(`Content-Length: ${body.length}\r\n\r\n`);
  process.stdout.write(body);
}

async function main() {
  const reader = createReader(process.stdin);
  for (;;) {
    const read = await reader.readMessage();
    if (read == null) return;
    const { msg, framed } = read;
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
    writeReply(out, framed);
  }
}

main().catch((err) => {
  process.stderr.write(`${err instanceof Error ? err.stack : String(err)}\n`);
  process.exit(1);
});
