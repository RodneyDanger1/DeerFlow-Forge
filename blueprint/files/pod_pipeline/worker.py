"""Worker entry point.

  python -m pod_pipeline.worker --run-id <uuid>        run exactly one queued run (spawned by the MCP tool)
  python -m pod_pipeline.worker --drain [--scan]       recover stale runs, optionally scan inbox, then run
                                                       queued runs until none are left (systemd timer target)
  python -m pod_pipeline.worker --scan                 only register new inbox files
  python -m pod_pipeline.worker --list-templates       print Fourthwall productTemplateId values
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import uuid

from . import db
from .config import ConfigError, Settings
from .fourthwall import FourthwallClient, FourthwallError
from .ingest import scan_inbox
from .orchestrator import run_pipeline

log = logging.getLogger("pod.worker")


async def drain(settings: Settings, pool: db.Pool) -> list[dict]:
    done: list[dict] = []
    while True:
        batch = await asyncio.gather(*[run_pipeline(settings, pool, None, pid=os.getpid())
                                       for _ in range(settings.max_concurrency)])
        got = [r for r in batch if r]
        done.extend(got)
        if not got:
            return done


async def list_templates(settings: Settings) -> int:
    if not (settings.fw_api_user and settings.fw_api_secret):
        print("set FW_API_USER and FW_API_SECRET first", file=sys.stderr)
        return 2
    async with FourthwallClient(settings.fw_base_url, settings.fw_api_user, settings.fw_api_secret) as fw:
        try:
            print(json.dumps(await fw.list_product_templates(), indent=2))
        except FourthwallError as exc:
            print(f"Fourthwall error: {exc}", file=sys.stderr)
            return 1
    return 0


async def amain(args: argparse.Namespace) -> int:
    settings = Settings.from_env()
    if args.list_templates:
        return await list_templates(settings)
    pool = await db.create_pool(settings)
    try:
        if args.scan:
            n = await scan_inbox(settings, pool)
            log.info("inbox scan registered %d new asset(s)", n)
        if args.run_id:
            res = await run_pipeline(settings, pool, uuid.UUID(args.run_id), pid=os.getpid())
            if res is None:
                log.info("run %s was not claimable (already running or finished)", args.run_id)
                return 0
            log.info("run finished: %s", json.dumps(res))
            return 0 if res["ok"] else 1
        if args.drain:
            recovered = await db.recover_stale_runs(pool)
            if recovered:
                log.warning("re-queued %d stale run(s) whose worker process vanished", recovered)
            results = await drain(settings, pool)
            failed = [r for r in results if not r["ok"]]
            log.info("drained %d run(s), %d failed", len(results), len(failed))
            return 1 if failed else 0
        return 0
    finally:
        await pool.close()


def main() -> None:
    logging.basicConfig(level=os.environ.get("POD_LOG_LEVEL", "INFO"), stream=sys.stderr,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(prog="pod_pipeline.worker")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--run-id")
    g.add_argument("--drain", action="store_true")
    g.add_argument("--list-templates", action="store_true")
    ap.add_argument("--scan", action="store_true", help="register new inbox files first")
    args = ap.parse_args()
    if not (args.run_id or args.drain or args.list_templates or args.scan):
        ap.error("nothing to do: pass --run-id, --drain, --scan or --list-templates")
    try:
        sys.exit(asyncio.run(amain(args)))
    except ConfigError as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
