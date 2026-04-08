# Cataloging Service (PS)
## CWG Working Draft - 2026-03-27

# 1. Document Details
## 1.1 Version History
| Version | Date | Summary |
|---|---|---|
| Draft-01 | 2026-03-27 | Migrated to v2 RFC template structure |

## 1.2 Latest editor's draft
- ./10_Cataloging_Service.md

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
- https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%22RFC-013%22

### 1.7.2 Discussions
- https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22RFC-013%22

### 1.7.3 Pull Requests
- https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22RFC-013%22

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
    - [2.1 PS Endpoint](#21-ps-endpoint)
    - [2.2 Publication Request](#22-publication-request)
    - [2.3 PS Response](#23-ps-response)
    - [2.4 Validation](#24-validation)
    - [2.5 Normalization](#25-normalization)
    - [2.6 Forwarding to DS](#26-forwarding-to-ds)
    - [2.7 Item Removal](#27-item-removal)
    - [2.8 Idempotency](#28-idempotency)
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
**Security/privacy implications:** PS holds normalized catalog data from BPPs. Access control and data residency policies for the PS are out of scope of the core protocol but MUST be defined in the Network Profile.  
**Replaces / Relates to:** Replaces the legacy gateway layer (legacy gateway) catalog pull model. Evolved from the "Search Provider" concept in BECKN-011 (legacy pre-v2).

---

## Abstract

This RFC defines the normative specification for the Publishing Service (PS) — the catalog ingestion and normalization actor in a Beckn v2 network. BPPs push catalog updates to the PS using the standard Beckn `publish` action. The PS validates, normalizes, and forwards catalog graphs to one or more DS instances for indexing.

---

## 1. Context

In legacy pre-v2, catalog data was never persistently stored outside BPPs. Every BAP discover triggered a real-time pull from all BPPs via legacy gateway multicast. This created tight availability coupling: a BPP offline meant its catalog was unavailable for discovery.

The PS decouples catalog availability from BPP availability by maintaining a continuously updated, normalized index of catalog data.

---

## 2. Specification (Normative)

### 2.1 PS Endpoint

The PS MUST expose the universal Beckn endpoint:

```
POST /catalog/publish
```

The PS MUST authenticate the BPP sender by verifying the Beckn Signature and resolving the BPP's public key from the DeDi registry.

### 2.2 Publication Request

BPPs send a `RequestContainer` where `context.action = "publish"`:

```json
{
  "context": {
    "action": "publish",
    "domain": "beckn:retail",
    "version": "2.0.0",
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

### 2.3 PS Response

On successful validation, the PS MUST return `Ack` (HTTP 200) with a `CounterSignature`.

On validation failure, the PS MUST return `NackBadRequest` (HTTP 400) with an error describing the schema violation.

### 2.4 Validation

The PS MUST validate:
- The Beckn Signature on the incoming request.
- The `context` object for required fields.
- The `message` payload against the `core_schema` JSON-LD context and applicable domain schema packs.

The PS SHOULD reject publications containing items with missing mandatory fields per the network's schema profile.

### 2.5 Normalization

After validation, the PS MUST normalize the catalog payload:
- Expand JSON-LD shorthand using the declared `@context`.
- Map fields to canonical `core_schema` entity types.
- Apply deduplication using stable item identifiers (`Item.id`, `Provider.id`).
- Apply timestamps to determine freshness for incremental updates.

### 2.6 Forwarding to DS

The PS MUST forward normalized catalog graphs to all DS instances configured in the network.

The PS SHOULD use a reliable message queue or event stream for PS → DS forwarding to prevent data loss.

### 2.7 Item Removal

A BPP MUST indicate item removal by publishing items with a status marker (e.g., `"availability": {"status": "DISABLED"}`). The PS MUST propagate this removal signal to all DS instances.

### 2.8 Idempotency

Publication requests MUST be idempotent. Re-publishing the same item with the same content and timestamp MUST NOT create duplicate index entries.

---

## 3. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-016-01 | PS MUST expose `POST /catalog/publish` | MUST |
| CON-016-02 | PS MUST verify the Beckn Signature on every publication request | MUST |
| CON-016-03 | PS MUST return `Ack` with `CounterSignature` on successful receipt | MUST |
| CON-016-04 | PS MUST validate `message` against `core_schema` | MUST |
| CON-016-05 | PS MUST forward normalized graphs to DS | MUST |
| CON-016-06 | PS MUST handle item removal signals | MUST |
| CON-016-07 | BPPs MUST publish catalog updates to at least one PS | MUST |
| CON-016-08 | BPPs SHOULD send incremental updates, not full snapshots | SHOULD |

---

## 4. Security Considerations

- The PS holds aggregated catalog data. It MUST enforce authentication on all `publish` requests.
- The PS SHOULD apply rate limiting per BPP to prevent denial-of-service via excessive publication requests.
- Data residency and access control for catalog data at rest are governed by the Network Profile.

---

## 5. References

- [09_Discovery_Architecture.md](./09_Discovery_Architecture.md)
- [11_Discovery_Service.md](./11_Discovery_Service.md)
- [`beckn/core_schema`](https://github.com/beckn/core_schema)

---

## 6. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | | | Initial draft |
