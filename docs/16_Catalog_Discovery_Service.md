# Catalog Discovery Service (CDS)

**Status:** Draft  
**Author(s):**  
**Created:**  
**Updated:**  
**Conformance impact:** Major (defines a new required network actor)  
**Security/privacy implications:** Discovery queries may contain sensitive user intent data. The CDS SHOULD apply appropriate data minimization when logging queries.  
**Replaces / Relates to:** Replaces the Beckn Gateway (BG) for discovery. Evolved from the "Search Provider" concept in BECKN-011 (v1.x).

---

## Abstract

This RFC defines the normative specification for the Catalog Discovery Service (CDS) — the discovery query engine in a Beckn v2 network. The CDS maintains a continuously updated index of catalog data received from one or more CPS instances. BAPs query the CDS for discovery using the `discover` action. The CDS does not forward queries to BPPs; all discovery is served from its own index.

---

## 1. Context

In v1.x, every BAP discovery request triggered a real-time fan-out to all BPPs via BG multicast. This was slow, stateless, and did not scale. The CDS replaces this with a stateful, index-based approach — analogous to a search engine maintaining a crawled index of content.

---

## 2. Specification (Normative)

### 2.1 CDS Endpoint

The CDS MUST expose the universal Beckn endpoint:

```
GET  /beckn/discover      ← Body Mode (preferred for server-to-server)
POST /beckn/discover      ← POST mode
GET  /beckn/discover?...  ← Query Mode (for client-initiated discovery)
```

The CDS MUST authenticate the BAP sender by verifying the Beckn Signature.

### 2.2 Discovery Request

BAPs send a `RequestContainer` where `context.action = "discover"`:

```json
{
  "context": {
    "action": "discover",
    "domain": "beckn:retail",
    "version": "2.0.1",
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

### 2.3 CDS Response

The CDS MUST immediately return `Ack` (HTTP 200) with a `CounterSignature`.

The CDS MUST send results as a `CallbackContainer` (action: `on_discover`) to the BAP's `bapUri`. Each callback MUST include `inReplyTo` binding it to the original discovery request.

The CDS MAY send multiple `on_discover` callbacks for a single request (e.g., paginated results, progressive loading).

### 2.4 Discovery Results

The `CallbackContainer` message contains a subset of the CDS index matching the query:

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

The CDS MUST maintain a continuously updated index by consuming normalized catalog graphs from CPS.

The CDS MUST reflect item removals (signaled by CPS) within a network-policy-defined maximum propagation delay.

### 2.6 Query Execution

The CDS SHOULD support:
- Full-text search over item names and descriptions.
- Geo-spatial filtering (radius search, bounding box).
- Category and taxonomy filtering.
- Price range filtering.
- Availability filtering.

The CDS MAY apply network-configurable ranking and relevance scoring.

### 2.7 Synchronous Mode (Optional)

Networks MAY configure the CDS to return results synchronously (HTTP 200 with catalog body) instead of via async callback. This is appropriate for Query Mode requests (where callbacks are not expected).

---

## 3. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-017-01 | CDS MUST expose `GET /beckn/discover` and `POST /beckn/discover` | MUST |
| CON-017-02 | CDS MUST verify the Beckn Signature on every discovery request | MUST |
| CON-017-03 | CDS MUST return `Ack` with `CounterSignature` on successful receipt | MUST |
| CON-017-04 | CDS MUST send results via `on_discover` callback to BAP | MUST |
| CON-017-05 | CDS MUST NOT forward discovery requests to BPPs | MUST |
| CON-017-06 | CDS MUST consume catalog updates from CPS | MUST |
| CON-017-07 | CDS MUST propagate item removals within the network-defined delay | MUST |
| CON-017-08 | BAPs MUST send discovery queries to CDS, not directly to BPPs | MUST |

---

## 4. Security Considerations

- Discovery queries may contain sensitive user intent data (location, health queries, financial queries). The CDS SHOULD log only what is necessary for operational purposes.
- The CDS MUST reject unauthenticated requests.
- Rate limiting SHOULD be applied per BAP.

---

## 5. References

- [14_Discovery_Architecture.md](./14_Discovery_Architecture.md)
- [15_Catalog_Publishing_Service.md](./15_Catalog_Publishing_Service.md)
- [`beckn/core_schema`](https://github.com/beckn/core_schema)

---

## 6. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | | | Initial draft |
