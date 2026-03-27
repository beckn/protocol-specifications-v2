# Core Schema First-Class Properties Analysis

**Status:** Draft  
**Authors:** Ravi Prakash, Abhishek (Beckn Foundation)  
**Created:** 2026-03-13  
**Purpose:** Inform the design of `beckn-proposed.yaml` — the merged, developer-friendly, backward-compatible Beckn Protocol v2.0 API specification.

---

## Context and Decision Background

On 2026-03-13, the Beckn chief architect Pramod Varma reviewed three competing versions of the v2.0 API specification and concluded:

- **[`beckn-ravis-original-version.yaml`](../api/v2.0.0/beckn-ravis-original-version.yaml)** — Author: Ravi Prakash. Stress-tested across multiple domains (retail, mobility, logistics, energy, healthcare). Uses the `Order` schema from the v2.0-rc1 release. Introduces a two-phase `context.try` pattern for cancellation, update, rate, and support actions.
- **[`beckn-v2-abhisheks-version.yaml`](../api/v2.0.0/beckn-v2-abhisheks-version.yaml)** — Author: Abhishek. More developer-friendly structure. Introduces the generalized `Contract` model with `commitments`, `consideration`, `performance`, and `settlements`. Uses `oneOf: [order, contract]` on every transaction message for explicit backward compatibility.
- **[`beckn.yaml`](../api/v2.0.0/beckn.yaml)** — Auto-generated transport skeleton. Delegates all payload schema to `https://schema.beckn.io` via external `$ref`. No inline schemas. Includes important transport-layer schemas: `Signature`, `CounterSignature`, `InReplyTo`, `Ack`, `AckNoCallback`, `NackBadRequest`, `NackUnauthorized`, `ServerError`.

The verdict: merge all three into a single `beckn-proposed.yaml` that is:
1. **Minimalist** — only what is essential in the core API spec; everything else deferred to `schema.beckn.io`.
2. **Pragmatic / Developer-friendly** — clear naming, explicit backward-compatible `oneOf` constructs.
3. **Backward compatible** with the previous 2.0-rc1 release.

---

## Design Principles (Ratified)

| # | Principle | Notes |
|---|-----------|-------|
| 1 | All domain-agnostic schemas are sourced from `schemas/schema` (the `beckn/core_schema` repo) | Check each schema: does it **really** belong in the API spec, or does it live entirely in `schemas/schema`? |
| 2 | Full backward compatibility with 2.0-rc1 | Transaction message envelopes MUST carry `oneOf: [order, contract]` (not just `contract`) |
| 3 | New APIs ⇒ new version (2.x), but MUST be backward compatible with 2.0 | Applies to any new endpoints added |
| 4 | Extended protocol modules (IGM, R&S, Reputation) go in `beckn-extended.yaml` | Not in the core spec |
| 5 | Remove the `/beckn/{endPoint}` generator module | No auto-generated abstract endpoint; concrete named paths only |
| 6 | All schemas MUST have a `$id` pointing to their canonical URI in `schema.beckn.io` | Pattern: `https://schema.beckn.io/{SchemaName}/v2.0` |

---

## Filtering Mechanism: Should a Schema Live in the API Spec or Only in `schemas/schema`?

A schema earns a **first-class slot in `beckn-proposed.yaml`** only if it satisfies ALL of the following tests:

| Test | Question | If YES → in API spec | If NO → in `schemas/schema` only |
|------|----------|---------------------|----------------------------------|
| **T1 — Envelope test** | Is this schema carried directly in the `message` field of at least one API request or response? | ✅ | ❌ |
| **T2 — Interop-boundary test** | Does every BAP and BPP need to agree on this schema's shape to interoperate? | ✅ | ❌ |
| **T3 — Domain-agnosticism test** | Is this schema equally meaningful across retail, mobility, healthcare, logistics, energy? | ✅ | ❌ |
| **T4 — Minimalism test** | Would removing this schema force implementors to use untyped attributes (`Attributes`) instead, reducing interoperability? | ✅ | ❌ |

Schemas that fail T1 (not directly in a message body) still live in `schemas/schema` and are referenced by the first-class schemas via `$ref: https://schema.beckn.io/...`.

---

## First-Class Schema Analysis

### 1. `Context`

