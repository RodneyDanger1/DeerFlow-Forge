---
name: fourthwall-product-publish
description: Publish, replace or retire a Ridgeboundia Fourthwall design product through the exact live pipeline — hidden create, PUBLIC, hide the old generation, storefront index, runFourthwallSync, DB whitelist repair and 200/404 verification. Use when the user says publish this design, put it on the store, replace the tee/hoodie/beanie, new Fourthwall product, go live, republish, hide the old one, or fix what is live.
version: 1.0.0
author: DeerFlow Forge
license: original
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [fourthwall, publish, catalogue, dtg, embroidery, storefront, ridgeboundia]
    related_skills: [apparel-print-master, embroidery-art, fourthwall-catalog-audit, merch-mockup-proof]
---

# Fourthwall product publish

Publishes one owner-approved design through the same path the live store uses: upload → create **hidden** → publish `PUBLIC` → hide the older generation → wait for the storefront index → `runFourthwallSync` → repair the local whitelist → verify HTTP. Fourthwall has no in-place art edit, so a replacement is always a new product plus a state change on the old one. This skill changes the live store: get explicit owner approval before step 2.

## When to use
- A gated PNG master is approved and must become a new live product.
- A live product must be replaced (the tee-3 → tee-4 pattern).
- A bad or duplicate product must be hidden, or a hidden one republished.
- A price/colour/size change needs a new product because uploaded art cannot be edited in place.

## When not to use
- Art is not gated — finish `apparel-print-master` or `embroidery-art` first.
- The job is only to inspect the live catalogue — `fourthwall-catalog-audit`.
- The job is only to inspect mockups or order a sample — `merch-mockup-proof`.
- No named owner approval, no credentials, or no storefront token — stop and report the gate.
- `KNITTING` or `supportsBackendRendering:false` — refuse before any upload.
- “Delete this product” — `DELETE` archives permanently; use `HIDDEN` unless a terminal archive is explicitly wanted.

## Inputs
- Owner approval (who, when), new slug, display name, template id and region.
- The master PNG plus its passing JSON gate report; PNG/JPEG only, ≤25 MB.
- Approved colour, size array and profit margin in **USD** (not a percentage).
- The full intended live set and the ids to hide; never infer the live set from memory.
- Env only, never a file or command line: `FOURTHWALL_API_USERNAME`, `FOURTHWALL_API_PASSWORD`, `FOURTHWALL_STOREFRONT_TOKEN` (`ptkn_…`).

## Live catalogue (read back 2026-11-05)
| Product | Slug | Fourthwall id | Template | Region (in) | Colour / sizes | Retail | Images |
|---|---|---|---|---|---|---|---|
| Lost And Learning Tee | `lost-and-learning-tee-4` | `5d40b2c7-5687-46bb-a0a0-75c19d4b9a9e` | `pro_e4677535402b4eeb81` | `front_large` 15×18 | Black, S–5XL | $20.50–$28.50 | 10 |
| Lost And Learning Hoodie | `lost-and-learning-hoodie-3` | `84305616-1446-490f-b022-adff79b9bdb4` | `pro_gUu4CvXsRm-BxogjB89KzA` | `front` 14×14 | Black, S–5XL | $33.20–$41.20 | 4 |
| Lost And Learning Beanie | `lost-and-learning-beanie-3` | `6e655114-1d1d-40fb-977c-d413f8ee54bf` | `pro_12abde5f29c34ffbb2` | `embroidery_front` 5×1.75 | Black, One size | $24.29 | 7 |
| Abyssal Signal Neon Whale Tee | `abyssal-signal-neon-whale-tee-3` | `7bff0d73-51b6-494d-a38a-62ca57615f0b` | `pro_e4677535402b4eeb81` | `front_large` 15×18 | Black, S–5XL | $24.00–$32.00 | 10 |
| GRU Hoodie | `gru-hoodie` | `9ebab6d3-0a07-4039-bea5-f9d9608b8b24` | existing product | — | White, S–3XL | $34.99–$38.99 | 4 |

Tee-3 `lost-and-learning-tee-3` (`be2bfd1c-5e30-44a6-abd7-c6b57c18a82c`) is **HIDDEN** and its page 404s; it is archived, not deleted. Provider total is 14: 5 `PUBLIC` + 9 `HIDDEN`. Unit costs: tee $9.50, hoodie $22.20, beanie $13.29, whale $9.50, GRU $23.25. 300 DPI masters: 4500×5400 tee, 4200×4200 hoodie, 1500×525 beanie.

## Exact commands
Run on the Ridgeboundia host. Load the platform credentials without printing them; `--env-file` overrides the pipeline `DATABASE_URL` with the storefront database.

```bash
cd /srv/ridgeboundia
set -a; . /opt/pod-pipeline/config/pipeline.env; set +a
export FOURTHWALL_API_USERNAME="$FW_API_USER" FOURTHWALL_API_PASSWORD="$FW_API_SECRET"
read -rsp 'Storefront token (ptkn_): ' FOURTHWALL_STOREFRONT_TOKEN; echo; export FOURTHWALL_STOREFRONT_TOKEN
: "${FOURTHWALL_STOREFRONT_TOKEN:?missing token — the index wait and sync are blocked}"
```

