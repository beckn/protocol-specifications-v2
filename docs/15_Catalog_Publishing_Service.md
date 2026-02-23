# Catalog Publishing Service (CPS)

**Status:** Draft  
**Author(s):**  
**Created:**  
**Updated:**  
**Conformance impact:** Major (defines a new required network actor)  
**Security/privacy implications:** CPS holds normalized catalog data from BPPs. Access control and data residency policies for the CPS are out of scope of the core protocol but MUST be defined in the Network Profile.  
**Replaces / Relates to:** Replaces the Beckn Gateway (BG) catalog pull model. Evolved from the "Search Provider" concept in BECKN-011 (v1.x).

---

## Abstract

This RFC defines the normative specification for the Catalog Publishing Service (CPS) — the catalog ingestion and normalization actor in a Beckn v2 network. BPPs push catalog updates to the CPS using the standard Beckn `publish` action. The CPS validates, normalizes, and forwards catalog graphs to one or more CDS instances for indexing.

---

## 1. Context

In v1.x, catalog data was never persistently stored outside BPPs. Every BAP search triggered a real-time pull from all BPPs via BG multicast. This created tight availability coupling: a BPP offline meant its catalog was unavailable for discovery.

The CPS decouples catalog availability from BPP availability by maintaining a continuously updated, normalized index of catalog data.

---

## 2. Specification (Normative)

### 2.1 CPS Endpoint

The CPS MUST expose the universal Beckn endpoint:

```
POST /beckn/publish
```

The CPS MUST authenticate the BPP sender by verifying the Beckn Signature and resolving the BPP's public key from the DeDi registry.

### 2.2 Publication Request

BPPs send a `RequestContainer` where `context.action = "publish"`:

```json
{
  "context": {
    "action": "publish",
    "domain": "beckn:retail",
    "version": "2.0.1",
    "bppId": "bpp.example.com",
    "bppUri": "https://bpp.example.com",
    "transactionId": "uuid",
    "messageId": "uuid",
    "timestamp": "2026-01-01T00:00:00Z",
    "ttl": "PT5M"
  },
  "message": {
    "@context": ["https://schema.beckn.io/core/v2/context.jsonld"],
    "@type": "CatalogUpdate",
    "provider": { "@type": "Provider", "id": "...", ... },
    "items": [ { "@type": "Item", ... } ],
    "offers": [ { "@type": "Offer", ... } ]
  }
}
```

### 2.3 CPS Response

On successful validation, the CPS MUST return `Ack` (HTTP 200) with a `CounterSignature`.

On validation failure, the CPS MUST return `NackBadRequest` (HTTP 400) with an error describing the schema violation.

### 2.4 Validation

The CPS MUST validate:
- The Beckn Signature on the incoming request.
- The `context` object for required fields.
- The `message` payload against the `core_schema` JSON-LD context and applicable domain schema packs.

The CPS SHOULD reject publications containing items with missing mandatory fields per the network's schema profile.

### 2.5 Normalization

After validation, the CPS MUST normalize the catalog payload:
- Expand JSON-LD shorthand using the declared `@context`.
- Map fields to canonical `core_schema` entity types.
- Apply deduplication using stable item identifiers (`Item.id`, `Provider.id`).
- Apply timestamps to determine freshness for incremental updates.

### 2.6 Forwarding to CDS

The CPS MUST forward normalized catalog graphs to all CDS instances configured in the network.

The CPS SHOULD use a reliable message queue or event stream for CPS → CDS forwarding to prevent data loss.

### 2.7 Item Removal

A BPP MUST indicate item removal by publishing items with a status marker (e.g., `"availability": {"status": "DISABLED"}`). The CPS MUST propagate this removal signal to all CDS instances.

### 2.8 Idempotency

Publication requests MUST be idempotent. Re-publishing the same item with the same content and timestamp MUST NOT create duplicate index entries.

---

## 3. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-016-01 | CPS MUST expose `POST /beckn/publish` | MUST |
| CON-016-02 | CPS MUST verify the Beckn Signature on every publication request | MUST |
| CON-016-03 | CPS MUST return `Ack` with `CounterSignature` on successful receipt | MUST |
| CON-016-04 | CPS MUST validate `message` against `core_schema` | MUST |
| CON-016-05 | CPS MUST forward normalized graphs to CDS | MUST |
| CON-016-06 | CPS MUST handle item removal signals | MUST |
| CON-016-07 | BPPs MUST publish catalog updates to at least one CPS | MUST |
| CON-016-08 | BPPs SHOULD send incremental updates, not full snapshots | SHOULD |

---

## 4. Security Considerations

- The CPS holds aggregated catalog data. It MUST enforce authentication on all `publish` requests.
- The CPS SHOULD apply rate limiting per BPP to prevent denial-of-service via excessive publication requests.
- Data residency and access control for catalog data at rest are governed by the Network Profile.

---

## 5. References

- [14_Discovery_Architecture.md](./14_Discovery_Architecture.md)
- [16_Catalog_Discovery_Service.md](./16_Catalog_Discovery_Service.md)
- [`beckn/core_schema`](https://github.com/beckn/core_schema)

---

## 6. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | | | Initial draft |
