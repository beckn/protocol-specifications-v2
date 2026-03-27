# DeDi-Compliant Network Registry
## CWG Working Draft - 2026-03-27

# 1. Document Details
## 1.1 Version History
| Version | Date | Summary |
|---|---|---|
| Draft-01 | 2026-03-27 | Migrated to v2 RFC template structure |

## 1.2 Latest editor's draft
- ./08_DeDi_Registry_Integration.md

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
- https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%22RFC-011%22

### 1.7.2 Discussions
- https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22RFC-011%22

### 1.7.3 Pull Requests
- https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22RFC-011%22

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
    - [2.1 DeDi Compliance Requirement](#21-dedi-compliance-requirement)
    - [2.2 Participant Record](#22-participant-record)
    - [2.3 Subscribe (Registration)](#23-subscribe-registration)
    - [2.4 Lookup (Key Resolution)](#24-lookup-key-resolution)
    - [2.5 Key Rotation](#25-key-rotation)
    - [2.6 Unsubscribe](#26-unsubscribe)
    - [2.7 Integration with Beckn Authentication](#27-integration-with-beckn-authentication)
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
**Conformance impact:** Major (replaces bespoke Beckn registry with DeDi-compliant registry)  
**Security/privacy implications:** The registry is publicly accessible. Participant public keys and endpoints are publicly visible by design. Private keys MUST never be stored in the registry.  
**Replaces / Relates to:** Replaces bespoke Beckn legacy pre-v2 `lookup`/`subscribe` registry. Aligns with the [DeDi protocol](https://dedi.global).

---

## Abstract

This RFC defines how Beckn Protocol v2 uses a DeDi-compliant directory as its Network Registry. It specifies the participant record format, the required DeDi operations (subscribe, lookup, unsubscribe), and the integration points with the Beckn authentication flow.

---

## 1. Context

A Beckn network requires a shared, publicly accessible directory of participant identities, signing keys, and endpoints. In legacy pre-v2, this was a bespoke Beckn registry with custom `lookup` and `subscribe` APIs. In v2, the registry is aligned with the [Decentralized Directory (DeDi) protocol](https://dedi.global), enabling cross-ecosystem discoverability and a shared trust layer.

---

## 2. Specification (Normative)

### 2.1 DeDi Compliance Requirement

A Beckn v2 Network Registry MUST be compliant with the DeDi protocol. It MUST expose the standard DeDi APIs for participant registration, key publication, and lookup.

### 2.2 Participant Record

Each Beckn Network Participant MUST have a record in the DeDi registry with the following fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `subscriberId` | string | MUST | Unique identifier (typically FQDN) |
| `subscriberUrl` | string (URI) | MUST | HTTPS endpoint implementing `/discover, /on_discover, /select, /on_select, and related action endpoints` |
| `role` | string enum | MUST | `BAP`, `BPP`, `PS`, `DS` |
| `domain` | string array | MUST | Supported interaction domains |
| `networkId` | string | MUST | Network identifier |
| `signingPublicKey` | string (Base64) | MUST | Ed25519 public key for signature verification |
| `encryptionPublicKey` | string (Base64) | SHOULD | Public key for message encryption (if applicable) |
| `keyId` | string (UUID) | MUST | Unique key identifier used in `Authorization` header |
| `validFrom` | string (ISO 8601) | MUST | Key validity start |
| `validUntil` | string (ISO 8601) | MUST | Key validity end |
| `status` | string enum | MUST | `SUBSCRIBED`, `INITIATED`, `UNDER_SUBSCRIPTION`, `UNSUBSCRIBED`, `SUSPENDED` |
| `created` | string (ISO 8601) | MUST | Record creation timestamp |
| `updated` | string (ISO 8601) | MUST | Last update timestamp |

### 2.3 Subscribe (Registration)

A new participant registers by:

1. Generating an Ed25519 key pair.
2. Constructing a participant record as defined in 2.2.
3. Signing the record with the new private key.
4. Submitting the signed record to the registry's `subscribe` endpoint.

The registry MUST verify the signature and, if valid, store the record and return a confirmation.

The registry MUST set `status = SUBSCRIBED` upon successful registration.

### 2.4 Lookup (Key Resolution)

Any party can resolve a participant record:

```
GET {registryUrl}/dedi/lookup?subscriberId={id}&keyId={keyId}
```

Response:
```json
{
  "subscriberId": "bpp.example.com",
  "subscriberUrl": "https://bpp.example.com",
  "role": "BPP",
  "signingPublicKey": "Base64EncodedPublicKey==",
  "keyId": "ae3ea24b-cfec-495e-81f8-044aaef164ac",
  "validFrom": "2026-01-01T00:00:00Z",
  "validUntil": "2027-01-01T00:00:00Z",
  "status": "SUBSCRIBED"
}
```

The registry MUST return a 404 if no valid record is found for the given `subscriberId` and `keyId`.

The registry MUST return a 410 (Gone) or equivalent if the key has been revoked or the participant is suspended.

### 2.5 Key Rotation

To rotate a signing key:

1. Generate a new Ed25519 key pair.
2. Submit a new key record with a new `keyId` via `subscribe` or a key-update endpoint.
3. The old key MUST remain valid until its `validUntil` timestamp or until all in-flight requests signed with it have expired (whichever is later).
4. Participants SHOULD cache old keys for the maximum TTL of any in-flight request.

### 2.6 Unsubscribe

A participant removes itself by submitting an authenticated `unsubscribe` request. The registry MUST:
- Set `status = UNSUBSCRIBED`.
- Retain the record for audit purposes.
- Return 404 or 410 for subsequent lookup requests for that `subscriberId`.

### 2.7 Integration with Beckn Authentication

The DeDi registry lookup is a mandatory step in the Beckn signature verification flow:

```
Receive request
→ Parse Authorization header → extract subscriberId, keyId, algorithm
→ DeDi lookup(subscriberId, keyId) → signingPublicKey
→ Verify Ed25519 signature using signingPublicKey
→ Accept or reject
```

Participants SHOULD cache lookup results for the duration of `validUntil - now` to minimize registry load.

---

## 3. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-018-01 | Registry MUST be DeDi-protocol compliant | MUST |
| CON-018-02 | Registry MUST expose subscribe, lookup, and unsubscribe operations | MUST |
| CON-018-03 | Participant records MUST include all required fields from Section 2.2 | MUST |
| CON-018-04 | Registry MUST return `signingPublicKey` for valid lookup requests | MUST |
| CON-018-05 | Registry MUST reject lookup of revoked/suspended keys | MUST |
| CON-018-06 | All participants MUST be registered in the DeDi registry | MUST |
| CON-018-07 | Participants SHOULD cache lookup results for the key validity duration | SHOULD |
| CON-018-08 | Old keys MUST remain resolvable until their `validUntil` timestamp | MUST |

---

## 4. Security Considerations

- The registry is publicly accessible. This is intentional — public verifiability is a core DeDi property.
- Private keys MUST NEVER be submitted to or stored in the registry.
- Participants MUST rotate keys immediately upon suspected private key compromise.
- Registry implementations SHOULD rate-limit lookup requests to prevent DoS.
- Registry records SHOULD be signed by the registry operator for external verifiability.

---

## 5. References

- [DeDi protocol](https://dedi.global)
- [07_Registry_and_Identity.md](./07_Registry_and_Identity.md)
- [13_Authentication_and_Security.md](./13_Authentication_and_Security.md)
- [14_Signing_Beckn_APIs_in_HTTP.md](./14_Signing_Beckn_APIs_in_HTTP.md)

---

## 6. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | | | Initial draft |
