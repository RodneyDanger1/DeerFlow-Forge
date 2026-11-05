#!/usr/bin/env python3
"""Fetch the Fourthwall template catalogue and per-template detail.

Writes the machine-readable snapshots used by `tools.prep_print_art` and the
vault notes:

  config/fourthwall-product-templates.json   list rows (25 pages)
  config/fourthwall-template-details.json    detail rows incl. area geometry
  config/fourthwall-template-details.csv

Credentials come from the environment (FW_API_USER / FW_API_SECRET) — the same
Basic-auth pair the pipeline uses. Nothing here is ever logged or printed.
"""
from __future__ import annotations

import base64
import csv
import json
import os
import re
import sys
import time
from pathlib import Path

import httpx

BASE = "https://api.fourthwall.com/open-api/v1.0"
LIST_OUT = Path("config/fourthwall-product-templates.json")
DETAIL_OUT = Path("config/fourthwall-template-details.json")
CSV_OUT = Path("config/fourthwall-template-details.csv")


def strip_html(value: str) -> str:
    text = re.sub(r"<br\s*/?>", " ", value or "")
    text = re.sub(r"</(p|li|ul|ol|h[1-6])>", " ", text)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"').strip()


def auth_headers() -> dict[str, str]:
    user = os.environ.get("FW_API_USER")
    secret = os.environ.get("FW_API_SECRET")
    if not user or not secret:
        raise SystemExit("FW_API_USER and FW_API_SECRET must be set")
    token = base64.b64encode(f"{user}:{secret}".encode()).decode()
    return {"Authorization": f"Basic {token}", "accept": "application/json"}


def fetch_list(client: httpx.Client, headers: dict[str, str]) -> list[dict]:
    rows: list[dict] = []
    total = None
    page = 1
    while True:
        path = "/product-templates" if page == 1 else f"/product-templates/page/{page}"
        response = client.get(f"{BASE}{path}", headers=headers)
        response.raise_for_status()
        data = response.json()
        page_rows = data.get("results", [])
        total = data.get("total", total)
        rows.extend(page_rows)
        print(f"list page {page}: rows={len(page_rows)} total={total}")
        if not page_rows or (total is not None and len(rows) >= int(total)) or page > 100:
            break
        page += 1
    return rows


def fetch_details(client: httpx.Client, headers: dict[str, str], rows: list[dict]) -> dict[str, dict]:
    details: dict[str, dict] = {}
    failures: list[str] = []
    for index, row in enumerate(rows, start=1):
        pid = row["productId"]
        for _ in range(4):
            response = client.get(f"{BASE}/product-templates/{pid}", headers=headers)
            if response.status_code == 200:
                details[pid] = response.json()
                break
            if response.status_code == 429:
                time.sleep(float(response.headers.get("retry-after", "2")) + 0.5)
                continue
            failures.append(f"{pid}:{response.status_code}")
            break
        time.sleep(0.12)  # stay under the documented 100 req / 10 s
        if index % 100 == 0:
            print(f"detail {index}/{len(rows)} failures={len(failures)}")
    if failures:
        print(f"detail failures: {failures[:10]}", file=sys.stderr)
    return details


def merge(rows: list[dict], details: dict[str, dict]) -> list[dict]:
    merged = []
    for row in rows:
        detail = details.get(row["productId"], {})
        colors = detail.get("colorVariants") or []
        areas = detail.get("customizableAreas") or []
        area_geometry = {
            area.get("regionId") or area.get("name"): {
                "name": area.get("name"),
                "available": area.get("available"),
                "productionMethod": area.get("productionMethod"),
                "supportsBackendRendering": area.get("supportsBackendRendering"),
                **{key: (area.get("dimensions") or {}).get(key) for key in ("inchesWidth", "inchesHeight", "pixelsWidth", "pixelsHeight", "dpi")},
            }
            for area in areas
            if isinstance(area, dict)
        }
        base = (row.get("basePrice") or {}).get("amount")
        merged.append({
            "productId": row["productId"],
            "name": row.get("name"),
            "slug": detail.get("slug"),
            "category": row.get("category"),
            "brand": row.get("brand"),
            "productionMethod": row.get("productionMethod"),
            "supportsBackendRendering": row.get("supportsBackendRendering"),
            "basePrice": row.get("basePrice"),
            "priceFrom": detail.get("priceFrom"),
            "priceTo": detail.get("priceTo"),
            "minimumOrdersNumber": detail.get("minimumOrdersNumber"),
            "description": strip_html(detail.get("description", "")),
            "colorCount": len(colors),
            "colors": [c.get("color", c).get("name") if isinstance(c, dict) else c for c in colors],
            "areas": [area.get("name") for area in areas if isinstance(area, dict)],
            "areaGeometry": area_geometry,
            "pricing": [{"margin": margin, "retail": round((base or 0) + margin, 2)} for margin in (12.0, 13.5, 15.0)],
            "detailFetched": bool(detail),
        })
    return merged


def main() -> int:
    headers = auth_headers()
    with httpx.Client(timeout=40) as client:
        rows = fetch_list(client, headers)
        details = fetch_details(client, headers, rows)
    merged = merge(rows, details)
    LIST_OUT.parent.mkdir(parents=True, exist_ok=True)
    LIST_OUT.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    DETAIL_OUT.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["productId", "name", "slug", "category", "brand", "productionMethod", "supportsBackendRendering",
                         "basePriceUSD", "priceFrom", "priceTo", "minimumOrders", "colors", "areas", "areaGeometry",
                         "retail_at_12_margin", "retail_at_13_5_margin", "retail_at_15_margin", "description", "detailFetched"])
        for item in merged:
            retail = {entry["margin"]: entry["retail"] for entry in item["pricing"]}
            writer.writerow([item["productId"], item["name"], item["slug"], item["category"], item["brand"],
                             item["productionMethod"], item["supportsBackendRendering"], (item["basePrice"] or {}).get("amount"),
                             item["priceFrom"], item["priceTo"], item["minimumOrdersNumber"], "; ".join(map(str, item["colors"])),
                             "; ".join(item["areas"]), json.dumps(item["areaGeometry"]), retail.get(12.0), retail.get(13.5),
                             retail.get(15.0), item["description"], item["detailFetched"]])
    print(f"templates={len(merged)} details={sum(1 for item in merged if item['detailFetched'])} -> {DETAIL_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
