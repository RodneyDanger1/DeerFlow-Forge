---
name: fourthwall-catalog-audit
description: Independently audit what is actually live in the Ridgeboundia Fourthwall store — Open API state/access/price/image readback, local DB whitelist and duplicate check, storefront 200/404 checks, archive-not-delete rules and an evidence table. Use when the user says audit the store, what is actually live, check the catalogue, find duplicates or hidden products, verify the whitelist, is this product live, or why does the shop disagree with Fourthwall.
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [fourthwall, audit, catalogue, storefront, database, verification, ridgeboundia]
    related_skills: [fourthwall-product-publish, merch-mockup-proof, apparel-print-master, brand-system]
---

# Fourthwall catalogue audit

A read-only, three-layer audit: what the provider says, what the local database says, and what a browser actually gets. The three layers disagree in useful ways — the provider can return a product the public page 404s, and the local DB can keep rows that are deliberately archived. This skill records the disagreement as evidence; it does not repair unless a separate approval says so.

## When to use
- “What is actually live?” before a launch, after a publish, or after an incident.
- The shop, the manifest and the provider disagree.
- Duplicate, hidden or orphaned products are suspected.
- A 404/200 check is needed for `/shop` and every product slug.
- A whitelist repair must be planned and then proved.

## When not to use
- Publishing, replacing or hiding a product — `fourthwall-product-publish`.
- Inspecting mockups or ordering a sample — `merch-mockup-proof`.
- Repairing without approval — audit read-only, report the proposed SQL.
- No credentials — run the DB/HTTP layers and label the provider layer blocked; never invent counts.

## Inputs
- Read-only VPS access (`ssh -i ~/.ssh/id_ed25519_hostinger root@179.197.88.181`).
- Platform credentials `FW_API_USER`/`FW_API_SECRET` in `/opt/pod-pipeline/config/pipeline.env`.
- Storefront token (`ptkn_…`) only for the Storefront API layer; absent means that layer is blocked.
- Storefront DB: container `ridgeboundia-postgres`, user/db `ridgeboundia`, table `"Product"`.
- Audit timestamp in UTC and the owner's expected live set, written down before reading.

## Live truth (read back 2026-11-05)
| Product | Slug | Fourthwall id | Access / state | Variants | Images | Retail |
|---|---|---|---|---|---|---|
| Lost And Learning Tee | `lost-and-learning-tee-4` | `5d40b2c7-5687-46bb-a0a0-75c19d4b9a9e` | PUBLIC / AVAILABLE | 8 | 10 | $20.50–$28.50 |
| Lost And Learning Hoodie | `lost-and-learning-hoodie-3` | `84305616-1446-490f-b022-adff79b9bdb4` | PUBLIC / AVAILABLE | 8 | 4 | $33.20–$41.20 |
| Lost And Learning Beanie | `lost-and-learning-beanie-3` | `6e655114-1d1d-40fb-977c-d413f8ee54bf` | PUBLIC / AVAILABLE | 1 | 7 | $24.29 |
| Abyssal Signal Neon Whale Tee | `abyssal-signal-neon-whale-tee-3` | `7bff0d73-51b6-494d-a38a-62ca57615f0b` | PUBLIC / AVAILABLE | 8 | 10 | $24.00–$32.00 |
| GRU Hoodie | `gru-hoodie` | `9ebab6d3-0a07-4039-bea5-f9d9608b8b24` | PUBLIC / AVAILABLE | 6 | 4 | $34.99–$38.99 |

Provider total 14 = 5 `PUBLIC` + 9 `HIDDEN`. Tee-3 (`be2bfd1c-5e30-44a6-abd7-c6b57c18a82c`) is HIDDEN and 404s. Local: 13 rows = 5 `active` + 8 `archived`, exactly 1 `featured`. Hidden whale `26b47bd0-ed16-4fc4-80dc-a3baf3157c3b` has **no** local row — a provider-only orphan.

## Exact commands
Read the provider list. `tsx` is the app's runtime; this keeps credentials in env, not argv.

```bash
cd /srv/ridgeboundia
set -a; . /opt/pod-pipeline/config/pipeline.env; set +a
npx tsx - <<'TS'
const auth = "Basic " + Buffer.from(process.env.FW_API_USER + ":" + process.env.FW_API_SECRET).toString("base64");
const res = await fetch(process.env.FW_BASE_URL + "/open-api/v1.0/products?size=100", { headers: { authorization: auth } });
const page = await res.json();
console.log(`HTTP ${res.status} total=${page.total} rows=${page.results.length}`);
for (const p of page.results) console.log([p.slug, p.id, p.access.type, p.state.type, p.variants.length, p.images.length, Math.min(...p.variants.map(v => v.unitPrice.value)), Math.max(...p.variants.map(v => v.unitPrice.value))].join("\t"));
TS
```

