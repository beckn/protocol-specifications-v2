# Conformance Rules and Certification Criteria

**Status:** Draft  
**Author(s):**  
**Created:**  
**Updated:**  
**Conformance impact:** Informative for protocol; normative for certification programs  
**Security/privacy implications:** Certification test suites MUST NOT expose or retain production signing keys or sensitive participant data used during testing.  
**Replaces / Relates to:** New in v2. Provides the normative conformance framework referenced by [24_Conformance_and_Testing.md](./24_Conformance_and_Testing.md).

---

## Abstract

This RFC defines the normative conformance rules and certification criteria for Beckn Protocol v2.0.1. It enumerates the machine-verifiable requirements for each actor role (BAP, BPP, CPS, CDS, DeDi Registry), defines the structure of a conformance test suite, and establishes the criteria for a participant to claim Beckn v2.0.1 conformance.

---

## 1. Conformance Claims

A participant claims conformance to Beckn Protocol v2.0.1 by:
1. Implementing all MUST requirements for its actor role (as defined in this RFC).
2. Successfully passing the Beckn v2.0.1 conformance test suite for its role.
3. Declaring its conformance claim in its DeDi registry record.

Conformance claims are role-specific. A participant implementing both BAP and BPP roles MUST pass conformance tests for both roles.

---

## 2. Common Requirements (All Roles)

All actor roles MUST satisfy the following:

| ID | Requirement |
|---|---|
| C-ALL-01 | Expose `/beckn/{becknEndpoint}` over HTTPS (TLS 1.2+) |
| C-ALL-02 | Sign all outgoing requests with a valid Beckn Signature (Ed25519, BLAKE2b-512) |
| C-ALL-03 | Verify all incoming request signatures by resolving public keys from the DeDi registry |
| C-ALL-04 | Reject requests with invalid or expired signatures with `401 NackUnauthorized` |
| C-ALL-05 | Include a valid `Context` object with all mandatory fields on every request |
| C-ALL-06 | Return the correct transport response schema for each defined scenario |
| C-ALL-07 | Return `CounterSignature` in every `Ack` (HTTP 200) response |
| C-ALL-08 | Register in the DeDi registry with a valid `signingPublicKey` and `keyId` |

---

## 3. BAP Conformance Requirements

| ID | Requirement |
|---|---|
| C-BAP-01 | Send `RequestContainer` for all initiated actions |
| C-BAP-02 | Implement a callback endpoint for `CallbackContainer` responses |
| C-BAP-03 | Send discovery queries to CDS (not directly to BPPs) |
| C-BAP-04 | Verify `inReplyTo` on received `CallbackContainer` messages |
| C-BAP-05 | Handle `AckNoCallback` (409) without expecting a subsequent callback |

---

## 4. BPP Conformance Requirements

| ID | Requirement |
|---|---|
| C-BPP-01 | Implement callback endpoints for all supported transaction actions |
| C-BPP-02 | Include `inReplyTo` in all sent `CallbackContainer` messages |
| C-BPP-03 | Publish catalog updates to at least one registered CPS |
| C-BPP-04 | Return `AckNoCallback` (409) when no callback will follow |
| C-BPP-05 | Return appropriate application-level error codes (Section 3 of RFC-021) |

---

## 5. CPS Conformance Requirements

| ID | Requirement |
|---|---|
| C-CPS-01 | Accept `publish` action requests from authenticated BPPs |
| C-CPS-02 | Validate `message` against `core_schema` and applicable domain schema packs |
| C-CPS-03 | Return `Ack` with `CounterSignature` on successful receipt |
| C-CPS-04 | Forward normalized catalog graphs to all configured CDS instances |
| C-CPS-05 | Process item removal signals and propagate to CDS |
| C-CPS-06 | Implement idempotent publication (duplicate submissions MUST NOT create duplicates) |

---

## 6. CDS Conformance Requirements

| ID | Requirement |
|---|---|
| C-CDS-01 | Accept `discover` action requests from authenticated BAPs |
| C-CDS-02 | Return `Ack` with `CounterSignature` on successful receipt |
| C-CDS-03 | Return discovery results via `on_discover` callback with `inReplyTo` |
| C-CDS-04 | NOT forward discovery requests to individual BPPs |
| C-CDS-05 | Consume catalog updates from CPS and maintain a current index |
| C-CDS-06 | Reflect item removals within the network-defined propagation delay |

---

## 7. DeDi Registry Conformance Requirements

| ID | Requirement |
|---|---|
| C-REG-01 | Expose DeDi-compliant `subscribe`, `lookup`, and `unsubscribe` APIs |
| C-REG-02 | Store all required participant record fields |
| C-REG-03 | Return `signingPublicKey` for valid `lookup` requests |
| C-REG-04 | Return 404/410 for revoked or unsubscribed participant keys |
| C-REG-05 | Retain historical records for audit purposes after unsubscribe |

---

## 8. Conformance Test Suite Structure

A Beckn v2.0.1 conformance test suite MUST include:

### 8.1 Schema Validation Tests
- Validate that outgoing messages conform to `api/v2.0.1/beckn.yaml`.
- Validate that required fields are present in all contexts.

### 8.2 Signature Tests
- Verify that valid signatures are accepted.
- Verify that expired signatures return `401`.
- Verify that tampered payloads return `401`.
- Verify that `CounterSignature` is present and verifiable in `Ack` responses.
- Verify that `inReplyTo` is present and correct in `CallbackContainer` messages.

### 8.3 Flow Tests
- Full discovery lifecycle: `discover` → `on_discover`.
- Full transaction lifecycle: `select` → `on_select` → `init` → `on_init` → `confirm` → `on_confirm`.
- Catalog publication: `publish` → CDS index update.

### 8.4 Error Handling Tests
- Missing `context` fields → `400 NackBadRequest`.
- Unsupported `context.version` → `400 NackBadRequest`.
- Missing or invalid `Authorization` → `401 NackUnauthorized`.
- Request to non-existent item → appropriate `30xxx` error code.

### 8.5 Negative Tests
- Replay of a valid but expired request → `401`.
- Discovery query sent directly to BPP → rejection (for conformant BPPs: no `discover` endpoint).

---

## 9. Certification Process

A network or participant seeking formal Beckn v2.0.1 certification SHOULD:

1. Self-test using the open-source conformance test suite.
2. Submit test results to an accredited certification body (as defined by network governance).
3. Receive a conformance certificate tied to `subscriberId`, `role`, and `protocolVersion`.
4. Declare the certification in the DeDi registry record.

Certification is voluntary at the protocol level. Networks MAY make certification mandatory in their Network Profile.

---

## 10. References

- [24_Conformance_and_Testing.md](./24_Conformance_and_Testing.md)
- [2_Keyword_Definitions.md](./2_Keyword_Definitions.md)
- [GOVERNANCE.md](../GOVERNANCE.md) — Section 9: Specification change lifecycle
- `api/v2.0.1/beckn.yaml`

---

## 11. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | | | Initial draft |
