# RFC-026: Catalog APIs

**Status:** Draft
**Author(s):** Beckn Protocol contributors
**Created:** 2026-04-22
**Updated:** 2026-04-22
**Conformance impact:** Major (introduces catalog lifecycle management APIs for Beckn v2 networks)
**Security/privacy implications:** Catalog data is published and distributed across Network Participants. Authentication via Beckn HTTP Signature is required on all endpoints. Subscription callbacks must be secured to prevent unauthorized catalog injection.
**Replaces / Relates to:** Supersedes [15_Catalog_Publishing_Service.md](./15_Catalog_Publishing_Service.md) and [16_Catalog_Discovery_Service.md](./16_Catalog_Discovery_Service.md).

---

## Abstract

This RFC defines the normative specification for all Catalog APIs in Beckn Protocol v2. It covers the full catalog lifecycle: publishing catalogs for network indexing, pushing catalogs to edge discovery services, subscribing to catalog update streams, pulling catalogs on demand, and searching master resource definitions. All APIs follow the standard Beckn asynchronous request-callback pattern and use Network Participant terminology throughout.

---

## 1. Context

In Beckn v2 networks, catalog data must flow efficiently from providers to discovery services. Network Participants need standardized APIs to publish, distribute, subscribe to, and query catalog data across networks. This RFC formalizes those APIs to ensure consistent interoperability across all network implementations.

---

## 2. Problem

Without a unified, normative specification for catalog lifecycle management:

- Network Participants cannot interoperably exchange catalog data.
- Edge discovery services have no standard interface for receiving catalog updates.
- Subscribers have no standard mechanism to receive incremental catalog changes.
- Master resource definitions cannot be consistently queried across networks.

---

## 3. Motivation

Standardizing catalog APIs enables:

- Consistent catalog distribution across heterogeneous network implementations.
- Decoupled catalog synchronization between providers and discovery services.
- Efficient incremental updates via subscriptions and pull modes.
- Reusable master resource definitions shared across Network Participants.

---

## 4. Design Principles

- **Interoperability-first:** All catalog APIs use the standard Beckn context and message envelope, ensuring any conformant Network Participant can exchange catalog data.
- **Abstraction over specificity:** APIs are domain-neutral and support any schema type, not tied to any specific vertical or catalog structure.
- **Optimal ignorance:** Each API exposes only the information necessary for its function. Publishing does not require knowledge of downstream subscribers.
- **Security by design:** All endpoints require Beckn HTTP Signature authentication. Only the Network Participant that created a subscription can deactivate it.
- **Reusability before novelty:** Master resource definitions enable resource reuse across catalogs, avoiding duplication of canonical data.

---

## 5. Specification (Normative)

### 5.1 Catalog Publish

#### `POST /catalog/publish`

A Network Participant submits one or more catalogs for indexing. The catalog system returns an immediate `ACK` and processes catalogs asynchronously, delivering per-catalog results via `/catalog/on_publish`.

**Requirements:**

- The Network Participant MUST include a valid Beckn HTTP Signature on every publish request.
- The catalog system MUST return an `ACK` immediately on receipt.
- The catalog system MUST validate catalog payloads against the declared schema type.
- The catalog system MUST deliver per-catalog processing results to `/catalog/on_publish` asynchronously.

#### `POST /catalog/on_publish`

Callback endpoint implemented by the Network Participant. The catalog system delivers per-catalog indexing results here after processing is complete.

**Requirements:**

- The Network Participant MUST implement `POST /catalog/on_publish` to receive processing results.
- The Network Participant MUST respond with `ACK` on receipt of the callback.

---

### 5.2 Catalog Push

#### `POST /catalog/push`

Endpoint implemented by the edge discovery service owned by a Network Participant. The catalog system invokes this endpoint to push and sync catalogs to the discovery service, keeping it up to date with the subscribed network catalogs.

**Requirements:**

- The edge discovery service MUST implement `POST /catalog/push`.
- The catalog system MUST authenticate via Beckn HTTP Signature on every push request.
- The edge discovery service MUST return an `ACK` immediately on receipt.
- The edge discovery service MUST apply received catalogs to its local index.

---

### 5.3 Catalog Subscription

#### `POST /catalog/subscription`

A Network Participant creates a subscription to receive catalog updates for specified networks and/or schema types.

**Requirements:**

- At least one of `networkIds` or `schemaTypes` MUST be provided.
- The catalog system MUST return an existing active subscription if an identical scope subscription already exists (idempotent).
- The catalog system MUST generate and return a unique `subscriptionId` UUID for each new subscription.

