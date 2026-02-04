# Beckn Protocol 2.1 — Core Transaction APIs Overview (Normative RFC Representation)

## Request for Comments — DRAFT

### About this Document

This document is a **normative overview** of the **server-to-server** Beckn Protocol transaction layer between a **BAP** (Beckn Application Platform) and a **BPP** (Beckn Protocol Provider). It describes:

* The **four lifecycle stages** and the endpoints in each stage:

  * **Discovery**: `discover`, `publish`
  * **Ordering**: `select`, `init`, `confirm`
  * **Fulfillment**: `status`, `update`, `track`, `cancel`
  * **Post-fulfillment**: `rating`, `support`
* The **payload object families** transported by each endpoint (via `message` schemas).
* Typical **BAP/BPP-facing product triggers** (what user-facing actions usually cause the servers to call these endpoints).
* The **ACK/NACK** pattern and the callback (`on_*`) pattern.

This document intentionally avoids deep schema commentary. Each endpoint and each payload schema is expected to have its own dedicated specification later.

---

# Context

## Protocol interaction model (normative)

1. Beckn is a **BAP ↔ BPP** protocol. All transactional interactions described here are between these two parties.
2. Beckn is **server-to-server**. Any “user action” referenced below is merely the frontend trigger that causes the **BAP server** or **BPP server** to initiate a call.
3. The protocol is **asynchronous by default**:

   * A “request” endpoint (e.g., `select`) is sent from one party to the other and returns an **ACK/NACK** immediately.
   * The “response” is delivered later via the corresponding **callback** endpoint (e.g., `on_select`), which also returns an **ACK/NACK** immediately.
4. Each request body is structurally:

   * `context`: protocol envelope (including `action`, and sometimes `try`)
   * `message`: the stage/action-specific payload object

## ACK/NACK (normative)

* All endpoints in this overview return an **ACK/NACK** response indicating **receipt + basic validation**, not business completion.
* Business results (catalog lists, quotes, confirmed orders, updated terms, etc.) arrive in the `message` payload of the callback (`on_*`) endpoints.

---

# Intended Outcome

Provide a crisp, implementer-oriented reference for the **foundational transactional communication layer** in Beckn Protocol 2.1, suitable as the entry-point RFC before domain bindings and detailed endpoint RFCs.

---

# Protocol Stages and Endpoint Catalogue

## Stage 1 — Discovery

Discovery consists of two actions:

* `discover` / `on_discover`: discover catalogs available across a network
* `catalog/publish` / `catalog/on_publish`: publish catalogs for indexing

### 1. `GET /beckn/discover` → `POST /beckn/on_discover`

**Direction**

* `discover`: **BAP → (Catalog Discovery Service and/or BPP)**
* `on_discover`: **BPP → BAP**

**Purpose (normative)**

* `discover` performs catalog discovery using **text search**, **JSONPath-based filtering (RFC 9535)**, or both, with optional schema adaptation by the implementation.
* `on_discover` returns catalog search results (potentially aggregating catalogs from multiple BPPs).

**Payload objects**

* `discover.message`: `DiscoverMessage`
* `on_discover.message`: `OnDiscoverMessage`

**Typical triggers**

* **BAP UX**: user searches/browses (“search for restaurants”, “find EV chargers near me”, “search jobs”, etc.).
* **BPP/Discovery Service**: processes filters, queries catalogs/indexes, then posts results to `on_discover`.

---

### 2. `POST /beckn/catalog/publish` → `POST /beckn/catalog/on_publish`

**Direction**

* `catalog/publish`: **BPP → Catalog Publishing Service**
* `catalog/on_publish`: **Catalog Publishing Service → BPP**

**Purpose (normative)**

* `catalog/publish` submits one or more catalogs to be indexed. Returns ACK if accepted for processing.
* `catalog/on_publish` delivers per-catalog processing outcomes asynchronously.

**Payload objects**

* `catalog/publish.message`: `CatalogPublishMessage`
* `catalog/on_publish.message`: `CatalogOnPublishMessage`

**Typical triggers**

* **BPP ops/system**: catalog updates, scheduled re-publish, inventory/price refresh pipelines.
* **Publishing service**: validates, indexes, reports results back.

---

## Stage 2 — Ordering

Ordering consists of:

* `select` (quote), `init` (final draft), `confirm` (order creation)

### 3. `POST /beckn/select` → `POST /beckn/on_select`

**Direction**

* `select`: **BAP → BPP**
* `on_select`: **BPP → BAP**

**Purpose (normative)**

* `select` asks for a **quote** based on chosen items/quantities/offers/coupons and optionally **anonymous bidding**, **without sharing consumer PII**.
* `on_select` returns a computed quote, may check inventory/serviceability, may return auction bid context, and may provide links to external forms if required before proceeding.

