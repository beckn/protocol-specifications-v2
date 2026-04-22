# RFC-08: Catalog APIs

## 1. Document Details

- **Status:** Draft.
- **Authors:** Beckn Protocol contributors.
- **Created:** 2026-04-22.
- **Updated:** 2026-04-22.
- **Version history:** To be published.
- **Latest editor's draft:** Click [here](https://github.com/beckn/protocol-specifications-v2/blob/schema-update/docs/08_Catalog_APIs.md).
- **Implementation report:** To be published by implementation working group.
- **Stress test report:** To be published by testing and certification working group.
- **Conformance impact:** Major (introduces catalog lifecycle management APIs for Beckn v2 networks).
- **Security/privacy implications:** Catalog data is published and distributed across Network Participants. Authentication via Beckn HTTP Signature is required on all endpoints. Subscription callbacks must be secured to prevent unauthorized catalog injection.
- **Replaces / Relates to:** Supersedes 15_Catalog_Publishing_Service.md and 16_Catalog_Discovery_Service.md.
- **Feedback:** Issues: Click [here](https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%22RFC-08%22); Discussions: Click [here](https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22RFC-08%22); Pull Requests: Click [here](https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22RFC-08%22).
- **Errata:** To be published.

## 2. Abstract

This RFC defines the normative specification for all Catalog APIs in Beckn Protocol v2. It covers the full catalog lifecycle: publishing catalogs for network indexing, pushing catalogs to edge discovery services, subscribing to catalog update streams, pulling catalogs on demand, and searching master resource definitions. All APIs follow the standard Beckn asynchronous request-callback pattern and use Network Participant terminology throughout.

## 3. Table of Contents