> **Style note:** All `Context` property names are **camelCase** per the v2.0 style guide, matching `schemas/schema/Context/v2.0/attributes.yaml`.
>
> **On-ground experience:** All fields below are REQUIRED. Production deployments have demonstrated that partial context causes routing failures, replay attacks, and non-repudiation gaps. No context field may be omitted.

| Property | Type | Required | Justification |
|----------|------|----------|---------------|
| `action` | `$ref BecknEndpoint` | ✅ | The action tells the receiver which message payload schema to apply. Without it, no dispatch. |
| `bapId` | `string` | ✅ | Identity of the Beckn Application Platform (FQDN). Without it, the BPP cannot verify the caller's identity or route callbacks correctly. |
| `bapUri` | `string (uri)` | ✅ | Callback URI for the BAP. Without this, the BPP cannot call back — the async flow breaks entirely. |
| `bppId` | `string` | ✅ | Identity of the BPP. Required for the BAP to verify the callback origin and prevent spoofing. |
| `bppUri` | `string (uri)` | ✅ | BPP's endpoint. Required for routing direct calls from the BAP. |
| `transactionId` | `string (uuid)` | ✅ | Ties all messages in a single transaction together. Non-repudiation anchor. Without it, the BAP cannot correlate callbacks to their originating requests. |
| `messageId` | `string (uuid)` | ✅ | Unique per-message identifier. Required for deduplication, idempotency enforcement, and `InReplyTo` binding. Production experience: duplicate messages without a stable `messageId` caused double-processing and double-charging. |
| `timestamp` | `string (date-time)` | ✅ | Used in signature verification and replay attack prevention. Without it, signatures cannot be validated and the system is vulnerable to replay attacks. |
| `version` | `string` | ✅ | Backward compatibility gating — receivers use this to route to the correct handler version. Without it, 2.0-rc1 and 2.0.0 implementations cannot coexist on the same network. |
| `ttl` | `string (ISO 8601 duration)` | ✅ | Defines message validity window. Without it, stale messages (e.g., from network delays, retries) cannot be rejected, leading to ghost transactions. |
| `networkId` | `string` | ✅ | Scopes the request to a specific Beckn network. Without it, multi-network deployments cannot disambiguate which network a request is addressed to. |
| `try` | `boolean` | ✅ | **Two-phase negotiation flag.** `true` = preview consequences without committing state. `false` = commit. Without an explicit `try` value, receivers cannot distinguish preview from commit — production systems defaulted to accidental commits. |
| `lineage` | `LineageEntry[]` | ✅ | Cross-transaction causal attribution (max 1 entry). Required for audit trails, non-repudiation, and agentic transaction chains. Without lineage, cascaded or AI-triggered transactions cannot be traced back to their origin. |

**Canonical source:** [`schemas/schema/Context/v2.0/attributes.yaml`](../../schemas/schema/Context/v2.0/attributes.yaml) — `$id: https://schema.beckn.io/Context/v2.0`  
**Note:** Property names are camelCase (`bapId`, `bapUri`, `bppId`, `bppUri`, `transactionId`, `messageId`, `networkId`). The `try` flag is a first-class `Context` property (on-ground learning from production); it is NOT an inline override at the endpoint level.  
**Proposed `$id`:** `https://schema.beckn.io/Context/v2.0`

---

### 2. `Catalog`

**Verdict: FIRST-CLASS.** The `on_discover` callback message is `{ catalogs: Catalog[] }`. Every BAP and BPP must agree on `Catalog` to perform discovery.

| Property | Type | Required | Justification |
|----------|------|----------|---------------|
| `id` | `string` | ✅ | Unique catalog identifier. Required for catalog-level operations (publish, index, reference). |
| `descriptor` | `Descriptor` | ✅ | Human-readable name and description. Required for display in all UIs. |
| `bppId` | `string` | ✅ | Links catalog to its owning BPP. Required for routing `select` after discovery. |
| `bppUri` | `string (uri)` | ✅ | BPP endpoint for all post-discovery actions. |
| `items` | `oneOf [Item, Resource][]` | ✅ | Array of items in the catalog. Each entry is either a legacy `Item` (2.0-rc1 backward compat) or a new cross-domain `Resource`. Using `oneOf [Item, Resource]` allows old BAPs to continue sending/receiving `Item` objects while new implementations use the more abstract `Resource`. Both types share a common `id` + `descriptor` surface. |
| `offers` | `Offer[]` | ✅ (bc compat) | Backward compatible with 2.0-rc1. |
| `providers` | `Provider[]` | ✅ | A catalog may be hosted by a CDS on behalf of multiple BPPs. Provider association is required. |
| `validity` | `TimePeriod` | ❌ | Optional. Defined in `schemas/schema/TimePeriod`. Referenced via `$ref`. |
| `isActive` | `boolean` | ❌ | Optional. CDS-level operational attribute. Not needed in core; defaults to `true`. |

