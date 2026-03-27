# Conformance and Testing

**Status:** Informative  
**Applies to:** Beckn Protocol v2.0.x (current LTS: v2.0.0)

---

## 1. Overview

This document defines what it means for a Beckn Network Participant to be **conformant** with Beckn Protocol v2.0.0, and provides guidance on testing and validating conformance.

---

## 2. Conformance Levels

The key words MUST, SHOULD, and MAY in this document are to be interpreted as defined in [29_Keyword_Definitions.md](./29_Keyword_Definitions.md).

A conformant implementation:
- **MUST** implement all normative requirements marked MUST.
- **SHOULD** implement all normative requirements marked SHOULD.
- **MAY** implement optional features.

Conformance is assessed per **actor role**: a BAP is assessed against BAP conformance requirements, a BPP against BPP requirements, and so on.

---

## 3. Transport Conformance (All Actor Roles)

The following requirements apply to every Beckn Network Participant regardless of role:

### 3.1 Endpoint

- MUST expose the action-specific endpoints required for the participant role as defined in `api/v2.0.0/beckn.yaml`.
- MUST support the HTTP methods defined for the actions relevant to their role.
- MUST support HTTPS (TLS 1.2 or later).

### 3.2 Request and Response Schemas

- MUST send and accept `RequestContainer` and `CallbackContainer` as defined in `api/v2.0.0/beckn.yaml`.
- MUST include a valid `Context` object on every request and callback.
- MUST respond with the correct transport response schema (`Ack`, `AckNoCallback`, `NackBadRequest`, `NackUnauthorized`, `ServerError`) for each defined scenario.

### 3.3 Authentication

- MUST sign every request and callback with a valid Beckn Signature in the `Authorization` header (except legacy GET Query mode, where it is a query parameter).
- MUST verify the Beckn Signature on every incoming request by resolving the sender's public key from the DeDi registry.
- MUST reject requests with invalid or expired signatures with `401 NackUnauthorized`.

### 3.4 Non-Repudiation (v2.0.0+)

- MUST return a `CounterSignature` in the `Ack` response body upon successful receipt of a signed request.
- MUST include `inReplyTo` in every `CallbackContainer`.

---

## 4. BAP Conformance Requirements

In addition to transport conformance:

- MUST send `RequestContainer` messages for all actions it initiates.
- MUST implement a callback endpoint to receive `CallbackContainer` responses from BPPs and DS.
- MUST send discovery queries to DS (not directly to BPPs).
- MUST NOT attempt to contact a BPP directly for discovery.

---

## 5. BPP Conformance Requirements

In addition to transport conformance:

- MUST implement the callback endpoint for all transaction actions it supports.
- MUST publish catalog updates to at least one PS instance.
- MUST register in the DeDi-compliant Registry with a valid signing key.
- MUST return `AckNoCallback` (409) when a request is received but no callback will follow.

---

## 6. PS Conformance Requirements

In addition to transport conformance:

- MUST accept `publish` action requests from BPPs.
- MUST validate published payloads against `core_schema` and relevant domain schema packs.
- MUST forward normalized catalog graphs to DS.
- MUST acknowledge publication with `Ack` (200) on successful receipt.

---

## 7. DS Conformance Requirements

In addition to transport conformance:

- MUST maintain a continuously updated index from PS feeds.
- MUST accept `discover` action requests from BAPs.
- MUST return results as `CallbackContainer` responses (async) or synchronous JSON responses per network policy.
- MUST NOT forward discovery requests to individual BPPs.

---

## 8. DeDi Registry Conformance Requirements

- MUST expose DeDi-compliant `subscribe`, `lookup`, and `unsubscribe` APIs.
- MUST store participant records with at minimum: `subscriberId`, `subscriberUrl`, `role`, `signingPublicKey`, `keyId`, `validFrom`, `validUntil`, `status`.
- MUST return `signingPublicKey` for valid `lookup` requests.
- MUST mark revoked keys with an appropriate status that causes lookup to fail.

---

## 9. Testing Guidance

### 9.1 Schema Validation

All `RequestContainer` and `CallbackContainer` messages SHOULD be validated against the OpenAPI schema in `api/v2.0.0/beckn.yaml` before sending and after receiving.

### 9.2 Signature Verification

A conformance test suite SHOULD:
- Send requests with known key pairs and verify that receivers correctly accept valid signatures.
- Send requests with expired signatures and verify `401 NackUnauthorized` responses.
- Send requests with tampered payloads and verify rejection.
- Verify that `CounterSignature` is present and valid in all `Ack` responses.

### 9.3 Lifecycle Testing

End-to-end conformance tests SHOULD exercise complete transaction lifecycles:
- Discovery: BAP → DS → `on_discover`
- Transaction: BAP → BPP (`select` → `on_select` → `init` → `on_init` → `confirm` → `on_confirm`)
- Catalog publication: BPP → PS → DS index

### 9.4 Negative Testing

- MUST verify that requests with missing `context` fields return `400 NackBadRequest`.
- MUST verify that requests with unsupported `version` values return `400 NackBadRequest`.
- MUST verify that unauthenticated requests return `401 NackUnauthorized`.

---

## 10. Further Reading

- [29_Keyword_Definitions.md](./29_Keyword_Definitions.md) — MUST / SHOULD / MAY definitions
- [08_Conformance_and_Certification.md](./08_Conformance_and_Certification.md) — normative conformance RFC
- `api/v2.0.0/beckn.yaml` — authoritative transport schemas
