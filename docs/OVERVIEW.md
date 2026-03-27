# Beckn Protocol v2.0.0 — Engineering Overview

> **Status**: Release Candidate · **Repo**: `beckn/protocol-specifications-v2` · **15-min call reference**

---

## 1. What Is This?

A **ground-up redesign** of the Beckn Protocol. v2 does not patch v1 — it replaces the data model, discovery architecture, and registry layer while keeping the same async transaction philosophy.

Three things ship in this repo:
| Artifact | Path | What it is |
|---|---|---|
| Unified API spec | `api/beckn.yaml` | OpenAPI 3.1.1 — Discovery + Transaction + Catalog Publish |
| Core schema | `schema/core/v2/attributes.yaml` | The 10 shared entity types every network uses |
| Domain schema packs | `schema/<UseCaseName>/v<n>/` | Pluggable, composable attribute bundles per vertical |

---

## 2. What Changed From v1 (The Four Big Shifts)

### 2.1 Schema format: OpenAPI/JSON Schema → JSON-LD + schema.org
- v1 used ad-hoc JSON fields inside a Beckn envelope
- v2 every entity is a **JSON-LD graph** with `@context`, `@type`, and explicit `schema:` mappings
- Result: off-the-shelf RDF tools, graph DBs, and semantic validators work out of the box

### 2.2 Discovery: BG multicast → CDS push model
- v1: BAP → Beckn Gateway → multicast fan-out to all BPPs → `on_search` callbacks
- v2: BPPs **push catalogs** to a Catalog Discovery Service (CDS) asynchronously; BAPs **query CDS** for results
- Transactions (`/select`, `/init`, `/confirm`, …) still go BAP → BPP directly — nothing changed there

```
v1:  BAP ──search──▶ BG ──fan-out──▶ BPP1, BPP2
                          ◀─on_search─

v2:  BPP1 ──push──▶ CDS  (continuous, async)
     BAP  ──query──▶ CDS ──results──▶ BAP
     BAP  ──select/init/confirm──▶ BPP  (unchanged)
```

### 2.3 Registry: Beckn lookup/subscribe → DeDi-compliant directory
- v1 had a bespoke Beckn registry with custom `lookup` / `subscribe` APIs
- v2 registry is a **DeDi (Decentralized Directory) protocol**-compliant public directory
- Participant records (DID, endpoints, keys, capabilities) are standard DeDi entries — interoperable across ecosystems

### 2.4 Composability: monolithic domain blobs → core + schema packs
- v1: adding a new sector required patching the core or creating sector-specific APIs
- v2: core is a **small, stable set of types**; domain specifics live in separate **Attribute Packs**
- Any entity (`Item`, `Order`, `Fulfillment`, …) has an `*Attributes` field typed as `Attributes` — a JSON-LD bag that accepts any domain context

---

## 3. Repo Structure

```
protocol-specifications-v2/
├── api/
│   └── beckn.yaml              ← Single unified OpenAPI spec (all 3 API families)
├── schema/
│   ├── core/v2/                ← Core entity types (shared by all networks)
│   │   ├── attributes.yaml     ← OpenAPI schemas: Catalog, Item, Offer, Order, …
│   │   ├── context.jsonld      ← beckn: namespace → schema.org mappings
│   │   └── vocab.jsonld        ← beckn: term definitions
│   ├── EvChargingService/v1/   ← Domain pack (EV charging)
│   ├── EvChargingOffer/v1/
│   ├── EvChargingPointOperator/v1/
│   ├── EvChargingSession/v1/
│   └── PaymentSettlement/v1/
├── docs/                       ← TBD (governance docs, guides)
└── governance/                 ← TBD (WG charters, RFC process)
```

---

## 4. Core Entity Model (`schema/core/v2/attributes.yaml`)

Ten stable types. **All** domain specifics attach via the `Attributes` bag.

| Entity | Maps to | Key fields |
|---|---|---|
| `Catalog` | — | `beckn:items[]`, `beckn:offers[]`, `beckn:bppId` |
| `Item` | — | `beckn:descriptor`, `beckn:provider`, **`beckn:itemAttributes`** |
| `Offer` | `schema:Offer` | `beckn:items[]`, `beckn:price`, **`beckn:offerAttributes`** |
| `Provider` | — | `beckn:locations[]`, `beckn:rating`, **`beckn:providerAttributes`** |
| `Order` | `schema:Order` | `beckn:orderStatus`, `beckn:seller`, `beckn:orderItems[]`, **`beckn:orderAttributes`** |
| `OrderItem` | `schema:OrderItem` | `beckn:orderedItem`, `beckn:quantity`, **`beckn:orderItemAttributes`** |
| `Payment` | — | `beckn:paymentStatus`, `beckn:amount`, **`beckn:paymentAttributes`** |
| `Fulfillment` | — | `beckn:mode` (DELIVERY/PICKUP/RESERVATION/DIGITAL), **`beckn:deliveryAttributes`** |
| `Buyer` | `schema:Person/Org` | `beckn:id`, `beckn:role`, **`beckn:buyerAttributes`** |
| `Invoice` | `schema:Invoice` | `beckn:number`, `beckn:totals`, **`beckn:invoiceAttributes`** |

