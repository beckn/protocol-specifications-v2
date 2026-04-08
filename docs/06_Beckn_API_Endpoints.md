# Beckn API Endpoint Guide (v2.0.0)

Source of truth: `api/v2.0.0/beckn.yaml`

This document explains all API endpoints defined in the Beckn v2.0.0 OpenAPI contract and how they are used across discovery, contracting, fulfillment, post-fulfillment, catalog services, and master resource search.

## 1) API Fundamentals

- **OpenAPI version:** `3.1.1`
- **Spec version:** `2.0.0`
- **Base server:** `https://{subscriberUrl}`
- **Authentication:** every endpoint requires `Authorization` header using Beckn HTTP Signature (`#/components/schemas/Signature`)
- **ACK model:** success responses use Ack/Nack envelopes, with counter-signature in body (`#/components/schemas/CounterSignature`)

### 1.1 Common request envelope

Most POST operations use:

```json
{
  "context": {
    "version": "2.0.0",
    "action": "<endpoint-specific-action>",
    "bapId": "...",
    "bapUri": "...",
    "bppId": "...",
    "bppUri": "...",
    "transactionId": "...",
    "messageId": "...",
    "timestamp": "..."
  },
  "message": {
    "...": "endpoint-specific payload"
  }
}
```

### 1.2 Common response envelope semantics

- `Ack`: `status` (`ACK|NACK`) + mandatory `signature` (counter-signature)
- `AckNoCallback` (`409`): request accepted but no callback follows, includes `error`
- `NackBadRequest` (`400`): invalid request payload/structure
- `NackUnauthorized` (`401`): signature/auth failure
- `ServerError` (`500`): internal processing failure

## 2) Transaction Lifecycle Mapping

Core lifecycle defined in the API description:

```text
discover -> on_discover
select -> on_select -> init -> on_init -> confirm -> on_confirm
-> [status / on_status]* -> [update / on_update]* -> [cancel / on_cancel]?
-> [track / on_track]* -> rate / on_rate -> support / on_support
```

## 3) Endpoint Matrix (All Paths)

