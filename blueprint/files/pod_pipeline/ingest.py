"""Inbox scanner. Layout: <root>/data/inbox/<account_id>/<file>. New, settled files are hashed,
inspected and registered in ingested_assets (status 'pending'). Duplicates (same sha256) are ignored."""
from __future__ import annotations

import asyncio
import hashlib
import logging
import mimetypes
import time
from pathlib import Path
from typing import Any

from PIL import Image

from . import db
from .config import Settings

log = logging.getLogger("pod.ingest")
SKIP_SUFFIXES = {".part", ".tmp", ".crdownload", ".swp"}
MAX_INGEST_BYTES = 500 * 1024 * 1024


def inspect_file(path: Path) -> dict[str, Any]:
    """Blocking: hash + cheap metadata. Run in a thread."""
    h = hashlib.sha256()
    size = 0
    with open(path, "rb") as fh:
        while chunk := fh.read(1024 * 1024):
            h.update(chunk)
            size += len(chunk)
    meta: dict[str, Any] = {"sha256": h.hexdigest(), "byte_size": size,
                            "mime": mimetypes.guess_type(path.name)[0], "width": None, "height": None,
                            "dpi": None, "color_space": "unknown", "has_alpha": None}
    try:
        with Image.open(path) as im:
            meta["width"], meta["height"] = im.width, im.height
            dpi = im.info.get("dpi")
            if dpi:
                meta["dpi"] = int(round(float(dpi[0]))) or None
            meta["mime"] = Image.MIME.get(im.format or "", meta["mime"])
            meta["color_space"] = {"RGB": "srgb", "RGBA": "srgb", "LA": "gray", "L": "gray", "P": "indexed",
                                   "PA": "indexed", "CMYK": "cmyk"}.get(im.mode, "unknown")
            meta["has_alpha"] = im.mode in ("RGBA", "LA", "PA") or "transparency" in im.info
    except Exception:
        pass            # SVG/PDF/etc.: keep the basics; Craft apps do the real inspection
    return meta


async def scan_inbox(settings: Settings, pool: db.Pool) -> int:
    root = settings.inbox
    if not root.is_dir():
        return 0
    registered = 0
    now = time.time()
    for acct_dir in sorted(p for p in root.iterdir() if p.is_dir() and p.name.isdigit()):
        account_id = int(acct_dir.name)
        async with pool.acquire() as con:
            if not await con.fetchval("SELECT 1 FROM users_saas_accounts WHERE id=$1 AND status='active'", account_id):
                log.warning("inbox/%s has no active account; skipping", acct_dir.name)
                continue
            known = {r["source_path"] for r in await con.fetch(
                "SELECT source_path FROM ingested_assets WHERE account_id=$1", account_id)}
        for f in sorted(acct_dir.iterdir()):
            if (not f.is_file() or f.is_symlink() or f.name.startswith(".") or f.suffix.lower() in SKIP_SUFFIXES
                    or str(f) in known):
                continue
            st = f.stat()
            if now - st.st_mtime < settings.inbox_settle_s or st.st_size == 0 or st.st_size > MAX_INGEST_BYTES:
                continue            # still being written, empty, or oversized
            meta = await asyncio.to_thread(inspect_file, f)
            new_id = await db.register_asset(
                pool, account_id=account_id, source_path=str(f), filename=f.name, sha256=meta["sha256"],
                byte_size=meta["byte_size"], mime=meta["mime"], width=meta["width"], height=meta["height"],
                dpi=meta["dpi"], color_space=meta["color_space"], has_alpha=meta["has_alpha"])
            if new_id is not None:
                registered += 1
                log.info("registered asset %s (%s)", new_id, f.name)
    return registered