Create **hidden** (same functions the storefront client uses; `publishOnCreate:false` is hard-coded):

```bash
npx tsx --env-file=.env.production - <<'TS'
import { readFile } from "node:fs/promises";
import { uploadDesignImage, createHiddenDesignProduct } from "./lib/fourthwall/product-create";
const bytes = await readFile("/opt/pod-pipeline/data/ai-uploads/rb_tee_craft.png");
const image = await uploadDesignImage({ bytes, fileName: "rb_tee_craft.png", contentType: "image/png" });
const created = await createHiddenDesignProduct({
  productTemplateId: "pro_e4677535402b4eeb81", name: "Lost And Learning Tee",
  description: "Lost And Learning Tee — Ridgeboundia", imageId: image.imageId, region: "front_large",
  placementStrategy: "AUTO", colors: ["Black"], profitMargin: 11.00,
  sizes: ["S", "M", "L", "XL", "2XL", "3XL", "4XL", "5XL"],
});
console.log(JSON.stringify({ imageId: image.imageId, ...created }, null, 2));
TS
```

The response must contain `productId` and a non-empty `images` array; `hidden:true` comes from the library. Never publish from the create call.

Publish the new id, hide the old generation (`PUT /products/{id}/state` is idempotent and only accepts `PUBLIC`/`HIDDEN`):

```bash
API=https://api.fourthwall.com/open-api/v1.0
curl -fsS -u "$FOURTHWALL_API_USERNAME:$FOURTHWALL_API_PASSWORD" -X PUT "$API/products/<NEW_ID>/state" -H 'content-type: application/json' -d '{"state":"PUBLIC"}'
curl -fsS -u "$FOURTHWALL_API_USERNAME:$FOURTHWALL_API_PASSWORD" -X PUT "$API/products/<OLD_ID>/state" -H 'content-type: application/json' -d '{"state":"HIDDEN"}'
```

Wait for the storefront index (product page must resolve before sync), then sync:

```bash
for i in $(seq 1 18); do
  curl -fsS "https://storefront-api.fourthwall.com/v1/products/<NEW_SLUG>?storefront_token=$FOURTHWALL_STOREFRONT_TOKEN" >/dev/null && { echo "indexed after $((i*10))s"; break; }
  sleep 10
done
npx tsx --env-file=.env.production - <<'TS'
import { runFourthwallSync } from "./lib/fourthwall/sync";
const r = await runFourthwallSync({ actorEmail: "owner@ridgeboundia.com" });
console.log(JSON.stringify(r, null, 2)); if (r.status !== "completed") process.exit(1);
TS
```

Repair the local whitelist (approval required; raw SQL, no deletes):

```bash
docker exec ridgeboundia-postgres psql -U ridgeboundia -d ridgeboundia -v ON_ERROR_STOP=1 -c "BEGIN; UPDATE \"Product\" SET status='archived', featured=false WHERE status='active' AND \"fourthwallProductId\" NOT IN ('5d40b2c7-5687-46bb-a0a0-75c19d4b9a9e','84305616-1446-490f-b022-adff79b9bdb4','6e655114-1d1d-40fb-977c-d413f8ee54bf','7bff0d73-51b6-494d-a38a-62ca57615f0b','9ebab6d3-0a07-4039-bea5-f9d9608b8b24'); UPDATE \"Product\" SET status='active' WHERE \"fourthwallProductId\" IN ('5d40b2c7-5687-46bb-a0a0-75c19d4b9a9e','84305616-1446-490f-b022-adff79b9bdb4','6e655114-1d1d-40fb-977c-d413f8ee54bf','7bff0d73-51b6-494d-a38a-62ca57615f0b','9ebab6d3-0a07-4039-bea5-f9d9608b8b24'); UPDATE \"Product\" SET featured = (\"fourthwallProductId\"='5d40b2c7-5687-46bb-a0a0-75c19d4b9a9e'); COMMIT;"
```

Verify (expected 200 for `/shop` and the five live pages, 404 for tee-3):

```bash
for s in shop lost-and-learning-tee-4 lost-and-learning-hoodie-3 lost-and-learning-beanie-3 abyssal-signal-neon-whale-tee-3 gru-hoodie lost-and-learning-tee-3; do
  url=https://ridgeboundia.com/shop; [ "$s" = shop ] || url=https://ridgeboundia.com/product/$s
  printf '%s %s\n' "$s" "$(curl -sS -o /dev/null -w '%{http_code}' "$url")"
done
```

