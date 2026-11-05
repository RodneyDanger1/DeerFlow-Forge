"""Pipeline orchestrator: one `run_pipeline()` call = one asset through one product route.

Flow:  claim run -> stage input (sha256 verified) -> VectorCraft trace (raster fallback on exit 1)
       -> route steps (validate + fsync after each) -> publish to Fourthwall -> mark run.
"""
from __future__ import annotations

import asyncio
import datetime as dt
import hashlib
import logging
import shutil
import traceback
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

from . import db
from .config import ConfigError, Settings
from .fourthwall import FourthwallClient, FourthwallError, UnsupportedMedia
from .routes import (ROUTES, Route, Step, merged_cfg, raster_fallback_step, render, render_argv, trace_step)
from .runner import FlushTimeout, StepOutcome, flush_to_disk, run_step
from .validators import VALIDATORS, ValidationError

log = logging.getLogger("pod.orchestrator")

TRACE_FALLBACK_EXIT_CODES = {1}      # spec: "if a vector trace step returns exit code 1 -> raster fallback"


class PipelineError(RuntimeError):
    def __init__(self, message: str, *, digest: str = "", exit_code: int | None = None, quarantine: bool = False):
        super().__init__(message)
        self.digest, self.exit_code, self.quarantine = digest, exit_code, quarantine


@dataclass
class RunCtx:
    settings: Settings
    pool: db.Pool
    run: dict[str, Any]
    route: Route
    cfg: dict[str, Any]
    work: Path
    build: Path
    logs: Path
    vars: dict[str, Any] = field(default_factory=dict)
    _idx: int = 0

    def next_index(self) -> int:
        self._idx += 1
        return self._idx


# ------------------------------------------------------------------------------ entry point
async def run_pipeline(settings: Settings, pool: db.Pool, run_id: uuid.UUID | None, *, pid: int) -> dict[str, Any] | None:
    """Claim and execute one run (specific run_id, or the oldest queued one when None).
    Returns a summary dict, or None when nothing was claimable."""
    run = await db.claim_run(pool, run_id, pid)
    if run is None:
        return None
    rid: uuid.UUID = run["run_id"]
    summary: dict[str, Any] = {"run_id": str(rid), "asset_id": run["asset_id"], "product_type": run["product_type"],
                               "ok": False, "product_state": None, "artifact": None, "error": None}
    ctx: RunCtx | None = None
    try:
        route = ROUTES[run["product_type"]]
        ctx = RunCtx(settings=settings, pool=pool, run=run, route=route,
                     cfg=merged_cfg(run["product_type"], settings.products),
                     work=settings.sandbox / str(rid), build=settings.build / str(rid), logs=settings.job_logs / str(rid))
        await db.log_sync(pool, account_id=run["account_id"], direction="outbound", channel="orchestrator",
                          event_type="run.started", run_id=rid, payload={"product_type": run["product_type"]})
        final = await _execute(ctx)
        summary["artifact"] = str(final)
        summary["product_state"] = await _publish(ctx, final)
        await db.set_asset(pool, run["asset_id"], status="processed")
        await db.finish_run(pool, rid, ok=True, digest=None)
        summary["ok"] = True
        await asyncio.to_thread(shutil.rmtree, ctx.work, True)       # keep sandbox only for failed runs
    except PipelineError as exc:
        summary["error"] = _short(exc)
        await _fail(pool, run, exc.digest or str(exc), quarantine=exc.quarantine)
    except ConfigError as exc:
        summary["error"] = f"configuration: {exc}"
        await _fail(pool, run, summary["error"])
    except Exception as exc:                                          # bug or environment failure: keep it compact
        log.exception("run %s crashed", rid)
        summary["error"] = f"{type(exc).__name__}: {exc}"
        await _fail(pool, run, "".join(traceback.format_exception_only(type(exc), exc)) + _tb_tail())
    await db.log_sync(pool, account_id=run["account_id"], direction="outbound", channel="orchestrator",
                      event_type="run.finished", run_id=rid, success=summary["ok"], payload=summary)
    return summary


def _short(exc: BaseException) -> str:
    return str(exc)[:500]


def _tb_tail() -> str:
    return "\n".join(traceback.format_exc().splitlines()[-6:])


async def _fail(pool: db.Pool, run: dict[str, Any], digest: str, *, quarantine: bool = False) -> None:
    await db.finish_run(pool, run["run_id"], ok=False, digest=digest)
    await db.set_asset(pool, run["asset_id"], status="quarantined" if quarantine else "failed")