**Source for new `resources` field:** Abhishek's version ([`beckn-v2-abhisheks-version.yaml`](../api/v2.0.0/beckn-v2-abhisheks-version.yaml)) — introduces `beckn:resources[]` alongside `beckn:items[]`  
**Author of `resources` field:** Abhishek  
**Proposed `$id`:** `https://schema.beckn.io/Catalog/v2.0`

---

### 3. `Intent` (DiscoverMessage)

**Verdict: FIRST-CLASS.** The `discover` request message is `{ intent: Intent }`. The BAP expresses what it is looking for; the BPP/CDS uses it to filter its catalog.

| Property | Type | Required | Justification |
|----------|------|----------|---------------|
| `item` | `Item` (partial) | ❌ | Optional descriptor fragment used to match against catalog items. |
| `provider` | `Provider` (partial) | ❌ | Optional provider filter (name, location). |
| `fulfillment` | `Fulfillment` (partial) | ❌ | Optional fulfillment filter (pickup/delivery location, time). |
| `payment` | `Payment` (partial) | ❌ | Optional payment method filter. |
| `category` | `Category` | ❌ | Optional category filter. |
| `offer` | `Offer` (partial) | ❌ | Optional offer filter. |
| `tags` | `Tag[]` | ❌ | Optional tag-based filter. |

**Additional properties from Ravi's version:**

| Property | Type | Required | Justification |
|----------|------|----------|---------------|
| `textSearch` | `string` | ❌ (one of) | Free-text search query. Required for discovery to be practically usable by non-technical consumers. |
| `filters` | JSONPath expression | ❌ (one of) | Structured filtering via RFC 9535 JSONPath. Required for programmatic consumers. |
| `spatial` | `SpatialConstraint[]` | ❌ (one of) | Geo-spatial filtering. Required for location-based discovery (mobility, logistics). |
| `mediaSearch` | `MediaSearch` | ❌ | Optional visual/audio search input. |

**Source:** Ravi's version for `textSearch`, `filters`, `spatial`, `mediaSearch`. Abhishek's version for the structural `oneOf` validation pattern.  
**Authors:** Ravi Prakash (search fields), Abhishek (validation pattern)  
**Proposed `$id`:** `https://schema.beckn.io/Intent/v2.0`

---

### 4. `Order` (Legacy — Backward Compatibility)

**Verdict: FIRST-CLASS (retained for backward compatibility only).** Every transaction API from 2.0-rc1 carries `order` in its `message`. Removing `Order` from the API spec would break all existing implementations.

| Property | Type | Required | Justification |
|----------|------|----------|---------------|
| `id` | `string` | ❌ (set by BPP on confirm) | Primary identifier. MUST be stable post-confirmation. |
| `items` | `OrderItem[]` | ✅ (select+) | Selected items. Core of what is being ordered. |
| `fulfillment` | `Fulfillment` | ✅ (init+) | How the order is delivered. There is NO order without fulfillment — without fulfillment, what is the point of an order? |
| `billing` | `Billing` | ✅ (init+) | Billing details for invoice generation. Required for all commercial orders. |
| `payment` | `Payment` | ✅ (confirm+) | Payment terms. An unconfirmed order has no payment; a confirmed order MUST have payment terms. |
| `quote` | `Quote` | ✅ (on_select+) | Price breakdown. Required for the BAP to display the price to the consumer. |
| `status` | `string (enum)` | ✅ (confirm+) | Order lifecycle state. Required for fulfillment tracking. |
| `cancellationPolicy` | `CancellationPolicy` | ❌ | Optional. Referenced from `schemas/schema`. |
| `documents` | `Document[]` | ❌ | Optional. Referenced from `schemas/schema`. |
| `tags` | `Tag[]` | ❌ | Optional. |