| Method | Path | operationId | Tag | `context.action` | Message schema | Responses |
|---|---|---|---|---|---|---|
| POST | `/discover` | `discover` | Discovery | `discover` | `DiscoverAction` | `200,400,401,409,500` |
| POST | `/on_discover` | `onDiscover` | Discovery | `on_discover` | `OnDiscoverAction` | `200,400,401,500` |
| POST | `/select` | `select` | Transaction | `select` | `SelectAction` | `200,400,401,409,500` |
| POST | `/on_select` | `onSelect` | Transaction | `on_select` | `OnSelectAction` | `200,400,401,500` |
| POST | `/init` | `init` | Transaction | `init` | `InitAction` | `200,400,401,409,500` |
| POST | `/on_init` | `onInit` | Transaction | `on_init` | `OnInitAction` | `200,400,401,500` |
| POST | `/confirm` | `confirm` | Transaction | `confirm` | `ConfirmAction` | `200,400,401,409,500` |
| POST | `/on_confirm` | `onConfirm` | Transaction | `on_confirm` | `OnConfirmAction` | `200,400,401,500` |
| POST | `/status` | `status` | Fulfillment | `status` | `StatusAction` | `200,400,401,409,500` |
| POST | `/on_status` | `onStatus` | Fulfillment | `on_status` | `OnStatusAction` | `200,400,401,500` |
| POST | `/track` | `track` | Fulfillment | `track` | `TrackAction` | `200,400,401,409,500` |
| POST | `/on_track` | `onTrack` | Fulfillment | `on_track` | `OnTrackAction` | `200,400,401,500` |
| POST | `/update` | `update` | Fulfillment | `update` | `UpdateAction` | `200,400,401,409,500` |
| POST | `/on_update` | `onUpdate` | Fulfillment | `on_update` | `OnUpdateAction` | `200,400,401,500` |
| POST | `/cancel` | `cancel` | Fulfillment | `cancel` | `CancelAction` | `200,400,401,409,500` |
| POST | `/on_cancel` | `onCancel` | Fulfillment | `on_cancel` | `OnCancelAction` | `200,400,401,500` |
| POST | `/rate` | `rate` | Post-Fulfillment | `rate` | `RateAction` | `200,400,401,409,500` |
| POST | `/on_rate` | `onRate` | Post-Fulfillment | `on_rate` | `OnRateAction` | `200,400,401,500` |
| POST | `/support` | `support` | Post-Fulfillment | `support` | `SupportAction` | `200,400,401,409,500` |
| POST | `/on_support` | `onSupport` | Post-Fulfillment | `on_support` | `OnSupportAction` | `200,400,401,500` |
| POST | `/catalog/publish` | `catalogPublish` | Catalog Publishing | `catalog/publish` or `catalog_publish` | `CatalogPublishAction` | `200,400,401,409,500` |
| POST | `/catalog/on_publish` | `catalogOnPublish` | Catalog Publishing | `on_catalog_publish` or `catalog/on_publish` | `CatalogOnPublishAction` | `200,400,401,500` |
| POST | `/catalog/subscription` | `catalogSubscribe` | Subscription | `catalog/subscription` | `CatalogSubscribeAction` | `200,400,401,500` |
| GET | `/catalog/subscriptions` | `catalogSubscribeList` | Subscription | - | - | `200,400,500` |
| GET | `/catalog/subscription/{subscriptionId}` | `catalogSubscribeGet` | Subscription | - | - | `200,400,401,404,500` |
| DELETE | `/catalog/subscription/{subscriptionId}` | `catalogSubscribeDelete` | Subscription | - | - | `200,400,401,404,500` |
| POST | `/catalog/pull` | `catalogPull` | Catalog Pull | `catalog/pull` | `CatalogPullAction` | `200,400,401,500` |
| GET | `/catalog/pull/result/{requestId}/{filename}` | `getPullResult` | Catalog Pull | - | - | `200,400,401,404` |
| POST | `/catalog/master/search` | `masterSearch` | Master Resource Search | `catalog/master_search` | `MasterSearchAction` | `200,400,401,500` |
| GET | `/catalog/master/schemaTypes` | `listMasterSchemaTypes` | Master Resource Search | - | - | `200,401,500` |
| GET | `/catalog/master/{masterItemId}` | `getMasterItem` | Master Resource Search | - | - | `200,400,404,500` |

## 4) Detailed Endpoint Walkthrough

### 4.1 Discovery

- **`POST /discover`**: BAP asks DS/BPP for matching catalogs; supports text, JSONPath filtering (RFC 9535), geo constraints, and media search. Returns immediate ACK; result comes in callback.
- **`POST /on_discover`**: callback carrying `OnDiscoverAction` (`message.catalogs[]`) from CDS/BPP to BAP.

### 4.2 Transaction (Contracting)

- **`POST /select`**: BAP selects resources/offers and requests quote (`SelectAction`).
- **`POST /on_select`**: BPP returns priced/updated contract (`OnSelectAction`).
- **`POST /init`**: BAP sends billing, fulfillment/performance, and payment intent (`InitAction`).
- **`POST /on_init`**: BPP returns final draft contract with payment terms (`OnInitAction`).
- **`POST /confirm`**: BAP commits accepted terms and confirms contract (`ConfirmAction`).
- **`POST /on_confirm`**: BPP returns confirmed contract (`OnConfirmAction`).

### 4.3 Fulfillment

