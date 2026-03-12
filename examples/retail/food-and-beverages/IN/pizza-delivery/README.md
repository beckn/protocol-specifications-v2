# Beckn Protocol v2.0 — Retail Examples

This directory contains a complete set of Beckn Protocol v2.0 message examples for the **retail (food and beverage)** domain, tracing a single end-to-end transaction: **Arjun Sharma orders 2× Margherita Pizza from Pizzeria Roma via a Beckn-enabled pizza app**.

All examples are derived directly from the schemas published at [`https://schema.beckn.io/`](https://schema.beckn.io/) and conform to the OpenAPI specification at [`protocol-specifications-v2/api/v2.0.0/beckn.yaml`](../../protocol-specifications-v2/api/v2.0.0/beckn.yaml).

---

## Scenario

| Field | Value |
|---|---|
| **Consumer** | Arjun Sharma (`arjun.sharma@pizza-app.example.com`) |
| **Provider** | Pizzeria Roma — MG Road, Bangalore |
| **BAP** | `pizza-app.example.com` |
| **BPP** | `pizzeria-roma.example.com` |
| **Transaction ID** | `txn-0001-2026-retail-pizza` |
| **Items** | 2× Margherita Pizza @ INR 299 each |
| **Delivery Fee** | INR 40 |
| **Total** | INR 638 |
| **Fulfillment** | Home delivery, Apt 204, Sunrise Heights, 12 MG Road, Bangalore |
| **Date** | 2026-03-10 |

---

## Flow Diagram

```
BAP                                   BPP
 │                                     │
 │──── POST /beckn/discover ──────────▶│  discover.json
 │◀─── POST /beckn/on_discover ────────│  on_discover.json
 │                                     │
 │──── POST /beckn/select ────────────▶│  select.json
 │◀─── POST /beckn/on_select ──────────│  on_select.json
 │                                     │
 │──── POST /beckn/init ──────────────▶│  init.json
 │◀─── POST /beckn/on_init ────────────│  on_init.json
 │                                     │
 │──── POST /beckn/confirm ───────────▶│  confirm.json
 │◀─── POST /beckn/on_confirm ─────────│  on_confirm.json
 │                                     │
 │──── POST /beckn/status ────────────▶│  status.json
 │◀─── POST /beckn/on_status ──────────│  on_status.json
 │                                     │
 │──── POST /beckn/cancel ────────────▶│  cancel.json
 │◀─── POST /beckn/on_cancel ──────────│  on_cancel.json
 │                                     │
 │──── POST /beckn/support ───────────▶│  support.json
 │◀─── POST /beckn/on_support ─────────│  on_support.json
```

---

## Files

| File | Beckn Endpoint | Schema | Description |
|---|---|---|---|
| [`discover.json`](./discover.json) | `beckn/discover` | [`DiscoverAction/v2.0`](https://schema.beckn.io/DiscoverAction/v2.0) | BAP discovers pizzas near MG Road using `message.intent.textSearch` |
| [`on_discover.json`](./on_discover.json) | `beckn/on_discover` | [`OnDiscoverAction/v2.0`](https://schema.beckn.io/OnDiscoverAction/v2.0) | BPP responds with `message.catalogs[]` containing items from Pizzeria Roma |
| [`select.json`](./select.json) | `beckn/select` | [`SelectAction/v2.0`](https://schema.beckn.io/SelectAction/v2.0) | BAP selects 2× Margherita, sets delivery address in `message.contract` |
| [`on_select.json`](./on_select.json) | `beckn/on_select` | [`OnSelectAction/v2.0`](https://schema.beckn.io/OnSelectAction/v2.0) | BPP returns updated contract with `contractValue` breakdown and delivery ETAs |
| [`init.json`](./init.json) | `beckn/init` | [`InitAction/v2.0`](https://schema.beckn.io/InitAction/v2.0) | BAP submits consumer details (name, phone, email) and delivery preferences |
| [`on_init.json`](./on_init.json) | `beckn/on_init` | [`OnInitAction/v2.0`](https://schema.beckn.io/OnInitAction/v2.0) | BPP confirms payment terms and SLA; contract status: `DRAFT` |
| [`confirm.json`](./confirm.json) | `beckn/confirm` | [`ConfirmAction/v2.0`](https://schema.beckn.io/ConfirmAction/v2.0) | BAP confirms order with payment proof in `entitlements[]` |
| [`on_confirm.json`](./on_confirm.json) | `beckn/on_confirm` | [`OnConfirmAction/v2.0`](https://schema.beckn.io/OnConfirmAction/v2.0) | BPP assigns `id` + `displayId` to the contract; status: `ACTIVE` |
| [`status.json`](./status.json) | `beckn/status` | [`StatusAction/v2.0`](https://schema.beckn.io/StatusAction/v2.0) | BAP polls order status using only `message.order.id` |
| [`on_status.json`](./on_status.json) | `beckn/on_status` | [`OnStatusAction/v2.0`](https://schema.beckn.io/OnStatusAction/v2.0) | BPP returns full contract with fulfillment `state: Out for Delivery` |
| [`cancel.json`](./cancel.json) | `beckn/cancel` | [`CancelAction/v2.0`](https://schema.beckn.io/CancelAction/v2.0) | BAP cancels the order; reason encoded in `entitlements[]` |
| [`on_cancel.json`](./on_cancel.json) | `beckn/on_cancel` | [`OnCancelAction/v2.0`](https://schema.beckn.io/OnCancelAction/v2.0) | BPP confirms cancellation; contract status: `CANCELLED`; refund in `entitlements[]` |
| [`support.json`](./support.json) | `beckn/support` | [`SupportAction/v2.0`](https://schema.beckn.io/SupportAction/v2.0) | BAP requests support for order using `message.supportRequest` (SupportRequest/v2.0) |
| [`on_support.json`](./on_support.json) | `beckn/on_support` | [`OnSupportAction/v2.0`](https://schema.beckn.io/OnSupportAction/v2.0) | BPP returns support channels, phone, email, and callback status (SupportInfo/v2.0) |

---

## Key v2.0 Schema Patterns

### 1. Intent uses `textSearch` (not `item`/`fulfillment`)

```json
// search.json — message.intent
{
  "textSearch": "Margherita Pizza near MG Road Bangalore"
}
```

The v2.0 [`Intent/v2.0`](https://schema.beckn.io/Intent/v2.0) schema supports `textSearch`, `filters` (JSONPath), and `spatial` constraints — not the older `item`/`fulfillment`/`payment` properties.

### 2. Catalog is flat (no nested Providers)

```json
// on_search.json — message.catalogs[0]
{
  "@context": "https://schema.beckn.io/",
  "@type": "beckn:Catalog",
  "id": "catalog-pizzeria-roma-blr-001",
  "providerId": "provider-roma-blr-mgroad-001",
  "items": [ ... ]
}
```

[`Catalog/v2.0`](https://schema.beckn.io/Catalog/v2.0) holds items directly. Each [`Item/v2.0`](https://schema.beckn.io/Item/v2.0) carries its own `provider` reference (not nested Provider → items).

### 3. Location uses GeoJSON (not `gps` string)

```json
// select.json — fulfillment stage endpoint
{
  "@type": "Location",
  "geo": {
    "type": "Point",
    "coordinates": [77.5946, 12.9716]
  },
  "address": {
    "streetAddress": "Apt 204, Sunrise Heights, 12 MG Road",
    "addressLocality": "Bangalore",
    "addressRegion": "Karnataka",
    "postalCode": "560001",
    "addressCountry": "IN"
  }
}
```

GeoJSON coordinate order is **[longitude, latitude]** (RFC 7946). [`Address/v2.0`](https://schema.beckn.io/Address/v2.0) uses schema.org `PostalAddress` field names.

### 4. Contract requires `@type` + `participants[]` + `items[]`

```json
// select.json — message.contract (minimum required)
{
  "@type": "beckn:Contract",
  "participants": [ { "@context": "...", "@type": "beckn:Participant", "id": "...", "role": "consumer" } ],
  "items": [ { "itemId": "item-margherita-regular" } ]
}
```

[`Contract/v2.0`](https://schema.beckn.io/Contract/v2.0) requires `@type`, `participants[]`, and `items[]`. The `items` are [`ContractItem/v2.0`](https://schema.beckn.io/ContractItem/v2.0) objects (not raw `Item` objects).

### 5. Fulfillment requires `mode`

```json
// select.json — contract.fulfillments[0]
{
  "@context": "https://schema.beckn.io/",
  "@type": "Fulfillment",
  "mode": {
    "@context": "https://schema.beckn.io/",
    "@type": "beckn:FulfillmentMode",
    "descriptor": { "@type": "beckn:Descriptor", "name": "Home Delivery" },
    "modeAttributes": {
      "@context": "https://schema.beckn.io/retail/",
      "@type": "retail:RetailCoreFulfillmentAttributes",
      "supportedFulfillmentTypes": ["DELIVERY"]
    }
  }
}
```

[`Fulfillment/v2.0`](https://schema.beckn.io/Fulfillment/v2.0) requires `mode` ([`FulfillmentMode/v2.0`](https://schema.beckn.io/FulfillmentMode/v2.0)). Domain-specific fulfillment attributes go into `mode.modeAttributes` using `RetailCoreFulfillmentAttributes`.

### 6. Status query uses only `message.order.id`

```json
// status.json — message
{
  "order": {
    "id": "f7a8b9c0-d1e2-4f3a-b5c6-789012345678"
  }
}
```

[`StatusAction/v2.0`](https://schema.beckn.io/StatusAction/v2.0) requires only the contract UUID — no extra fields.

### 7. SupportRequest uses `@type: Support`

```json
// support.json — message.supportRequest
{
  "@context": "https://schema.beckn.io/",
  "@type": "Support",
  "orderId": "f7a8b9c0-d1e2-4f3a-b5c6-789012345678",
  "callbackPhone": "+919876543210"
}
```

---

## Schema References

| Schema | IRI |
|---|---|
| DiscoverAction | `https://schema.beckn.io/DiscoverAction/v2.0` |
| OnDiscoverAction | `https://schema.beckn.io/OnDiscoverAction/v2.0` |
| SelectAction | `https://schema.beckn.io/SelectAction/v2.0` |
| OnSelectAction | `https://schema.beckn.io/OnSelectAction/v2.0` |
| InitAction | `https://schema.beckn.io/InitAction/v2.0` |
| OnInitAction | `https://schema.beckn.io/OnInitAction/v2.0` |
| ConfirmAction | `https://schema.beckn.io/ConfirmAction/v2.0` |
| OnConfirmAction | `https://schema.beckn.io/OnConfirmAction/v2.0` |
| StatusAction | `https://schema.beckn.io/StatusAction/v2.0` |
| OnStatusAction | `https://schema.beckn.io/OnStatusAction/v2.0` |
| CancelAction | `https://schema.beckn.io/CancelAction/v2.0` |
| OnCancelAction | `https://schema.beckn.io/OnCancelAction/v2.0` |
| SupportAction | `https://schema.beckn.io/SupportAction/v2.0` |
| OnSupportAction | `https://schema.beckn.io/OnSupportAction/v2.0` |
| Context | `https://schema.beckn.io/Context/v2.0` |
| Intent | `https://schema.beckn.io/Intent/v2.0` |
| Catalog | `https://schema.beckn.io/Catalog/v2.0` |
| Item | `https://schema.beckn.io/Item/v2.0` |
| Contract | `https://schema.beckn.io/Contract/v2.0` |
| ContractItem | `https://schema.beckn.io/ContractItem/v2.0` |
| Participant | `https://schema.beckn.io/Participant/v2.0` |
| Fulfillment | `https://schema.beckn.io/Fulfillment/v2.0` |
| FulfillmentMode | `https://schema.beckn.io/FulfillmentMode/v2.0` |
| FulfillmentStage | `https://schema.beckn.io/FulfillmentStage/v2.0` |
| FulfillmentStageEndpoint | `https://schema.beckn.io/FulfillmentStageEndpoint/v2.0` |
| Location | `https://schema.beckn.io/Location/v2.0` |
| Address | `https://schema.beckn.io/Address/v2.0` |
| PriceSpecification | `https://schema.beckn.io/PriceSpecification/v2.0` |
| State | `https://schema.beckn.io/State/v2.0` |
| SupportRequest | `https://schema.beckn.io/SupportRequest/v2.0` |
| SupportInfo | `https://schema.beckn.io/SupportInfo/v2.0` |