**Deprecation note:** `Order` is deprecated in v2.0. Its IRI is `beckn:Contract` in the JSON-LD context. New implementations SHOULD use `Contract`. The `order` key in message envelopes MUST be retained in `beckn-proposed.yaml` via `oneOf: [order, contract]`.  
**Source:** Ravi's version ([`beckn-ravis-original-version.yaml`](../api/v2.0.0/beckn-ravis-original-version.yaml)) — `$ref` to `schema/core/v2.1/attributes.yaml#Order`  
**Author:** Ravi Prakash  
**Proposed `$id`:** `https://schema.beckn.io/Order/v2.0` (alias for `Contract`)

---

### 5. `Contract` (New — Generalized)

**Verdict: FIRST-CLASS.** The generalized, domain-neutral replacement for `Order`. Carries the same information but abstracts it to be meaningful across commerce, mobility, energy, hiring, and data licensing.

The key abstraction decisions from Abhishek's version:

| Concept (Ravi / v2.0-rc1) | Concept (Abhishek / proposed) | Justification for abstraction |
|---------------------------|-------------------------------|-------------------------------|
| `orderItems` | `commitments` | A contract is not always about ordering items. A mobility ride contract has no "items". |
| `fulfillment` | `performance` | "Fulfillment" is commerce-specific. "Performance" covers API access, service provisioning, carbon transfer, etc. |
| `payment` | `consideration` + `settlements` | Payment is a special case of consideration. A barter contract, a data-for-service contract, or a token exchange has no "payment". |
| `cancellationPolicy` | Part of `contractAttributes` | Domain packs define cancellation semantics. Core only knows a contract can be cancelled. |

| Property | Type | Required | Justification |
|----------|------|----------|---------------|
| `id` | `string` | ✅ | Globally unique contract identifier. Required for all post-confirmation actions. |
| `status` | `string (enum)` | ✅ | Contract lifecycle state: `DRAFT → PENDING → CONFIRMED → IN_PROGRESS → COMPLETED → CANCELLED → FAILED → TERMINATED`. A contract without a knowable state cannot be tracked. |
| `parties` | `Party[]` | ✅ | Min 2 parties with roles. A contract without at least two parties is not a contract. |
| `commitments` | `Commitment[]` | ✅ (select+) | What is being agreed. No contract without commitments. This is the minimum semantic payload. |
| `consideration` | `Consideration[]` | ❌ | What is owed in exchange. Optional because barter/service contracts may not express monetary value at this layer. |
| `performance` | `Performance[]` | ❌ | How the contract is executed. Optional at select; required by confirm for delivery-based contracts. |
| `settlements` | `Settlement[]` | ❌ | Discharge records for consideration. Optional — populated post-payment. |
| `contractAttributes` | `Attributes` | ❌ | Domain-specific extension bag. |

**Source:** Abhishek's version ([`beckn-v2-abhisheks-version.yaml`](../api/v2.0.0/beckn-v2-abhisheks-version.yaml))  
**Author:** Abhishek  
**GitHub file:** [`beckn-v2-abhisheks-version.yaml` lines 1088–1242](../api/v2.0.0/beckn-v2-abhisheks-version.yaml)  
**Proposed `$id`:** `https://schema.beckn.io/Contract/v2.0`

---

### 6. `Consideration`

**Verdict: FIRST-CLASS (companion to `Contract`).** The generalized representation of value exchanged. Replaces the commerce-specific `Payment` at the contract level.

| Property | Type | Required | Justification |
|----------|------|----------|---------------|
| `type` | `string (enum)` | ✅ | Declares what kind of consideration: `MONETARY`, `TOKEN`, `CREDIT`, `ASSET`, `SERVICE`, `OTHER`. Required for receivers to know how to interpret the consideration. |
| `status` | `string (enum)` | ✅ | Lifecycle: `PROPOSED → AGREED → PENDING → SETTLED → FAILED → CANCELLED`. Required for payment/settlement tracking. |
| `amount` | `object` | ❌ | Optional — applies only to MONETARY and TOKEN types. Domain packs fill in currency, value, etc. |
| `considerationAttributes` | `Attributes` | ❌ | Extension bag for domain-specific fields. |

