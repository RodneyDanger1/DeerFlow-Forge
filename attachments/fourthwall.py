"""Fourthwall Open API client.

Endpoints and the exact upload handshake were checked against docs.fourthwall.com (Nov 2026):

    POST /open-api/v1.0/media/upload-url   {fileName, contentType, size}  -> {uploadUrl, fileUrl}
    PUT  <uploadUrl>   (Google Cloud Storage, NO Fourthwall credentials)
         headers: Content-Type == contentType, x-goog-content-length-range: 0,<size>   (both are signed)
    POST /open-api/v1.0/media/images       {fileUrl, width, height}       -> {id: imageId, ...}
    POST /open-api/v1.0/products           {type:"design", productTemplateId, name, regions:[{region,imageId}]}
    GET  /open-api/v1.0/products/{id}      PUT /open-api/v1.0/products/{id}/state {state: PUBLIC|HIDDEN}
    GET  /open-api/v1.0/product-templates

Auth: HTTP Basic with an API key pair (docs: "API keys have full access to these endpoints").
Rate limits: media/upload-url 20 req/min per shop; most others 100 req / 10 s per shop.
"""
from __future__ import annotations

import asyncio
import time
from collections import deque
from pathlib import Path
from typing import Any, Awaitable, Callable

import httpx
from PIL import Image

Hook = Callable[[dict[str, Any]], Awaitable[None]]


class FourthwallError(RuntimeError):
    def __init__(self, message: str, *, status: int | None = None, code: str | None = None, body: Any = None):
        super().__init__(message)
        self.status, self.code, self.body = status, code, body


class UnsupportedMedia(FourthwallError):
    """406 UNSUPPORTED_MEDIA_TYPE_ERROR / UNSUPPORTED_ASSET_TYPE_ERROR from the media library."""

    def __init__(self, message: str, *, supported: list[str] | None = None, **kw: Any):
        super().__init__(message, **kw)
        self.supported = supported or []


class SlidingWindowLimiter:
    """Client-side guard so we never trip the 20/min media limit (and thus never burn a retry)."""

    def __init__(self, max_calls: int, period_s: float, *, clock: Callable[[], float] = time.monotonic,
                 sleep: Callable[[float], Awaitable[None]] = asyncio.sleep) -> None:
        self._max, self._period, self._clock, self._sleep = max_calls, period_s, clock, sleep
        self._stamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            while True:
                now = self._clock()
                while self._stamps and now - self._stamps[0] >= self._period:
                    self._stamps.popleft()
                if len(self._stamps) < self._max:
                    self._stamps.append(now)
                    return
                await self._sleep(self._period - (now - self._stamps[0]) + 0.01)