Read one product when a row is disputed (replace `ID`):

```bash
ID=5d40b2c7-5687-46bb-a0a0-75c19d4b9a9e npx tsx - <<'TS'
const auth = "Basic " + Buffer.from(process.env.FW_API_USER + ":" + process.env.FW_API_SECRET).toString("base64");
const res = await fetch(process.env.FW_BASE_URL + "/open-api/v1.0/products/" + process.env.ID, { headers: { authorization: auth } });
const p = await res.json();
console.log(JSON.stringify({ id: p.id, slug: p.slug, access: p.access, state: p.state, variants: p.variants.length, images: p.images.length, prices: p.variants.map(v => v.unitPrice.value) }, null, 1));
TS
```

Storefront readback (needs the `ptkn_` token; without it this layer is blocked):

```bash
read -rsp 'Storefront token (ptkn_): ' FOURTHWALL_STOREFRONT_TOKEN; echo; export FOURTHWALL_STOREFRONT_TOKEN
curl -fsS "https://storefront-api.fourthwall.com/v1/products/lost-and-learning-tee-4?storefront_token=$FOURTHWALL_STOREFRONT_TOKEN" | head -c 600
```

Local DB audit (read-only; `psql` inside the container, no host psql):

```bash
docker exec -i ridgeboundia-postgres psql -U ridgeboundia -d ridgeboundia -P pager=off -f - <<'SQL'
SELECT count(*) AS total, count(*) FILTER (WHERE status='active') AS active, count(*) FILTER (WHERE status='archived') AS archived, count(*) FILTER (WHERE featured) AS featured FROM "Product";
SELECT slug, "fourthwallProductId", "priceCents", featured FROM "Product" WHERE status='active' ORDER BY slug;
SELECT regexp_replace(slug, '-[0-9]+$', '') AS design, count(*) FILTER (WHERE status='active') AS active_rows FROM "Product" GROUP BY 1 HAVING count(*) FILTER (WHERE status='active') > 1;
SQL
```

HTTP matrix (no credentials):

```bash
for s in shop lost-and-learning-tee-4 lost-and-learning-hoodie-3 lost-and-learning-beanie-3 abyssal-signal-neon-whale-tee-3 gru-hoodie lost-and-learning-tee-3; do
  url=https://ridgeboundia.com/shop; [ "$s" = shop ] || url=https://ridgeboundia.com/product/$s
  printf '%s %s\n' "$s" "$(curl -sS -o /dev/null -w '%{http_code}' "$url")"
done
```

Whitelist repair — **approval required**, never during the read-only audit. This is the exact one-transaction repair (no row deletes):

```bash
docker exec ridgeboundia-postgres psql -U ridgeboundia -d ridgeboundia -v ON_ERROR_STOP=1 -c "BEGIN; UPDATE \"Product\" SET status='archived', featured=false WHERE status='active' AND \"fourthwallProductId\" NOT IN ('5d40b2c7-5687-46bb-a0a0-75c19d4b9a9e','84305616-1446-490f-b022-adff79b9bdb4','6e655114-1d1d-40fb-977c-d413f8ee54bf','7bff0d73-51b6-494d-a38a-62ca57615f0b','9ebab6d3-0a07-4039-bea5-f9d9608b8b24'); UPDATE \"Product\" SET status='active' WHERE \"fourthwallProductId\" IN ('5d40b2c7-5687-46bb-a0a0-75c19d4b9a9e','84305616-1446-490f-b022-adff79b9bdb4','6e655114-1d1d-40fb-977c-d413f8ee54bf','7bff0d73-51b6-494d-a38a-62ca57615f0b','9ebab6d3-0a07-4039-bea5-f9d9608b8b24'); UPDATE \"Product\" SET featured = (\"fourthwallProductId\"='5d40b2c7-5687-46bb-a0a0-75c19d4b9a9e'); COMMIT;"
```

Evidence table for the vault log (`40-logs/YYYY-MM-DD-HHMM-fourthwall-audit.md`):

| Layer | Check | Command | Expected | Observed | Verdict |
|---|---|---|---|---|---|
| Provider | public/hidden counts | list readback | 5 / 9 | `<observed>` | PASS/FAIL |
| DB | active/archived/featured | psql count | 5 / 8 / 1 | `<observed>` | PASS/FAIL |
| HTTP | shop + 5 live + 1 old | curl matrix | 200 ×6, 404 ×1 | `<observed>` | PASS/FAIL |