#### `DELETE /catalog/subscription`

Deactivates an active subscription. Only the Network Participant that created the subscription can deactivate it.

**Requirements:**

- The `subscriptionId` MUST be provided in the request body.
- The catalog system MUST verify that the requesting Network Participant is the creator of the subscription before deactivating it.
- Subscription status after deactivation MUST be `INACTIVE`.

#### `GET /catalog/subscriptions`

Returns all active subscriptions for the calling Network Participant.

**Requirements:**

- The catalog system MUST scope results to the calling Network Participant's identity.
- The caller MAY filter to a single subscription using the `?id=<uuid>` query parameter.

---

### 5.4 Catalog Pull

#### `POST /catalog/pull`

A Network Participant requests catalogs matching specified filters. Returns an immediate `ACK`; results are delivered asynchronously via `/catalog/on_pull`.

Two modes are supported:

- **FULL** — returns the latest version of each matching catalog.
- **INCREMENTAL** — returns all catalog versions indexed between `fromDate` and `toDate`, useful for syncing changes since the last pull.

**Requirements:**

- At least one of `catalogIds`, `networkIds`, or `schemaTypes` MUST be provided in `filters`.
- The `context.transactionId` MUST be provided and MUST persist through to the `on_pull` callback.
- The catalog system MUST return an `ACK` immediately on receipt.
- The catalog system MUST deliver results to `/catalog/on_pull` asynchronously.

#### `POST /catalog/on_pull`

Callback endpoint hosted by the receiving Network Participant. After the Network Participant submits a `/catalog/pull` request, the results are delivered here asynchronously.

**Requirements:**

- The Network Participant MUST implement `POST /catalog/on_pull` to receive pull results.
- The callback MUST carry terminal status only: `COMPLETED` or `FAILED`.
- The callback is delivered with at-least-once semantics; the receiving Network Participant MUST deduplicate on `context.transactionId`.
- On `COMPLETED` status, exactly one of `catalogs` (inline) or `objectUrl` (pre-signed download link) MUST be present.
- On `FAILED` status, the `error` field MUST carry the failure reason.
- The Network Participant MUST respond with `ACK` on receipt of the callback.

---

### 5.5 Master Resource Search

#### `POST /catalog/master/search`

Search for canonical master resource definitions across networks. Filter by network and schema type; results are paginated and grouped by catalog.

#### `GET /catalog/master/schemaTypes`

Returns the distinct schema type URIs available across all master resources.

#### `GET /catalog/master/{masterItemId}`

Returns a single master resource by its identifier, wrapped in its catalog envelope with full provider and descriptor metadata.

**Requirements:**

- The catalog system MUST support filtering by `networkIds` and/or `schemaTypes`.
- Omitting a filter dimension MUST match all values for that dimension.
- Master resource search results MUST be paginated.
- The catalog system MUST return the full catalog envelope (including provider and descriptor metadata) for individual master resource lookups.

---

## 6. Examples

### Example 1 — Publish a catalog

```json
{
  "context": {
    "version": "2.0.0",
    "action": "catalog/publish",
    "messageId": "550e8400-e29b-41d4-a716-446655440000",
    "transactionId": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-04-22T10:00:00.000Z",
    "bppId": "np.example.com",
    "bppUri": "https://np.example.com",
    "networkId": "retail-network"
  },
  "message": {
    "catalogs": [
      {
        "id": "CAT-001",
        "descriptor": { "name": "Example Catalog" },
        "provider": {
          "id": "provider-001",
          "descriptor": { "name": "Example Provider" }
        },
        "resources": [
          {
            "id": "ITEM-001",
            "descriptor": { "name": "Example Item" },
            "resourceAttributes": {
              "@context": "https://schema.beckn.org/retail/schema/1.1.0/context.jsonld",
              "@type": "RetailItem"
            }
          }
        ]
      }
    ]
  }
}
```

### Example 2 — Subscribe to catalog updates

```json
{
  "context": {
    "version": "2.0.0",
    "action": "catalog/subscription",
    "messageId": "550e8400-e29b-41d4-a716-446655440000",
    "transactionId": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-04-22T10:00:00.000Z",
    "bapId": "np.example.com",
    "bapUri": "https://np.example.com"
  },
  "message": {
    "subscription": {
      "networkIds": ["retail"],
      "schemaTypes": [
        "https://schema.beckn.org/retail/schema/1.1.0/item.json#ItemType"
      ]
    }
  }
}
```

### Example 3 — Pull catalogs (INCREMENTAL mode)