- [Introduction](#4-introduction)
- [4.1 Terminology](#41-terminology)
- [4.2 Design Principles](#42-design-principles)
- [Specification](#5-specification)
- [5.1 Normative Requirements](#51-normative-requirements)
- [5.2 Conformance Requirements](#52-conformance-requirements)
- [5.3 Security and Privacy Considerations](#53-security-and-privacy-considerations)
- [5.4 Migration Notes](#54-migration-notes)
- [5.5 Examples](#55-examples)
- [Conclusion](#6-conclusion)
- [6.1 Changelog](#61-changelog)
- [Acknowledgements](#7-acknowledgements)
- [References](#8-references)

## 4. Introduction

In Beckn v2 networks, catalog data must flow efficiently from providers to discovery services. Network Participants need standardized APIs to publish, distribute, subscribe to, and query catalog data across networks. Without a unified, normative specification for catalog lifecycle management, Network Participants cannot interoperably exchange catalog data, edge discovery services have no standard interface for receiving catalog updates, and master resource definitions cannot be consistently queried across networks. This RFC formalizes those APIs to ensure consistent interoperability across all network implementations, enabling decoupled catalog synchronization, efficient incremental updates, and reusable master resource definitions.

### 4.1 Terminology

- **Normative:** Requirements that define conformance and interoperability behavior.
- **Informative:** Explanatory guidance that does not by itself define conformance.
- **Network Participant:** Any entity registered on a Beckn network that implements one or more Beckn protocol APIs.
- **Catalog system:** The server-side system responsible for ingesting, indexing, and distributing catalog data across the network.
- **Edge discovery service:** A discovery service owned and operated by a Network Participant, receiving catalog updates via `/catalog/push`.
- **Subscription:** A persistent registration by a Network Participant to receive catalog updates for specified networks and/or schema types.
- **Conformance impact:** Classification of expected compatibility effect (Patch, Minor, Major, Informative).
- **Migration notes:** Operational guidance required to adopt the change safely.
- **Errata:** Post-publication corrections and clarifications.

### 4.2 Design Principles

_Refer to [GOVERNANCE.md](../GOVERNANCE.md) for the current governance source._

- **Interoperability-first:** All catalog APIs use the standard Beckn context and message envelope, ensuring any conformant Network Participant can exchange catalog data.
- **Abstraction over specificity:** APIs are domain-neutral and support any schema type, not tied to any specific vertical or catalog structure.
- **Optimal ignorance:** Each API exposes only the information necessary for its function. Publishing does not require knowledge of downstream subscribers.
- **Security by design:** All endpoints require Beckn HTTP Signature authentication. Only the Network Participant that created a subscription can deactivate it.
- **Reusability before novelty:** Master resource definitions enable resource reuse across catalogs, avoiding duplication of canonical data.

## 5. Specification

_Use MUST / SHOULD / MAY as defined in [Keyword Definitions](https://github.com/beckn/protocol-specifications-v2/blob/main/docs/2_Keyword_Definitions.md)._

### 5.1 Normative Requirements

#### 5.1.1 Catalog Publish

**`POST /catalog/publish`**

A Network Participant submits one or more catalogs for indexing. The catalog system returns an immediate `ACK` and processes catalogs asynchronously, delivering per-catalog results via `/catalog/on_publish`.

- The Network Participant MUST include a valid Beckn HTTP Signature on every publish request.
- The catalog system MUST return an `ACK` immediately on receipt.
- The catalog system MUST validate catalog payloads against the declared schema type.
- The catalog system MUST deliver per-catalog processing results to `/catalog/on_publish` asynchronously.

**`POST /catalog/on_publish`**

Callback endpoint implemented by the Network Participant to receive per-catalog publish processing results. The catalog system delivers indexing results here after processing is complete.

- The Network Participant MUST implement `POST /catalog/on_publish` to receive processing results.
- The Network Participant MUST respond with `ACK` on receipt of the callback.

#### 5.1.2 Catalog Push

**`POST /catalog/push`**

Endpoint implemented by the edge discovery service owned by a Network Participant. The catalog system invokes this endpoint to push and sync catalogs to the discovery service, keeping it up to date with the subscribed network catalogs.

- The edge discovery service MUST implement `POST /catalog/push`.
- The catalog system MUST authenticate via Beckn HTTP Signature on every push request.
- The edge discovery service MUST return an `ACK` immediately on receipt.
- The edge discovery service MUST apply received catalogs to its local index.

#### 5.1.3 Catalog Subscription

**`POST /catalog/subscription`**

A Network Participant creates a subscription to receive catalog updates for specified networks and/or schema types.

- At least one of `networkIds` or `schemaTypes` MUST be provided.
- The catalog system MUST return an existing active subscription if an identical scope subscription already exists (idempotent).
- The catalog system MUST generate and return a unique `subscriptionId` UUID for each new subscription.

**`DELETE /catalog/subscription/{subscriptionId}`**

Deactivates an active subscription. Only the Network Participant that created the subscription can deactivate it.

- The `subscriptionId` MUST be provided as a path parameter.
- The catalog system MUST verify that the requesting Network Participant is the creator of the subscription before deactivating it.
- Subscription status after deactivation MUST be `INACTIVE`.

**`GET /catalog/subscriptions`**

Returns all active subscriptions for the calling Network Participant.

- The catalog system MUST scope results to the calling Network Participant's identity.
- The caller MAY filter to a single subscription using the `?id=<uuid>` query parameter.

#### 5.1.4 Catalog Pull

**`POST /catalog/pull`**

A Network Participant requests catalogs matching specified filters. Returns an immediate `ACK`; results are delivered asynchronously via `/catalog/on_pull`.

Two modes are supported:

- **FULL** — returns the latest version of each matching catalog.
- **INCREMENTAL** — returns all catalog versions indexed between `fromDate` and `toDate`, useful for syncing changes since the last pull. The date range MUST NOT exceed 5 days per request.

Requirements:

- At least one of `catalogIds`, `networkIds`, or `schemaTypes` MUST be provided in `filters`.
- The `context.transactionId` MUST be provided and MUST persist through to the `/catalog/on_pull` callback.
- The catalog system MUST return an `ACK` immediately on receipt.
- The catalog system MUST deliver results to `/catalog/on_pull` asynchronously.

**`POST /catalog/on_pull`**

Callback endpoint hosted by the receiving Network Participant. After the Network Participant submits a `/catalog/pull` request, the results are delivered here asynchronously.

- The Network Participant MUST implement `POST /catalog/on_pull` to receive pull results.
- The callback MUST carry terminal status only: `COMPLETED` or `FAILED`.
- The callback is delivered with at-least-once semantics; the receiving Network Participant MUST deduplicate on `context.transactionId`.
- On `COMPLETED` status, exactly one of `catalogs` (inline) or `objectUrl` (pre-signed download link) MUST be present.
- On `FAILED` status, the `error` field MUST carry the failure reason.
- The Network Participant MUST respond with `ACK` on receipt of the callback.

#### 5.1.5 Master Resource Search

**`POST /catalog/master/search`**

Search for canonical master resource definitions across networks. Filter by network and schema type; results are paginated and grouped by catalog.

**`GET /catalog/master/schemaTypes`**

Returns the distinct schema type URIs available across all master resources.

**`GET /catalog/master/{masterItemId}`**

Returns a single master resource by its identifier, wrapped in its catalog envelope with full provider and descriptor metadata.

Requirements:

- The catalog system MUST support filtering by `networkIds` and/or `schemaTypes`.
- Omitting a filter dimension MUST match all values for that dimension.
- Master resource search results MUST be paginated.
- The catalog system MUST return the full catalog envelope (including provider and descriptor metadata) for individual master resource lookups.

---

### 5.2 Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-08-01 | Network Participants MUST authenticate all catalog API requests via Beckn HTTP Signature | MUST |
| CON-08-02 | The catalog system MUST return an `ACK` immediately on receipt of `/catalog/publish` | MUST |
| CON-08-03 | The catalog system MUST deliver per-catalog results to `/catalog/on_publish` asynchronously | MUST |
| CON-08-04 | Edge discovery services MUST implement `POST /catalog/push` | MUST |
| CON-08-05 | At least one of `networkIds` or `schemaTypes` MUST be provided when creating a subscription | MUST |
| CON-08-06 | Subscription status MUST be either `ACTIVE` or `INACTIVE` | MUST |
| CON-08-07 | Only the Network Participant that created a subscription MUST be permitted to deactivate it | MUST |
| CON-08-08 | The catalog system MUST return an `ACK` immediately on receipt of `/catalog/pull` | MUST |
| CON-08-09 | The `context.transactionId` MUST be provided in `/catalog/pull` and MUST persist through to the `/catalog/on_pull` callback | MUST |
| CON-08-10 | Pull callbacks MUST carry terminal status only: `COMPLETED` or `FAILED` | MUST |
| CON-08-11 | The receiving Network Participant MUST deduplicate `/catalog/on_pull` callbacks on `context.transactionId` | MUST |
| CON-08-12 | On `COMPLETED` pull status, exactly one of `catalogs` or `objectUrl` MUST be present | MUST |
| CON-08-13 | The `fromDate` to `toDate` range in INCREMENTAL pull requests MUST NOT exceed 5 days | MUST |
| CON-08-14 | Master resource search results MUST be paginated | MUST |
| CON-08-15 | Omitting a filter dimension in master search MUST match all values for that dimension | MUST |

---

### 5.3 Security and Privacy Considerations

- All catalog API endpoints MUST enforce Beckn HTTP Signature authentication. Unauthenticated requests MUST be rejected with HTTP 401.
- Only the Network Participant that created a subscription MAY deactivate it, enforced via the Beckn auth header identity.
- Catalog data at rest and in transit SHOULD be protected per the Network Policy Profile.
- Rate limiting SHOULD be applied per Network Participant on publish and pull endpoints to prevent abuse.
- Pre-signed object URLs returned in `/catalog/on_pull` responses are short-lived and MUST NOT be used beyond their `expiresAt` timestamp.

---

### 5.4 Migration Notes

These catalog lifecycle APIs are new in Beckn v2 and have no direct equivalent in v1.x. Network Participants implementing v2.0 MUST implement the relevant catalog endpoints based on their role in the network. No backward-compatible migration path from v1.x is required.

---

### 5.5 Examples

#### Example 1 — Publish a catalog

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

#### Example 2 — Subscribe to catalog updates

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

#### Example 3 — Pull catalogs (INCREMENTAL mode)

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
    "toDate": "2026-04-06T00:00:00.000Z"
  }
}
```

#### Example 4 — on_pull callback (success, inline)

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

#### Example 5 — Deactivate a subscription

```
DELETE /catalog/subscription/f47ac10b-58cc-4372-a567-0e02b2c3d479
Authorization: Signature ...
```

#### Example 6 — Search master resources

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
    "filters": {
      "networkIds": ["retail"],
      "schemaTypes": [
        "https://schema.beckn.org/retail/schema/1.1.0/item.json#ItemType"
      ]
    },
    "limit": 20,
    "offset": 0
  }
}
```

## 6. Conclusion

This RFC defines the full catalog lifecycle API surface for Beckn Protocol v2, covering catalog publishing, edge discovery sync, subscription management, on-demand pull, and master resource search. Conformant implementations of these APIs will enable consistent, interoperable catalog data exchange across all Beckn v2 networks. The RFC advances to Candidate status when at least one reference implementation has been validated against the conformance requirements in Section 5.2.

### 6.1 Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | 2026-04-22 | | Initial draft |

## 7. Acknowledgements

Beckn Protocol contributors and the implementation working group whose feedback shaped the catalog API design.

## 8. References

- **Governance:** [GOVERNANCE.md](../GOVERNANCE.md).
- **Keyword definitions:** [2_Keyword_Definitions.md](https://github.com/beckn/protocol-specifications-v2/blob/main/docs/2_Keyword_Definitions.md).
- **API specification:** [beckn.yaml](../api/v2.0.0/beckn.yaml).
- **Prior art:** 15_Catalog_Publishing_Service.md, 16_Catalog_Discovery_Service.md.