## Workflow
1. Write the expected live set and the UTC timestamp before running anything.
2. Read the provider list; save the raw output next to the log.
3. Read the local DB counts and active rows; do not edit them.
4. Compare ids: every `active` local id must be `PUBLIC`; every `PUBLIC` id must be `active`.
5. Run the HTTP matrix; treat a 404 as evidence only for the slug requested.
6. Check duplicate active designs and provider-only orphans; classify, do not “clean up”.
7. Record the evidence table, then propose a repair separately if needed.

## Acceptance gates
- Provider: 14 total, 5 `PUBLIC`/`AVAILABLE`, 9 `HIDDEN`, all five live ids present.
- DB: 5 `active`, 8 `archived`, exactly 1 `featured` (tee-4), 0 duplicate active designs.
- Cross-check: every active `<->` PUBLIC id matches on both sides; no active row points to HIDDEN.
- HTTP: `/shop` 200; all five live product pages 200; tee-3 404.
- Evidence: raw provider output, psql output and curl codes stored with the UTC timestamp.
- No write occurred during the audit (no UPDATE, DELETE, publish or hide).

## Refusals
- “Just delete the duplicate” — local rows are archived, never deleted; provider DELETE is terminal.
- Editing the whitelist during an audit — stop; require a separate approved repair.
- Calling a hidden product “deleted” — it still exists with `access:HIDDEN`.
- Reporting counts without a timestamp or raw output — not evidence.
- Treating a 200 from the Platform API as proof the public page works.
- Guessing the storefront token or borrowing another shop's token.

## Worked example
The 2026-11-05 audit found provider 14 (5 PUBLIC, 9 HIDDEN) and local 13 (5 active, 8 archived, 1 featured). All five active ids matched PUBLIC products; tee-4 was the only featured row; 0 duplicate active designs; `/shop` and the five live pages returned 200; tee-3 returned 404. The audit also found provider-only hidden `abyssal-signal-neon-whale-tee-2` (`26b47bd0-ed16-4fc4-80dc-a3baf3157c3b`) with no local row, and confirmed the manifest table was stale: it listed tee-3 as live while its own correction block and the provider both said tee-4.

## Pitfalls
- **API 200 ≠ public 200**: hidden products come back from the Platform API with `access:HIDDEN`; the public slug 404s.
- **Storefront sync sees only the public catalogue**; archived generations survive locally and must be counted, not “fixed”.
- **`status` is a string** (`active`/`archived`), not a Prisma enum; raw SQL is safe but must quote the table/column names.
- **Slug suffixes are generations**, not duplicates: `-2`, `-3`, `-4`; strip `-[0-9]+$` before grouping.
- **Platform auth and Storefront auth are different**: Basic user/password vs `ptkn_` query token.
- **Storefront token is absent** from `.env.production`/container env today; this blocks only the Storefront layer.
- **GRU is White** with S–3XL, $34.99/$36.99/$38.99; do not infer it from the tee.
- **The manifest is not the source of truth**; its live-correction block wins over its table.

## Sources & verification
- VERIFIED — 2026-11-05 readback: 14 products, 5 PUBLIC, 9 HIDDEN, per-row variants/images/prices above; DB 13 rows, 5 active, 8 archived, 1 featured, 0 duplicate active; `/shop` 200, five pages 200, tee-3 404; provider-only orphan `26b47bd0…`; `npx tsx` readback returned HTTP 200.
- SCHEMA — `lib/fourthwall/config.ts:174` (storefront token refusal); `lib/fourthwall/storefront.ts` (collection read); `lib/fourthwall/sync.ts:219` (`runFourthwallSync`); `prisma/schema.prisma:125` (`status`), `:160` (`fourthwallProductId`).
- DOCS — fetched 2026-11-05: [List products](https://docs.fourthwall.com/api-reference/platform/products/list-products.md), [Get product](https://docs.fourthwall.com/api-reference/platform/products/get-product.md), [Archive a product](https://docs.fourthwall.com/api-reference/platform/products-(offers)/archive-product.md), [Update product state](https://docs.fourthwall.com/api-reference/platform/products-(offers)/update-product-state.md), [Get collection products](https://docs.fourthwall.com/api-reference/storefront/collections/get-collection-products.md), [Rate limiting](https://docs.fourthwall.com/guides/rate-limiting.md).
- UNVERIFIED — the owner-reported “GRU was accidentally archived” incident is not in the vault logs; the durable lesson is that `DELETE` is a terminal archive and restoration is admin-only. The Storefront API layer is docs-only until a `ptkn_` token is restored.