class FourthwallClient:
    def __init__(self, base_url: str, user: str, secret: str, *, hook: Hook | None = None,
                 transport: httpx.AsyncBaseTransport | None = None,
                 gcs_transport: httpx.AsyncBaseTransport | None = None,
                 limiter: SlidingWindowLimiter | None = None, max_429_retries: int = 3) -> None:
        self._api = httpx.AsyncClient(base_url=base_url, auth=(user, secret), timeout=30.0, transport=transport)
        self._gcs = httpx.AsyncClient(timeout=300.0, transport=gcs_transport)   # no auth: credentials must not go to GCS
        self._hook = hook
        self._media_limiter = limiter or SlidingWindowLimiter(20, 60.0)
        self._max_429 = max_429_retries

    async def aclose(self) -> None:
        await self._api.aclose()
        await self._gcs.aclose()

    async def __aenter__(self) -> "FourthwallClient":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.aclose()

    # ------------------------------------------------------------------ plumbing
    async def _call(self, method: str, path: str, *, event: str, json: Any = None, retry_5xx: bool = False) -> Any:
        attempt = 0
        while True:
            t0 = time.monotonic()
            resp = await self._api.request(method, path, json=json)
            if self._hook:
                await self._hook({
                    "event_type": event, "http_method": method, "url": str(resp.request.url),
                    "status_code": resp.status_code, "duration_ms": int((time.monotonic() - t0) * 1000),
                    "payload": {"request": json, "response": _clip(resp)},
                })
            if resp.status_code == 429 and attempt < self._max_429:
                attempt += 1
                wait = _retry_after(resp, default=2.0 * attempt)
                await asyncio.sleep(wait)
                continue
            if resp.status_code >= 500 and retry_5xx and attempt < 2:
                attempt += 1
                await asyncio.sleep(1.5 * attempt)
                continue
            if resp.is_success:
                return resp.json() if resp.content else None
            raise _error_from(resp)

    # ------------------------------------------------------------------ media
    async def request_upload_url(self, file_name: str, content_type: str, size: int) -> dict[str, str]:
        await self._media_limiter.acquire()
        return await self._call("POST", "/open-api/v1.0/media/upload-url", event="media.upload_url",
                                json={"fileName": file_name, "contentType": content_type, "size": size})

    async def put_to_storage(self, upload_url: str, data: bytes, content_type: str, size: int) -> None:
        if len(data) != size:
            raise FourthwallError(f"internal: size {size} != len(data) {len(data)}")
        t0 = time.monotonic()
        resp = await self._gcs.put(upload_url, content=data, headers={
            "Content-Type": content_type, "x-goog-content-length-range": f"0,{size}"})
        if self._hook:
            await self._hook({"event_type": "media.gcs_put", "http_method": "PUT",
                              "url": upload_url.split("?")[0], "status_code": resp.status_code,
                              "duration_ms": int((time.monotonic() - t0) * 1000),
                              "payload": {"bytes": size, "response": resp.text[:300]}})
        if not resp.is_success:
            raise FourthwallError(f"GCS upload failed with HTTP {resp.status_code}: {resp.text[:200]}",
                                  status=resp.status_code, code="GCS_UPLOAD_FAILED")

    async def register_image(self, file_url: str, width: int, height: int) -> dict[str, Any]:
        return await self._call("POST", "/open-api/v1.0/media/images", event="media.register",
                                json={"fileUrl": file_url, "width": width, "height": height})

    async def upload_image(self, path: Path) -> dict[str, Any]:
        """3-step upload. Returns the registered image dict (its `id` is the imageId)."""
        content_type = _content_type(path)
        data = await asyncio.to_thread(path.read_bytes)
        width, height = await asyncio.to_thread(_pixel_size, path)
        slot = await self.request_upload_url(path.name, content_type, len(data))
        await self.put_to_storage(slot["uploadUrl"], data, content_type, len(data))
        return await self.register_image(slot["fileUrl"], width, height)

    # ------------------------------------------------------------------ products
    async def list_product_templates(self) -> Any:
        return await self._call("GET", "/open-api/v1.0/product-templates", event="templates.list", retry_5xx=True)

    async def create_design_product(self, *, template_id: str, name: str, description: str,
                                    regions: list[dict[str, str]], publish_on_create: bool = False,
                                    profit_margin: float | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"type": "design", "productTemplateId": template_id, "name": name,
                                "description": description, "regions": regions, "publishOnCreate": publish_on_create}
        if profit_margin is not None:
            body["profitMargin"] = profit_margin
        # POST is not retried on 5xx: the product may exist already and a retry would duplicate it.
        return await self._call("POST", "/open-api/v1.0/products", event="product.create", json=body)

    async def get_product(self, product_id: str) -> dict[str, Any]:
        return await self._call("GET", f"/open-api/v1.0/products/{product_id}", event="product.get", retry_5xx=True)

    async def set_state(self, product_id: str, state: str) -> dict[str, Any]:
        if state not in ("PUBLIC", "HIDDEN"):
            raise ValueError("state must be PUBLIC or HIDDEN")
        return await self._call("PUT", f"/open-api/v1.0/products/{product_id}/state", event="product.state",
                                json={"state": state}, retry_5xx=True)


# --------------------------------------------------------------------------- helpers
def _content_type(path: Path) -> str:
    return {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
            ".pdf": "application/pdf", ".bmp": "image/bmp", ".mp4": "video/mp4",
            ".svg": "image/svg+xml"}.get(path.suffix.lower(), "application/octet-stream")


def _pixel_size(path: Path) -> tuple[int, int]:
    try:
        with Image.open(path) as im:
            return im.width, im.height
    except Exception:
        return 1, 1          # non-raster file (PDF/MP4): let Fourthwall decide whether it accepts the type


def _clip(resp: httpx.Response, limit: int = 1500) -> Any:
    try:
        text = resp.text
    except Exception:
        return None
    return text[:limit]


def _retry_after(resp: httpx.Response, default: float) -> float:
    try:
        return min(60.0, max(0.0, float(resp.headers.get("Retry-After", default))))
    except ValueError:
        return default


def _error_from(resp: httpx.Response) -> FourthwallError:
    try:
        body = resp.json()
    except ValueError:
        body = {"raw": resp.text[:300]}
    code = body.get("code") if isinstance(body, dict) else None
    msg = f"Fourthwall HTTP {resp.status_code} {code or ''} on {resp.request.method} {resp.request.url.path}".strip()
    if code in ("UNSUPPORTED_MEDIA_TYPE_ERROR", "UNSUPPORTED_ASSET_TYPE_ERROR"):
        supported = body.get("supportedMediaTypes") or []
        return UnsupportedMedia(msg, supported=list(supported), status=resp.status_code, code=code, body=body)
    return FourthwallError(msg, status=resp.status_code, code=code, body=body)
