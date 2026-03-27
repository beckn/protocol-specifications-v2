# Discovery Service (DS)
## CWG Working Draft - 2026-03-27

# 1. Document Details
## 1.1 Version History
| Version | Date | Summary |
|---|---|---|
| Draft-01 | 2026-03-27 | Migrated to v2 RFC template structure |

## 1.2 Latest editor's draft
- ./14_Catalog_Discovery_Service.md

## 1.3 Implementation report
- To be published by implementation working group.

## 1.4 Stress Test Report
- To be published by testing and certification working group.

## 1.5 Editors
- Beckn Protocol Core Working Group editors.

## 1.6 Authors
- Beckn Protocol contributors.

## 1.7 Feedback
### 1.7.1 Issues
- https://github.com/beckn/protocol-specifications-v2/issues

### 1.7.2 Discussions
- https://github.com/beckn/protocol-specifications-v2/discussions

### 1.7.3 Pull Requests
- https://github.com/beckn/protocol-specifications-v2/pulls

## 1.8 Errata
- To be published.

<!-- TOC START -->
## Table of Contents

  - [CWG Working Draft - 2026-03-27](#cwg-working-draft-2026-03-27)
- [1. Document Details](#1-document-details)
  - [1.1 Version History](#11-version-history)
  - [1.2 Latest editor's draft](#12-latest-editors-draft)
  - [1.3 Implementation report](#13-implementation-report)
  - [1.4 Stress Test Report](#14-stress-test-report)
  - [1.5 Editors](#15-editors)
  - [1.6 Authors](#16-authors)
  - [1.7 Feedback](#17-feedback)
    - [1.7.1 Issues](#171-issues)
    - [1.7.2 Discussions](#172-discussions)
    - [1.7.3 Pull Requests](#173-pull-requests)
  - [1.8 Errata](#18-errata)
- [2. Context](#2-context)
  - [Abstract](#abstract)
  - [1. Context](#1-context)
  - [2. Specification (Normative)](#2-specification-normative)
    - [2.1 DS Endpoint](#21-ds-endpoint)
    - [2.2 Discovery Request](#22-discovery-request)
    - [2.3 DS Response](#23-ds-response)
    - [2.4 Discovery Results](#24-discovery-results)
    - [2.5 Index Maintenance](#25-index-maintenance)
    - [2.6 Query Execution](#26-query-execution)
    - [2.7 Synchronous Mode (Optional)](#27-synchronous-mode-optional)
  - [3. Conformance Requirements](#3-conformance-requirements)
  - [4. Security Considerations](#4-security-considerations)
  - [5. References](#5-references)
  - [6. Changelog](#6-changelog)
<!-- TOC END -->

# 2. Context

**Status:** Draft  
**Author(s):**  
**Created:**  
**Updated:**  
**Conformance impact:** Major (defines a new required network actor)  
**Security/privacy implications:** Discovery queries may contain sensitive user intent data. The DS SHOULD apply appropriate data minimization when logging queries.  
**Replaces / Relates to:** Replaces the legacy gateway layer (legacy gateway) for discovery. Evolved from the "Search Provider" concept in BECKN-011 (legacy pre-v2).

---

## Abstract

This RFC defines the normative specification for the Discovery Service (DS) — the discovery query engine in a Beckn v2 network. The DS maintains a continuously updated index of catalog data received from one or more PS instances. BAPs query the DS for discovery using the `discover` action. The DS does not forward queries to BPPs; all discovery is served from its own index.

---

## 1. Context

In legacy pre-v2, every BAP discovery request triggered a real-time fan-out to all BPPs via legacy gateway multicast. This was slow, stateless, and did not scale. The DS replaces this with a stateful, index-based approach — analogous to a discover engine maintaining a crawled index of content.

---

## 2. Specification (Normative)

### 2.1 DS Endpoint

The DS MUST expose the universal Beckn endpoint:

```
GET  /discover      ← Body Mode (preferred for server-to-server)
POST /discover      ← POST mode
GET  /discover?...  ← Query Mode (for client-initiated discovery)
```

The DS MUST authenticate the BAP sender by verifying the Beckn Signature.

### 2.2 Discovery Request

BAPs send a `RequestContainer` where `context.action = "discover"`:

```json
{
  "context": {
    "action": "discover",
    "domain": "beckn:retail",
    "version": "2.0.0",
    "bapId": "bap.example.com",
    "bapUri": "https://bap.example.com",
    "transactionId": "uuid",
    "messageId": "uuid",
    "timestamp": "2026-01-01T00:00:00Z",
    "ttl": "PT30S"
  },
  "message": {
    "@type": "Intent",
    "item": {
      "@type": "Item",
      "name": "coffee",
      "category": { "@type": "Category", "name": "Beverages" }
    },
    "fulfillment": {
      "location": { "gps": "12.9716,77.5946", "radius": { "value": 5, "unit": "km" } }
    }
  }
}
```

### 2.3 DS Response

The DS MUST immediately return `Ack` (HTTP 200) with a `CounterSignature`.

The DS MUST send results as a `CallbackContainer` (action: `on_discover`) to the BAP's `bapUri`. Each callback MUST include `inReplyTo` binding it to the original discovery request.

The DS MAY send multiple `on_discover` callbacks for a single request (e.g., paginated results, progressive loading).

### 2.4 Discovery Results

The `CallbackContainer` message contains a subset of the DS index matching the query:

```json
{
  "context": { "action": "on_discover", ... },
  "message": {
    "@type": "Catalog",
    "providers": [
      {
        "@type": "Provider",
        "id": "provider-uuid",
        "descriptor": { "name": "Blue Bottle Coffee" },
        "items": [ { "@type": "Item", ... } ],
        "offers": [ { "@type": "Offer", ... } ]
      }
    ]
  },
  "inReplyTo": { ... }
}
```

### 2.5 Index Maintenance

The DS MUST maintain a continuously updated index by consuming normalized catalog graphs from PS.

The DS MUST reflect item removals (signaled by PS) within a network-policy-defined maximum propagation delay.

### 2.6 Query Execution

The DS SHOULD support:
- Full-text discover over item names and descriptions.
- Geo-spatial filtering (radius discover, bounding box).
- Category and taxonomy filtering.
- Price range filtering.
- Availability filtering.

The DS MAY apply network-configurable ranking and relevance scoring.

### 2.7 Synchronous Mode (Optional)

Networks MAY configure the DS to return results synchronously (HTTP 200 with catalog body) instead of via async callback. This is appropriate for Query Mode requests (where callbacks are not expected).

---

## 3. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-017-01 | DS MUST expose `GET /discover` and `POST /discover` | MUST |
| CON-017-02 | DS MUST verify the Beckn Signature on every discovery request | MUST |
| CON-017-03 | DS MUST return `Ack` with `CounterSignature` on successful receipt | MUST |
| CON-017-04 | DS MUST send results via `on_discover` callback to BAP | MUST |
| CON-017-05 | DS MUST NOT forward discovery requests to BPPs | MUST |
| CON-017-06 | DS MUST consume catalog updates from PS | MUST |
| CON-017-07 | DS MUST propagate item removals within the network-defined delay | MUST |
| CON-017-08 | BAPs MUST send discovery queries to DS, not directly to BPPs | MUST |

---

## 4. Security Considerations

- Discovery queries may contain sensitive user intent data (location, health queries, financial queries). The DS SHOULD log only what is necessary for operational purposes.
- The DS MUST reject unauthenticated requests.
- Rate limiting SHOULD be applied per BAP.

---

## 5. References

- [12_Discovery_Architecture.md](./12_Discovery_Architecture.md)
- [13_Catalog_Publishing_Service.md](./13_Catalog_Publishing_Service.md)
- [`beckn/core_schema`](https://github.com/beckn/core_schema)

---

## 6. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | | | Initial draft |