**Payload objects**

* `select.message`: `SelectMessage`
* `on_select.message`: `OnSelectMessage`

**Typical triggers**

* **BAP UX**: “view price”, “apply coupon”, “request quote”, “place anonymous bid”.
* **BPP logic**: pricing rules, offer validation, inventory/serviceability checks, auction logic.

---

### 4. `POST /beckn/init` → `POST /beckn/on_init`

**Direction**

* `init`: **BAP → BPP**
* `on_init`: **BPP → BAP**

**Purpose (normative)**

* `init` starts forming the **final order** by providing billing + fulfillment + source payment info required to compute final terms. (Also references to any required artifacts/inputs, as applicable.)
* `on_init` returns the final order draft including **terms of service** and potentially additional requirements (e.g., payment steps, attestations, forms).

**Payload objects**

* `init.message`: `InitMessage`
* `on_init.message`: `OnInitMessage`

**Typical triggers**

* **BAP UX**: “Proceed to checkout”, entering address, selecting delivery slot, choosing payment method.
* **BPP logic**: computes final charges/fees/taxes, validates fulfillment feasibility, generates ToS, creates payment intents/links if needed.

---

### 5. `POST /beckn/confirm` → `POST /beckn/on_confirm`

**Direction**

* `confirm`: **BAP → BPP**
* `on_confirm`: **BPP → BAP**

**Purpose (normative)**

* `confirm` indicates BAP acceptance/fulfillment of preconditions (e.g., payment proof/reference, attestations, submitted form references, authorizations).
* `on_confirm` returns the **confirmed order** with an Order ID after validating that all conditions (including payment, where required) are satisfied.

**Payload objects**

* `confirm.message`: `ConfirmMessage`
* `on_confirm.message`: `OnConfirmMessage`

**Typical triggers**

* **BAP UX**: “Place order”, “Pay now”, “Accept terms”, upload/submit required docs.
* **BPP logic**: final validation, order creation, payment reconciliation, allocation initialization.

---

## Stage 3 — Fulfillment

Fulfillment consists of:

* `status`, `update`, `track`, `cancel`

### 6. `POST /beckn/status` → `POST /beckn/on_status`

**Direction**

* `status`: **BAP → BPP**
* `on_status`: **BPP → BAP**

**Purpose (normative)**

* `status` requests the latest state of an order.
* `on_status` returns the latest state, including fulfillment status. The BPP may also call `on_status` proactively (push updates) even without an explicit `status` request.

**Payload objects**

* `status.message`: `StatusMessage`
* `on_status.message`: `OnStatusMessage`

**Typical triggers**

* **BAP UX**: order details page refresh, “where is my order?”, background polling.
* **BPP logic**: pushes state transitions (packed/shipped/arrived/completed), exception notifications.

---

### 7. `POST /beckn/track` → `POST /beckn/on_track`

**Direction**

* `track`: **BAP → BPP**
* `on_track`: **BPP → BAP**

**Purpose (normative)**

* `track` requests real-time tracking for an active order.
* `on_track` returns tracking handles (e.g., tracking URLs, tracker IDs, real-time stream endpoints).

**Payload objects**

* `track.message`: `TrackMessage`
* `on_track.message`: `OnTrackMessage`

**Typical triggers**

* **BAP UX**: user opens “Live tracking”.
* **BPP logic**: issues/refreshes tracking tokens/links, binds to logistics tracker providers.

---

### 8. `POST /beckn/update` → `POST /beckn/on_update`  *(two-mode via `context.try`)*

**Direction**

* `update`: **BAP → BPP**
* `on_update`: **BPP → BAP**

**Purpose (normative)**

* `update` requests modification of an active order and recalculation of terms (including payment).
* `on_update` returns the updated order with recomputed quote/payment terms.

**Two-mode behavior (`context.try`)**

* The spec models two branches: `context.try: true` vs `context.try: false`, enabling a **proposal/preview** vs **commit/confirm** style update flow.

**Payload objects**

* `update.message`: `UpdateInitMessage` (try=true) or `UpdateConfirmMessage` (try=false)
* `on_update.message`: `OnUpdateInitMessage` (try=true) or `OnUpdateConfirmMessage` (try=false)

**Typical triggers**

* **BAP UX**: change quantities, add/remove items, change address, reschedule slot, modify billing details.
* **BPP logic**: reallocation of fulfillment agent, substitution rules, repricing, payment adjustment links, validation against policies.

---

### 9. `POST /beckn/cancel` → `POST /beckn/on_cancel` *(two-mode via `context.try`; request description currently TODO in source)*