**Backward compatibility note:** The legacy `Payment` schema remains available in `schemas/schema` and is referenced via `$ref` in the `Order.payment` property. `Consideration` replaces `Payment` at the `Contract` level.  
**Source:** Abhishek's version ([`beckn-v2-abhisheks-version.yaml`](../api/v2.0.0/beckn-v2-abhisheks-version.yaml))  
**Author:** Abhishek  
**Proposed `$id`:** `https://schema.beckn.io/Consideration/v2.0`

---

### 7. `Performance`

**Verdict: FIRST-CLASS (companion to `Contract`).** The generalized execution unit. Replaces the commerce-specific `Fulfillment` at the contract level.

| Property | Type | Required | Justification |
|----------|------|----------|---------------|
| `id` | `string` | ✅ | Unique performance unit identifier. Required for tracking and support linking. |
| `status` | `string (enum)` | ✅ | Execution state: `PLANNED → IN_PROGRESS → COMPLETED → FAILED → CANCELLED`. Required for `track` and `status` actions. |
| `mode` | `string (enum)` | ❌ | `DELIVERY`, `SERVICE`, `ACCESS`, `TRANSFER`, `EXECUTION`, `OTHER`. Optional — conveys the type of performance to domain-agnostic renderers. |
| `commitmentRefs` | `string[]` | ❌ | References to commitments fulfilled by this performance unit. Optional — links execution to agreement. |
| `performanceAttributes` | `Attributes` | ❌ | Domain-specific extension bag (delivery address, service slot, access credentials, etc.). |

**Backward compatibility note:** The legacy `Fulfillment` schema remains available and is used in the `Order.fulfillment` property for backward compatibility. `Performance` replaces it at the `Contract` level.  
**Source:** Abhishek's version ([`beckn-v2-abhisheks-version.yaml`](../api/v2.0.0/beckn-v2-abhisheks-version.yaml))  
**Author:** Abhishek  
**Proposed `$id`:** `https://schema.beckn.io/Performance/v2.0`

---

### 8. `Settlement`

**Verdict: FIRST-CLASS (companion to `Contract`).** Records the discharge of agreed consideration. Equivalent to a payment receipt at the contract level.

| Property | Type | Required | Justification |
|----------|------|----------|---------------|
| `type` | `string (enum)` | ✅ | `MONETARY`, `TOKEN`, `CREDIT`, `ASSET`, `SERVICE`, `OTHER`. Mirrors `Consideration.type`. |
| `status` | `string (enum)` | ✅ | `INITIATED → PENDING → COMPLETED → FAILED → CANCELLED`. |
| `amount` | `object` | ❌ | Optional. Applicable to monetary/token settlements. |
| `considerationRefs` | `string[]` | ❌ | Links to `Consideration` entries being discharged. |
| `settlementRef` | `string` | ❌ | External reference (payment gateway ID, blockchain tx hash). |
| `settlementAttributes` | `Attributes` | ❌ | Extension bag. |

**Source:** Abhishek's version ([`beckn-v2-abhisheks-version.yaml`](../api/v2.0.0/beckn-v2-abhisheks-version.yaml))  
**Author:** Abhishek  
**Proposed `$id`:** `https://schema.beckn.io/Settlement/v2.0`

---

### 9. `Tracking` (TrackMessage / OnTrackMessage)

**Verdict: FIRST-CLASS.** The `track` action message is `{ tracking: TrackingRequest }`. The `on_track` response is `{ tracking: Tracking }`. These are the minimal interop contracts for real-time tracking.

| Property (`TrackingRequest`) | Type | Required | Justification |
|------------------------------|------|----------|---------------|
| `id` | `string` | ✅ | Tracking identifier (maps to `orderId` or `contractId`). Required to identify what is being tracked. |
| `callbackUrl` | `string (uri)` | ❌ | Optional webhook for push-based tracking updates. |

| Property (`Tracking`) | Type | Required | Justification |
|-----------------------|------|----------|---------------|
| `url` | `string (uri)` | ❌ (one of) | A link to a tracking page or real-time feed. |
| `status` | `string (enum)` | ✅ | `ACTIVE`, `DISABLED`, `COMPLETED`. Required for the BAP to know whether tracking is live. |

**Source:** `TrackingRequest` from Ravi's version. `Tracking` from `schemas/schema/Tracking` (external).  
**Author of TrackingRequest:** Ravi Prakash  
**Proposed `$id` (Tracking):** `https://schema.beckn.io/Tracking/v2.0`