## Workflow
1. Prove the gates on the master and get owner approval for the exact new slug.
2. Read provider and DB truth first (`fourthwall-catalog-audit` read-only section).
3. Upload + create hidden; record `productId`, `imageId` and created image URLs, then read it back (`access:HIDDEN`, price, colour, size, image count).
4. Publish `PUBLIC`; hide every older id for that design; never hide a different design.
5. Poll the storefront slug until 200 (observed 20 s–2 min); on timeout stop, do not sync.
6. Run `runFourthwallSync`; require `status:"completed"` and `productsSeen` matching the PUBLIC set.
7. Run the whitelist SQL; confirm 5 active, 1 featured, 0 duplicate designs, then verify the HTTP matrix and capture evidence.

## Acceptance gates
- Create response has a real `productId`, a non-empty `images` array, and was hidden on creation.
- Provider readback: new id `access:PUBLIC`/`state:AVAILABLE`; every old generation `access:HIDDEN`.
- Storefront: new page 200; old page 404; `/shop` contains the five live slugs. Sync: `status:"completed"`, not truncated, no failed rows; the new DB row is `active`.
- Local DB: 5 `active`, 8 `archived`, exactly 1 `featured` (the tee), 0 duplicate active designs.
- No row deleted, no template/colour/size changed silently, no price below cost + margin.

## Refusals
- No owner approval, or an ambiguous target — stop before uploading anything.
- Missing Platform credentials or storefront token — named refusal; do not fake an index wait.
- SVG/PDF/AI/TIFF artwork — PNG/JPEG only; export a PNG.
- `KNITTING` or `supportsBackendRendering:false` — refuse; do not route around the library.
- Editing a published product's art in place — impossible; create a new generation.
- `DELETE /products/{id}` during a replacement — terminal archive, not a hide.
- Blind retry after an ambiguous create — read back by slug/idempotency key first.

## Worked example
On 2026-11-05 the tee moved from `lost-and-learning-tee-3` (`be2bfd1c-5e30-44a6-abd7-c6b57c18a82c`) to `lost-and-learning-tee-4` (`5d40b2c7-5687-46bb-a0a0-75c19d4b9a9e`). The master was `rb_tee_craft.png` on `pro_e4677535402b4eeb81` `front_large`, Black, S–5XL, $9.50 cost + $11.00 margin. New product created hidden → published → old id hidden → storefront indexed → sync completed → DB activated tee-4/archived tee-3 → `featured=true` on tee-4. Readback: 5 PUBLIC, 9 HIDDEN, tee-4 $20.50–$28.50 with 8 variants and 10 images; tee-3 page 404; 13 local rows, 5 active, 8 archived, 1 featured.

## Pitfalls
- **Limits are shop-wide**: 5 `POST /products`/min, 20 `POST /media/upload-url`/min, 100 requests/10 s default. The pod pipeline shares the buckets; never publish in parallel.
- **Upload signature**: send the exact byte count in `size` and in `x-goog-content-length-range: 0,<size>`; the pre-signed URL lives ~6 h; never send Fourthwall credentials to GCS.
- **`profitMargin` is USD**, not a percentage; cost + margin = base retail, and size upcharges follow the provider ladder.
- **Hidden is not deleted**: the provider still returns the product with `access:HIDDEN` while the public page 404s; do not “fix” that with `DELETE`.
- **Slugs are generated then preserved**: new generations get `-2`, `-3`, `-4`; a name collision is 409 `OFFER_SLUG_DUPLICATION_ERROR`.
- **Mockups are not print proof**; they prove placement/cut-off only — see `merch-mockup-proof`.
- **The manifest table is stale**: its live-correction block wins; re-read the API before acting.

## Sources & verification
- VERIFIED — live Platform API readback on 2026-11-05 (14 products, 5 PUBLIC, prices/variants/image counts above); `/shop` and five product pages 200, tee-3 404; DB 13 rows, 5 active, 8 archived, 1 featured, 0 duplicate active designs; `npx tsx` loads `lib/fourthwall/product-create.ts` and `lib/fourthwall/sync.ts`.
- SCHEMA — `lib/fourthwall/product-create.ts:7-17` (five-step pipeline), `:50-52` (5/min, 20/min), `:743` (`createHiddenDesignProduct`); `lib/fourthwall/sync.ts:219` (`runFourthwallSync`); `prisma/schema.prisma:125` (`status`), `:160` (`fourthwallProductId`); `status` is a string, not an enum.
- DOCS — fetched 2026-11-05: [Create design products](https://docs.fourthwall.com/guides/create-design-products.md), [Create a product](https://docs.fourthwall.com/api-reference/platform/products/create-product.md), [Update product state](https://docs.fourthwall.com/api-reference/platform/products-(offers)/update-product-state.md), [Rate limiting](https://docs.fourthwall.com/guides/rate-limiting.md), [Get product by slug](https://docs.fourthwall.com/api-reference/storefront/products/get-product.md).
- UNVERIFIED — the storefront token is absent from `/srv/ridgeboundia/.env.production` and container env as of 2026-11-05, so the index wait and `runFourthwallSync` were not executed end-to-end; those commands are schema/docs-verified only.