**Direction**

* `cancel`: **BAP → BPP**
* `on_cancel`: **BPP → BAP**

**Purpose (normative)**

* `cancel` requests cancellation of an order.
* `on_cancel` returns the cancelled order state, potentially reflecting refund/payment updates (via payment references).

**Two-mode behavior (`context.try`)**

* Two-branch pattern exists (`context.try: true/false`) consistent with a **pre-check** vs **finalize cancellation** approach.

**Payload objects**

* `cancel.message`: `CancelInitMessage` (try=true) or `CancelConfirmMessage` (try=false)
* `on_cancel.message`: `OnCancelInitMessage` (try=true) or `OnCancelConfirmMessage` (try=false)

**Typical triggers**

* **BAP UX**: “Cancel order” → show penalty/refund preview (try=true) → “Confirm cancellation” (try=false).
* **BPP logic**: cancellation policy evaluation, fee/refund computation, fulfillment reversal, payment adjustments.

---

## Stage 4 — Post-fulfillment

Post-fulfillment consists of:

* `rate`, `support`

### 10. `POST /beckn/rate` → `POST /beckn/on_rate` *(two-mode via `context.try`)*

**Direction**

* `rate`: **BAP → BPP**
* `on_rate`: **BPP → BAP**

**Purpose (normative)**

* `rate` submits a rating for any aspect of an order.
* `on_rate` acknowledges rating receipt and may optionally return an aggregate snapshot/receipt.

**Two-mode behavior (`context.try`)**

* Two-branch pattern exists (`context.try: true/false`) to support “preview/validate rating target” vs “commit rating” style flows where needed.

**Payload objects**

* `rate.message`: `RateInitMessage` (try=true) or `RateConfirmMessage` (try=false)
* `on_rate.message`: `OnRateInitMessage` (try=true) or `OnRateConfirmMessage` (try=false)

**Typical triggers**

* **BAP UX**: post-completion rating prompt, rate delivery agent/item/provider, submit feedback.
* **BPP logic**: validates rating applicability, stores rating, optionally returns receipt/updated aggregates.

---

### 11. `POST /beckn/support` → `POST /beckn/on_support` *(request is two-mode via `context.try`)*

**Direction**

* `support`: **BAP → BPP**
* `on_support`: **BPP → BAP**

**Purpose (normative)**

* `support` requests support details for an entity (order/item/provider/etc.).
* `on_support` returns support contact/details (`SupportInfo`).

**Two-mode behavior (`context.try`)**

* `support` supports `context.try: true/false` branching, allowing pre-check/validation vs confirmed support request flows where applicable.

**Payload objects**

* `support.message`: `OnSupportInitMessage` (try=true) or `OnSupportConfirmMessage` (try=false)
* `on_support.message.support`: `SupportInfo`

**Typical triggers**

* **BAP UX**: “Need help?”, “Contact support”, dispute/issue flows.
* **BPP logic**: routes to correct helpdesk channel, returns contact points, ticket URLs, escalation policy pointers.

---

# Cross-cutting Normative Notes

## Endpoint naming and lifecycle coupling

* Each primary action has a corresponding callback:

  * `discover ↔ on_discover`
  * `select ↔ on_select`
  * `init ↔ on_init`
  * `confirm ↔ on_confirm`
  * `status ↔ on_status`
  * `update ↔ on_update`
  * `track ↔ on_track`
  * `cancel ↔ on_cancel`
  * `rate ↔ on_rate`
  * `support ↔ on_support`
  * `catalog/publish ↔ catalog/on_publish`

## The `context.action` field

* Every endpoint constrains `context.action` to a constant matching the endpoint (e.g., `select`, `on_select`, `catalog/publish`, etc.). This is the primary protocol-level discriminator.

## The `context.try` field (two-mode operations)

* Some operations are explicitly modeled with a `try` boolean to enable:

  * quote/preview/check feasibility (`try=true`)
  * confirm/commit the change (`try=false`)
* In this overview, `update`, `cancel`, `rate`, and `support` are modeled this way.

---

# Conclusion

This RFC captures the **minimal normative overview** of Beckn Protocol 2.1’s transactional communication layer: four stages, the endpoint pairs per stage, the message object families transported, and typical system triggers. It should be used as the “map of the terrain” before diving into the detailed endpoint RFCs and domain-specific bindings.

If you want the next step to be equally formal, I suggest we proceed stage-by-stage (Discovery → Ordering → Fulfillment → Post-fulfillment), and for each endpoint produce:

* a strict normative definition,
* a state machine slice,
* and message-level conformance rules (including `try` semantics where applicable).