---

### 10. `Support` (SupportMessage / OnSupportMessage)

**Verdict: FIRST-CLASS.** The `support` action message references an entity by `refId`/`refType`. The `on_support` response carries `Support` info (channels, tickets). This is the minimal interop contract for customer support.

Abhishek's version improves on Ravi's by making the reference type explicit:

| Property (`support` message) | Type | Required | Justification |
|------------------------------|------|----------|---------------|
| `refId` | `string` | ✅ | ID of the entity for which support is requested. Cannot provide support without knowing what it is about. |
| `refType` | `string (enum)` | ✅ | `CONTRACT`, `ORDER`, `PERFORMANCE`, `FULFILLMENT`, `RESOURCE`, `OFFER`, `PROVIDER`, `AGENT`, `OTHER`. Abstracts over domain-specific entity types. |

**Source for `refType` enum:** Abhishek's version ([`beckn-v2-abhisheks-version.yaml`](../api/v2.0.0/beckn-v2-abhisheks-version.yaml) line 572)  
**Author of `refType`:** Abhishek  
**Source for `SupportInfo`/`Support` schema:** `schemas/schema/Support` (external)  
**Proposed `$id` (Support):** `https://schema.beckn.io/Support/v2.0`

---

### 11. `RatingInput` (rate / on_rate)

**Verdict: FIRST-CLASS.** The `rate` action carries `ratings: RatingInput[]`. The response carries optional aggregate display data.

| Property (`RatingInput`) | Type | Required | Justification |
|--------------------------|------|----------|---------------|
| `id` | `string` | ✅ | ID of the entity being rated. Without it, the rating cannot be associated. |
| `ratingCategory` | `string (enum)` | ✅ | `ORDER`, `FULFILLMENT`, `ITEM`, `PROVIDER`, `AGENT`, `SUPPORT`, `OTHER`. Rating category determines how the score is stored and displayed. |
| `value` | `number` | ✅ | The actual rating value. Required — a rating without a value is not a rating. |
| `feedback` | `Feedback` | ❌ | Optional free-text feedback. |

**Source:** `schemas/schema/RatingInput` (external). Rate action pattern resolution: adopt Abhishek's simpler single-phase `rate`/`on_rate` (drop `context.try` for rating). The `try` pattern adds complexity without sufficient benefit for the rating use case.  
**Proposed `$id` (RatingInput):** `https://schema.beckn.io/RatingInput/v2.0`

---

### 12. `CatalogPublishMessage` / `CatalogProcessingResult`

**Verdict: FIRST-CLASS.** `/beckn/catalog/publish` and `/beckn/catalog/on_publish` are in both Ravi's and Abhishek's versions. Required for the Catalog Publishing Service (CPS) module.

| Property (`CatalogPublishMessage`) | Type | Required | Justification |
|------------------------------------|------|----------|---------------|
| `catalogs` | `Catalog[]` | ✅ (min 1) | The catalogs to be published. Without catalogs, there is nothing to publish. |

| Property (`CatalogProcessingResult`) | Type | Required | Justification |
|--------------------------------------|------|----------|---------------|
| `catalogId` | `string` | ✅ | Identifies which catalog the result applies to. |
| `status` | `string (enum)` | ✅ | `ACCEPTED`, `REJECTED`, `PARTIAL`. Required for the publisher to know what was processed. |
| `errors` | `Error[]` | ❌ | Optional — present when `status` is `REJECTED` or `PARTIAL`. |
| `stats` | `object` | ❌ | Optional — item count, provider count, category count. |

**Source:** Ravi's version for field names. Abhishek's version for `PARTIAL` status enum value (better than `processing`).  
**Proposed `$id` (CatalogProcessingResult):** `https://schema.beckn.io/CatalogProcessingResult/v2.0`

---

## Schemas Explicitly Excluded from the API Spec

The following schemas appear in one or more versions but do NOT pass the filtering test for inclusion as first-class API-spec schemas. They are referenced via `$ref: https://schema.beckn.io/{Name}/v2.0` from within the first-class schemas:

| Schema | Reason for exclusion |
|--------|----------------------|
| `Address` | Sub-object of `Location`. Never appears directly in a `message` field. |
| `Location` | Sub-object of `Fulfillment`/`Performance`. Never directly in `message`. |
| `Person` | Sub-object of `Consumer`/`FulfillmentAgent`. Not in `message`. |
| `Organization` | Sub-object of `Provider`/`Consumer`. Not in `message`. |
| `Descriptor` | Purely structural/display schema. Sub-object of many top-level schemas. |
| `TimePeriod` | Utility type. Sub-object of `Catalog.validity`, `Offer.validity`. |
| `GeoJSONGeometry` | Sub-object of `SpatialConstraint`. |
| `SpatialConstraint` | Sub-object of `Intent`. |
| `MediaSearch` | Sub-object of `Intent`. |
| `MediaInput` | Sub-object of `MediaSearch`. |
| `MediaSearchOptions` | Sub-object of `MediaSearch`. |
| `PaymentTerms` | Sub-object of `Consideration` / legacy `Order.payment`. |
| `SettlementTerm` | Sub-object of `Settlement`. |
| `CancellationPolicy` | Sub-object of `Contract`/`Order` via `contractAttributes`. |
| `FulfillmentStage` | Sub-object of `Fulfillment`/`Performance`. |
| `Skill` | Sub-object of `FulfillmentAgent`. |
| `Credential` | Sub-object of `Provider`/`Consumer`. |
| `Provider` | Sub-object of `Catalog`. First-class in `schemas/schema` but not a direct `message` payload. |
| `Item` | Sub-object of `Catalog`. First-class in `schemas/schema` but not a direct `message` payload. |
| `Offer` | Sub-object of `Catalog`. First-class in `schemas/schema` but not a direct `message` payload. |

---

## Transport Layer Schemas (Inline in `beckn-proposed.yaml`)

These schemas live **inside `beckn-proposed.yaml`** (not in `schemas/schema`) because they are transport-layer concerns, not data model concerns:

| Schema | Source | Justification |
|--------|--------|---------------|
| `Signature` | [`components/schema/core.yaml`](../api/v2.0.0/components/schema/core.yaml) | HTTP Auth header format. Not a domain schema. |
| `CounterSignature` | [`components/schema/core.yaml`](../api/v2.0.0/components/schema/core.yaml) | Signed ACK body receipt. Not a domain schema. |
| `InReplyTo` | [`components/schema/core.yaml`](../api/v2.0.0/components/schema/core.yaml) | Cryptographic request-response binding. |
| `Ack` | [`components/schema/core.yaml`](../api/v2.0.0/components/schema/core.yaml) | Synchronous ACK/NACK envelope. |
| `AckNoCallback` | [`components/schema/core.yaml`](../api/v2.0.0/components/schema/core.yaml) | ACK with no async callback signalling. |
| `NackBadRequest` | [`components/schema/core.yaml`](../api/v2.0.0/components/schema/core.yaml) | 400 NACK envelope. |
| `NackUnauthorized` | [`components/schema/core.yaml`](../api/v2.0.0/components/schema/core.yaml) | 401 NACK envelope. |
| `ServerError` | [`components/schema/core.yaml`](../api/v2.0.0/components/schema/core.yaml) | 500 error envelope. |
| `Error` | [`components/schema/core.yaml`](../api/v2.0.0/components/schema/core.yaml) | Base error object used by NACK envelopes. |

---

## `$id` Canonical URI Strategy

Every schema in `schemas/schema` that is referenced from `beckn-proposed.yaml` MUST have a `$id` added to its `attributes.yaml` file in the format:

```yaml
$id: https://schema.beckn.io/{SchemaName}/v2.0
```

This allows JSON Schema 2020-12 validators to resolve schemas by their canonical URI. It also aligns with the `schema.beckn.io` deployment used by `beckn.yaml`.

**Priority order for adding `$id`:**
1. `Context`
2. `Contract` + `Consideration` + `Performance` + `Settlement` + `Commitment`
3. `Catalog` + `Intent`
4. `Order` (backward compat alias for `Contract`)
5. `Tracking` + `TrackingRequest`
6. `Support` + `SupportTicket`
7. `RatingInput` + `Rating`
8. `CatalogProcessingResult`

---

## Proposed `beckn-proposed.yaml` Path Structure