- **`POST /status`**: BAP asks for current contract state (`StatusAction`).
- **`POST /on_status`**: BPP returns latest state (`OnStatusAction`); can push proactively after status stream is initiated.
- **`POST /track`**: BAP requests real-time tracking handle (`TrackAction`) for live progress/position updates
- **`POST /on_track`**: BPP returns tracking URL/handle and status (`OnTrackAction`).
- **`POST /update`**: BAP requests mutation on active contract (`UpdateAction`)
- **`POST /on_update`**: BPP returns recalculated terms or committed updated contract (`OnUpdateAction`).
- **`POST /cancel`**: BAP requests cancellation (`CancelAction`)
- **`POST /on_cancel`**: BPP returns cancellation policy preview or confirmed cancellation (`OnCancelAction`).

### 4.4 Post-Fulfillment

- **`POST /rate`**: BAP sends rating inputs (`RateAction`), supports `context.try` preview mode.
- **`POST /on_rate`**: BPP confirms rating and may return aggregate/details (`OnRateAction`).
- **`POST /support`**: BAP requests support channels or opens support ticket (`SupportAction`).
- **`POST /on_support`**: BPP returns support details/ticket outcomes (`OnSupportAction`).

### 4.5 Catalog Publishing

- **`POST /catalog/publish`**: BPP submits catalogs for indexing (`CatalogPublishAction`). Action supports both `catalog/publish` and `catalog_publish`.
- **`POST /catalog/on_publish`**: CDS returns per-catalog processing results (`CatalogOnPublishAction`). Action supports both `on_catalog_publish` and `catalog/on_publish`.

### 4.6 Subscription

- **`POST /catalog/subscription`**: creates subscription (`CatalogSubscribeAction`). At least one of `networkIds` or `schemaTypes` must be non-empty; empty `schemaTypes` behaves as wildcard `"*"`.
- **`GET /catalog/subscriptions`**: list subscriptions for subscriber.
- **`GET /catalog/subscription/{subscriptionId}`**: fetch one subscription record.
- **`DELETE /catalog/subscription/{subscriptionId}`**: soft delete/deactivate subscription (`status=DELETED`).

### 4.7 Catalog Pull

- **`POST /catalog/pull`**: asynchronous pull request; returns immediate ACK with `requestId`.
  - `mode=FULL`: latest version of each matching catalog.
  - `mode=INCREMENTAL`: all versions in `fromDate`..`toDate`.
  - completion is callback to `{context.bapUri}/on_catalog_pull` with pull result metadata.
- **`GET /catalog/pull/result/{requestId}/{filename}`**: downloads large result payload file.
  - path validation: UUID regex on `requestId` and allowlist for `filename` (`catalogs.json`).

### 4.8 Master Resource Search

- **`POST /catalog/master/search`**: query indexed master items (`MasterSearchAction`), response action is `on_catalog_master_search`.
- **`GET /catalog/master/schemaTypes`**: list schema types available in master index.
- **`GET /catalog/master/{masterItemId}`**: fetch one master item (path param pattern: `^[a-zA-Z0-9_\-:.]+$`).

## 5) Payload Schemas Used by Endpoint Groups

- Discovery: `DiscoverAction`, `OnDiscoverAction`
- Transaction: `SelectAction`, `OnSelectAction`, `InitAction`, `OnInitAction`, `ConfirmAction`, `OnConfirmAction`
- Fulfillment: `StatusAction`, `OnStatusAction`, `TrackAction`, `OnTrackAction`, `UpdateAction`, `OnUpdateAction`, `CancelAction`, `OnCancelAction`
- Post-Fulfillment: `RateAction`, `OnRateAction`, `SupportAction`, `OnSupportAction`
- Catalog services: `CatalogPublishAction`, `CatalogOnPublishAction`, `CatalogSubscribeAction`, `CatalogPullAction`, `CatalogSubscription`
- Master search: `MasterSearchAction`

## 6) Implementation Notes from the Spec

- The `Context` schema is broad by design; endpoint-level constraints are applied inline per operation.
- `context.version` is fixed to `2.0.0` in the schema.
- `context.try` is explicitly used for preview/commit behavior in `update`, `cancel`, `rate`, and `support` flows.
- Request signatures and response counter-signatures are normative for transport trust.