**`Attributes`** — the plug-in bag (used by every `*Attributes` field):
```yaml
Attributes:
  required: ["@context", "@type"]
  additionalProperties: true   # ← domain fields go here
```
Any domain pack supplies its own `@context` URI + `@type`. Unknown packs are safely ignored at runtime.

---

## 5. API Surface (`api/beckn.yaml`)

### 5.1 Discovery API (BAP ↔ CDS)
| Endpoint | Direction | Purpose |
|---|---|---|
| `GET /beckn/discover` | BAP → CDS | Text search, JSONPath filters, spatial (CQL2), multimodal |
| `POST /beckn/on_discover` | CDS → BAP | Async callback with catalog results |
| `GET /beckn/discover/browser-search` | Browser → CDS | URL-param search; returns HTML or JSON |

### 5.2 Transaction API (BAP ↔ BPP) — unchanged philosophy from v1
`/beckn/select` → `/beckn/on_select` → `/beckn/init` → `/beckn/on_init` → `/beckn/confirm` → `/beckn/on_confirm` → `/beckn/status` → `/beckn/on_status` → `/beckn/update` → `/beckn/on_update` → `/beckn/cancel` → `/beckn/on_cancel` → `/beckn/track` → `/beckn/on_track` → `/beckn/support` → `/beckn/on_support` → `/beckn/rating` → `/beckn/on_rating`

All return `AckResponse` (ACK/NACK) immediately; BPP delivers data via callback.

### 5.3 Catalog Publish API (BPP → CDS)
| Endpoint | Direction | Purpose |
|---|---|---|
| `POST /beckn/catalog/publish` | BPP → CDS | Push one or more Catalogs for indexing |
| `POST /beckn/catalog/on_publish` | CDS → BPP | Per-catalog result: ACCEPTED / REJECTED / PARTIAL |

---

## 6. Domain Schema Packs (Current)

5 packs ship today, all EV-charging related (reference vertical):

| Pack | Version | What it models |
|---|---|---|
| `EvChargingService` | v1 | Full charging service item + profile + renderer |
| `EvChargingOffer` | v1 | Tariff/pricing offer for a charging session |
| `EvChargingPointOperator` | v1 | CPO provider attributes |
| `EvChargingSession` | v1 | Active / completed session state |
| `PaymentSettlement` | v1 | Payment settlement record |

### Anatomy of a Pack
```
schema/EvChargingService/v1/
├── attributes.yaml       ← OpenAPI schemas for domain-specific types
├── context.jsonld        ← Maps domain props → schema.org / beckn: IRIs
├── vocab.jsonld          ← Domain vocabulary (RDFS definitions)
├── profile.json          ← Minimal discovery fields, index hints, privacy guidance
├── renderer.json         ← UI card / chip templates (HTML + JSON data paths)
├── README.md
└── examples/schema/      ← Working JSON-LD examples per scenario
```

---

## 7. Key Engineering Rules (Locked Decisions)

1. **Core is frozen** — new verticals → new packs, never patch core types
2. **`additionalProperties: true` on `Attributes`** — unknown fields must not cause parse failures; receivers ignore what they don't understand
3. **All `@context` URIs must resolve** — either raw GitHub URLs (RC phase) or hosted at a stable IRI on publish
4. **All coords are GeoJSON / EPSG:4326 [lon, lat]** — `GeoJSONGeometry` is the single geometry type
5. **v2 is a new protocol line** — dual-stack in transition (v1 for production, v2 for pilots); no in-place migration path exists yet

---

## 8. What's Not Done Yet

| Area | Status |
|---|---|
| `docs/` content | Placeholder — TBD |
| `governance/` | Placeholder — TBD |
| DeDi registry spec | Referenced in README; no implementation in this repo |
| Migration tooling (v1 → v2) | Not in repo; described as a network responsibility |
| Non-EV domain packs | None yet; EV is the reference vertical |
| Test / validation scripts | `migrations/`, `validations/`, `tests/` folders defined in convention but empty in existing packs |

---

*Last updated: 2026-03-02 · Source: `beckn/protocol-specifications-v2` @ `e1de22c`*