| Path | HTTP Method | Message Schema (proposed) |
|------|-------------|--------------------------|
| `/beckn/discover` | `POST` | `{ context, message: { intent: Intent } }` |
| `/beckn/on_discover` | `POST` | `{ context, message: { catalogs: Catalog[] } }` |
| `/beckn/select` | `POST` | `{ context, message: oneOf[ { order: Order }, { contract: Contract } ] }` |
| `/beckn/on_select` | `POST` | `{ context, message: oneOf[ { order: Order }, { contract: Contract } ] }` |
| `/beckn/init` | `POST` | `{ context, message: oneOf[ { order: Order }, { contract: Contract } ] }` |
| `/beckn/on_init` | `POST` | `{ context, message: oneOf[ { order: Order }, { contract: Contract } ] }` |
| `/beckn/confirm` | `POST` | `{ context, message: oneOf[ { order: Order }, { contract: Contract } ] }` |
| `/beckn/on_confirm` | `POST` | `{ context, message: oneOf[ { order: Order }, { contract: Contract } ] }` |
| `/beckn/status` | `POST` | `{ context, message: oneOf[ { order: { id } }, { contract: { id } } ] }` |
| `/beckn/on_status` | `POST` | `{ context, message: oneOf[ { order: Order }, { contract: Contract } ] }` |
| `/beckn/update` | `POST` | `{ context, message: oneOf[ { order: Order }, { contract: Contract } ] }` |
| `/beckn/on_update` | `POST` | `{ context, message: oneOf[ { order: Order }, { contract: Contract } ] }` |
| `/beckn/cancel` | `POST` | `{ context, message: oneOf[ { order: { id, reason } }, { contract: { id, reason } } ] }` |
| `/beckn/on_cancel` | `POST` | `{ context, message: oneOf[ { order: Order }, { contract: Contract } ] }` |
| `/beckn/track` | `POST` | `{ context, message: { tracking: TrackingRequest } }` |
| `/beckn/on_track` | `POST` | `{ context, message: { tracking: Tracking } }` |
| `/beckn/rate` | `POST` | `{ context, message: { ratings: RatingInput[] } }` |
| `/beckn/on_rate` | `POST` | `{ context, message: { received: bool, aggregate?: object, feedbackForm?: Form } }` |
| `/beckn/support` | `POST` | `{ context, message: { refId: string, refType: enum, support?: SupportInfo } }` |
| `/beckn/on_support` | `POST` | `{ context, message: { support: Support } }` |
| `/beckn/catalog/publish` | `POST` | `{ context, message: { catalogs: Catalog[] } }` |
| `/beckn/catalog/on_publish` | `POST` | `{ context, message: { results: CatalogProcessingResult[] } }` |

**Removed from `beckn-proposed.yaml` (moved to `beckn-extended.yaml` or deferred):**
- `/beckn/{endPoint}` abstract endpoint (generator module removed per design principle #5)
- Issue & Grievance Management endpoints
- Reconciliation & Settlement endpoints
- Reputation System endpoints

---

## Key Decisions Summary

| Decision | Rationale |
|----------|-----------|
| Use `oneOf: [order, contract]` on all transaction message envelopes | `oneOf` enforces exactly one of `order` or `contract` per message — cleaner validation semantics while retaining backward compatibility. |
| Adopt Abhishek's `Contract` model (`commitments`, `consideration`, `performance`, `settlements`) | More abstract, domain-neutral, cross-industry applicable. |
| Retain `Order` as a first-class message field (not deprecated at the API level) | Breaking change otherwise. `Order` → `Contract` is a semantic rename; backward compat MUST be maintained. |
| Drop `context.try` two-phase pattern for `rate` and `support` | Adds complexity without sufficient gain. Flat single-phase pattern is simpler and more developer-friendly. |
| Retain `context.try` two-phase pattern for `cancel` and `update` | The two-phase pattern has clear semantic value here: allows BPP to return cancellation/update terms before the BAP commits. |
| `support` message uses `refId`/`refType` (Abhishek) not nested `order.id` (Ravi) | More abstract; works for contracts, resources, providers, agents, not just orders. |
| Remove `/beckn/{endPoint}` abstract path | Generator artefact. `beckn-proposed.yaml` is hand-maintained; `scripts/prune_beckn_yaml.py` is no longer needed. |
| All schemas get `$id` pointing to `schema.beckn.io` | Enables JSON Schema 2020-12 canonical resolution and aligns with `beckn.yaml`'s external-ref model. |