```json
{
  "context": {
    "version": "2.0.0",
    "action": "catalog/pull",
    "messageId": "660e8400-e29b-41d4-a716-446655440002",
    "transactionId": "660e8400-e29b-41d4-a716-446655440003",
    "timestamp": "2026-04-22T10:00:00.000Z",
    "bapId": "np.example.com",
    "bapUri": "https://np.example.com"
  },
  "message": {
    "mode": "INCREMENTAL",
    "filters": {
      "networkIds": ["retail"]
    },
    "fromDate": "2026-04-01T00:00:00.000Z",
    "toDate": "2026-04-22T00:00:00.000Z"
  }
}
```

### Example 4 — on_pull callback (success, inline)

```json
{
  "context": {
    "version": "2.0.0",
    "action": "catalog/on_pull",
    "transactionId": "660e8400-e29b-41d4-a716-446655440003",
    "timestamp": "2026-04-22T10:00:05.000Z"
  },
  "message": {
    "status": "COMPLETED",
    "catalogs": [
      {
        "id": "CAT-001",
        "descriptor": { "name": "Example Catalog" }
      }
    ]
  }
}
```

### Example 5 — Search master resources

```json
{
  "context": {
    "version": "2.0.0",
    "action": "catalog/master_search",
    "messageId": "770e8400-e29b-41d4-a716-446655440004",
    "transactionId": "770e8400-e29b-41d4-a716-446655440005",
    "timestamp": "2026-04-22T10:00:00.000Z"
  },
  "message": {
    "networkIds": ["retail"],
    "schemaTypes": [
      "https://schema.beckn.org/retail/schema/1.1.0/item.json#ItemType"
    ]
  }
}
```

---

## 7. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-026-01 | Network Participants MUST authenticate all catalog API requests via Beckn HTTP Signature | MUST |
| CON-026-02 | The catalog system MUST return an `ACK` immediately on receipt of `/catalog/publish` | MUST |
| CON-026-03 | The catalog system MUST deliver per-catalog results to `/catalog/on_publish` asynchronously | MUST |
| CON-026-04 | Edge discovery services MUST implement `POST /catalog/push` | MUST |
| CON-026-05 | At least one of `networkIds` or `schemaTypes` MUST be provided when creating a subscription | MUST |
| CON-026-06 | Subscription status MUST be either `ACTIVE` or `INACTIVE` | MUST |
| CON-026-07 | Only the Network Participant that created a subscription MUST be permitted to deactivate it | MUST |
| CON-026-08 | The catalog system MUST return an `ACK` immediately on receipt of `/catalog/pull` | MUST |
| CON-026-09 | The `context.transactionId` MUST be provided in `/catalog/pull` and MUST persist through to the `/catalog/on_pull` callback | MUST |
| CON-026-10 | Pull callbacks MUST carry terminal status only: `COMPLETED` or `FAILED` | MUST |
| CON-026-11 | The receiving Network Participant MUST deduplicate `/catalog/on_pull` callbacks on `context.transactionId` | MUST |
| CON-026-12 | On `COMPLETED` pull status, exactly one of `catalogs` or `objectUrl` MUST be present | MUST |
| CON-026-13 | Master resource search results MUST be paginated | MUST |
| CON-026-14 | Omitting a filter dimension in master search MUST match all values for that dimension | MUST |

---

## 8. Security Considerations

- All catalog API endpoints MUST enforce Beckn HTTP Signature authentication. Unauthenticated requests MUST be rejected with HTTP 401.
- Only the Network Participant that created a subscription MAY deactivate it, enforced via the Beckn auth header identity.
- Catalog data at rest and in transit SHOULD be protected per the Network Policy Profile.
- Rate limiting SHOULD be applied per Network Participant on publish and pull endpoints to prevent abuse.
- Pre-signed object URLs returned in `/catalog/on_pull` responses are short-lived and MUST NOT be used beyond their `expiresAt` timestamp.

---

## 9. Migration Notes

These catalog lifecycle APIs are new in Beckn v2 and have no direct equivalent in v1.x. Network Participants implementing v2.0 MUST implement the relevant catalog endpoints based on their role in the network. No backward-compatible migration path from v1.x is required.

---

## 10. References


- [3_RFC_Template.md](./3_RFC_Template.md)
- [2_Keyword_Definitions.md](./2_Keyword_Definitions.md)
- [14_Discovery_Architecture.md](./14_Discovery_Architecture.md)
- [GOVERNANCE.md](../GOVERNANCE.md)
- [beckn.yaml](../api/v2.0.0/beckn.yaml)

---

## 11. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | 2026-04-22 | | Initial draft |