# ---------------------------------------------------------------------------------- stages
async def _execute(ctx: RunCtx) -> Path:
    s = ctx.settings
    for d in (ctx.work, ctx.build, ctx.logs):
        await asyncio.to_thread(d.mkdir, 0o750, True, True)
    await db.set_asset(ctx.pool, ctx.run["asset_id"], status="processing")

    src_path = Path(ctx.run["source_path"])
    staged = ctx.work / f"input{src_path.suffix.lower()}"
    await asyncio.to_thread(_stage_input, src_path, staged, ctx.run["sha256"])
    ctx.vars.update(src=str(staged), art=str(staged), work=str(ctx.work), build=str(ctx.build),
                    run_id=str(ctx.run["run_id"]), asset_id=ctx.run["asset_id"],
                    fallback_dpi=s.fallback_raster_dpi, cfg=ctx.cfg)

    await _trace_stage(ctx)
    for step in ctx.route.steps:
        await _run_step(ctx, step)
    final = Path(render(ctx.route.final, ctx.vars, where="route.final"))
    if not final.is_file():
        raise PipelineError(f"route finished but final artifact is missing: {final}")
    return final


def _stage_input(src: Path, dst: Path, expected_sha: str) -> None:
    if not src.is_file():
        raise PipelineError(f"source file is gone: {src}", quarantine=True)
    h = hashlib.sha256()
    with open(src, "rb") as fi, open(dst, "wb") as fo:
        while chunk := fi.read(1024 * 1024):
            h.update(chunk)
            fo.write(chunk)
        fo.flush()
    if h.hexdigest() != expected_sha:
        dst.unlink(missing_ok=True)
        raise PipelineError(f"{src.name} changed after ingest (sha256 mismatch); refusing to process", quarantine=True)


async def _trace_stage(ctx: RunCtx) -> None:
    pool, asset_id = ctx.pool, ctx.run["asset_id"]
    step = trace_step(ctx.route)
    idx = ctx.next_index()
    await db.set_asset(pool, asset_id, trace_state="tracing")
    try:
        outs = await _run_step(ctx, step, index=idx)
    except PipelineError as exc:
        if exc.exit_code not in TRACE_FALLBACK_EXIT_CODES:
            await db.set_asset(pool, asset_id, trace_state="trace_failed")
            raise
        log.warning("vector trace exited %s; switching to raster fallback (tier 1)", exc.exit_code)
        outs = await _run_step(ctx, raster_fallback_step(), index=idx, tier=1)
        ctx.vars["art"] = str(outs[0])
        await db.set_asset(pool, asset_id, trace_state="raster_fallback")
        return
    ctx.vars["art"] = str(outs[0])           # traced.svg
    await db.set_asset(pool, asset_id, trace_state="traced")


async def _run_step(ctx: RunCtx, step: Step, *, index: int | None = None, tier: int = 0) -> list[Path]:
    s = ctx.settings
    idx = index if index is not None else ctx.next_index()
    argv = render_argv(step, ctx.vars)
    timeout = step.timeout_s or s.step_timeout_s
    last_err: PipelineError | None = None
    for attempt in range(1, s.max_attempts + 1):
        log_path = ctx.logs / f"{idx:02d}-{step.name}-t{tier}-a{attempt}.log"
        job_id = await db.start_step(ctx.pool, ctx.run, module=step.module, step_name=step.name, step_index=idx,
                                     attempt=attempt, tier=tier, argv=argv)
        outcome: StepOutcome = await run_step(s, argv, work=ctx.work, build=ctx.build, log_path=log_path, timeout_s=timeout)
        problem: PipelineError | None = None
        outputs: list[Path] = []
        if not outcome.ok:
            why = "timed out after %ss" % timeout if outcome.timed_out else f"exit code {outcome.exit_code}"
            problem = PipelineError(f"{step.name} failed: {why}", digest=outcome.digest, exit_code=outcome.exit_code)
        else:
            try:
                outputs = await _collect_and_validate(ctx, step)
            except (PipelineError, ValidationError, FlushTimeout) as exc:
                code = 0 if isinstance(exc, PipelineError) else None
                problem = PipelineError(f"{step.name}: {exc}", digest=f"{exc}\n{outcome.digest}"[:4000], exit_code=code)
        await db.finish_step(ctx.pool, job_id, status="failed" if problem else "succeeded", exit_code=outcome.exit_code,
                             pid=outcome.pid, digest=(problem.digest if problem else outcome.digest if outcome.exit_code else None),
                             log_path=str(log_path), output_path=str(outputs[0]) if outputs else None)
        if problem is None:
            return outputs
        last_err = problem
        retryable = outcome.transient and attempt < s.max_attempts
        log.warning("step %s attempt %d failed (%s)%s", step.name, attempt, problem, "; retrying" if retryable else "")
        if not retryable:
            break
    assert last_err is not None
    raise last_err


