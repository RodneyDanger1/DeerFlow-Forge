#!/usr/bin/env python3
"""W2-B concurrency proof: two workers claim different queued jobs using SKIP LOCKED."""
from __future__ import annotations

import asyncio
import os
import sys
import time

import asyncpg

DSN = os.environ.get("FORGE_TEST_DSN")
if not DSN:
    print("FORGE_TEST_DSN required", file=sys.stderr)
    raise SystemExit(2)


async def main() -> None:
    a = await asyncpg.connect(DSN)
    b = await asyncpg.connect(DSN)
    try:
        await a.execute("SET search_path = forge, public")
        await b.execute("SET search_path = forge, public")
        for _ in range(2):
            await a.execute("INSERT INTO forge.forge_job (kind) VALUES ('skiplock')")
        ta = a.transaction()
        await ta.start()
        first = await a.fetchrow("SELECT * FROM forge.forge_claim_job('worker-a', 30)")
        start = time.monotonic()
        second = await b.fetchrow("SELECT * FROM forge.forge_claim_job('worker-b', 30)")
        elapsed = time.monotonic() - start
        assert first is not None and second is not None
        assert first["id"] != second["id"], (first["id"], second["id"])
        assert elapsed < 2.0, elapsed
        print(f"PASS T-SKIPLOCK distinct jobs={first['id']},{second['id']} elapsed_ms={elapsed*1000:.0f}")
        await ta.rollback()
    finally:
        await a.close()
        await b.close()


if __name__ == "__main__":
    asyncio.run(main())