async def _collect_and_validate(ctx: RunCtx, step: Step) -> list[Path]:
    outputs: list[Path] = []
    for tmpl in step.outputs:
        pattern = render(tmpl, ctx.vars, where=f"step {step.name} outputs")
        if "*" in pattern:
            matches = sorted(Path(pattern).parent.glob(Path(pattern).name))
            if not matches:
                raise PipelineError(f"expected output not produced: {pattern}")
            path = matches[0]
        else:
            path = Path(pattern)
        if not path.is_file() or path.stat().st_size == 0:
            raise PipelineError(f"expected output missing or empty: {path}")
        await flush_to_disk(path, poll_s=ctx.settings.flush_poll_s)
        outputs.append(path)
    for vname, tmpl in step.validators:
        target = Path(render(tmpl, ctx.vars, where=f"step {step.name} validator"))
        await asyncio.to_thread(VALIDATORS[vname], target, ctx.cfg)
    return outputs


# --------------------------------------------------------------------------------- publish
async def _publish(ctx: RunCtx, final: Path) -> str:
    """Upload to Fourthwall and create the design product. Returns the resulting publish_state."""
    run, pool, cfg = ctx.run, ctx.pool, ctx.cfg
    row = await db.upsert_product(pool, run)
    if row["fw_product_id"]:
        log.info("asset %s/%s already has Fourthwall product %s; not creating another",
                 run["asset_id"], run["product_type"], row["fw_product_id"])
        return row["publish_state"]
    upload_tmpl = ctx.route.upload
    if upload_tmpl is None:
        await db.upsert_product(pool, run, publish_state="draft", last_error="route has no Fourthwall upload step")
        return "draft"
    upload = Path(render(upload_tmpl, ctx.vars, where="route.upload"))

    creds = await db.get_fw_credentials(pool, ctx.settings, run["account_id"])
    if creds is None:
        await db.upsert_product(pool, run, publish_state="draft", last_error="no Fourthwall credentials configured")
        return "draft"
    template_id = cfg.get("fourthwall_template_id")
    if not template_id:
        msg = (f"products.json[{run['product_type']}].fourthwall_template_id is not set "
               "(list ids with: python -m pod_pipeline.worker --list-templates)")
        await db.upsert_product(pool, run, publish_state="failed", last_error=msg)
        raise PipelineError(msg)

    await db.upsert_product(pool, run, publish_state="processing", last_error=None, fw_template_id=template_id)

    async def hook(ev: dict[str, Any]) -> None:
        await db.log_sync(pool, account_id=run["account_id"], direction="outbound", channel="fourthwall_api",
                          run_id=run["run_id"], fw_product_row_id=row["id"], **ev)

    stem = Path(run["original_filename"]).stem.replace("_", " ").replace("-", " ").strip() or "Design"
    try:
        async with FourthwallClient(ctx.settings.fw_base_url, creds[0], creds[1], hook=hook) as fw:
            media_id = row["media_id"]
            if not media_id:
                img = await fw.upload_image(upload)
                media_id = img["id"]
                await db.upsert_product(pool, run, media_id=media_id, media_file_url=img.get("uri"))
            created = await fw.create_design_product(
                template_id=template_id, name=cfg.get("product_name", stem), description=cfg.get("description", stem),
                regions=[{"region": r, "imageId": media_id, "placementStrategy": "AUTO"} for r in cfg.get("regions", ["front"])],
                publish_on_create=False, profit_margin=cfg.get("profit_margin"))
            fw_id = created.get("productId") or created.get("id")
            if not fw_id:
                raise FourthwallError(f"create product response had no productId: {str(created)[:200]}")
            await db.upsert_product(pool, run, fw_product_id=fw_id)
            detail: dict[str, Any] = {}
            try:
                detail = await fw.get_product(fw_id)
            except FourthwallError as exc:       # product exists; detail is nice-to-have
                log.warning("created %s but could not read it back: %s", fw_id, exc)
            variants = detail.get("variants") or []
            state = "draft"
            if run.get("auto_publish"):
                await fw.set_state(fw_id, "PUBLIC")
                state = "active"
            await db.upsert_product(
                pool, run, fw_slug=detail.get("slug"), variants=variants,
                skus=[v["sku"] for v in variants if v.get("sku")], publish_state=state, last_error=None,
                published_at=dt.datetime.now(dt.timezone.utc) if state == "active" else None)
            return state
    except UnsupportedMedia as exc:
        msg = f"Fourthwall media library refused {upload.name} ({exc.code}); supported: {exc.supported or 'unknown'}"
        await db.upsert_product(pool, run, publish_state="needs_manual_upload", last_error=msg)
        return "needs_manual_upload"
    except FourthwallError as exc:
        await db.upsert_product(pool, run, publish_state="failed", last_error=str(exc)[:500])
        raise PipelineError(f"Fourthwall publish failed: {exc}", digest=str(exc)) from exc
    except httpx.TransportError as exc:
        await db.upsert_product(pool, run, publish_state="failed", last_error=f"network: {exc}"[:500])
        raise PipelineError(f"Fourthwall network error: {exc}") from exc

