# Non-Repudiation, Counter-Signatures, and Message Lineage
## CWG Working Draft - 2026-03-27

# 1. Document Details
## 1.1 Version History
| Version | Date | Summary |
|---|---|---|
| Draft-01 | 2026-03-27 | Migrated to v2 RFC template structure |

## 1.2 Latest editor's draft
- ./22_Non_Repudiation_and_Lineage.md

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
  - [2. Problem](#2-problem)
  - [3. Specification (Normative)](#3-specification-normative)
    - [3.1 CounterSignature](#31-countersignature)
    - [3.2 InReplyTo](#32-inreplyto)
    - [3.3 LineageEntry](#33-lineageentry)
  - [4. Conformance Requirements](#4-conformance-requirements)
  - [5. Security Considerations](#5-security-considerations)
  - [6. References](#6-references)
  - [7. Changelog](#7-changelog)
<!-- TOC END -->

# 2. Context

**Status:** Draft  
**Author(s):**  
**Created:**  
**Updated:**  
**Conformance impact:** Minor (additive — introduces new required schemas to existing Ack and CallbackContainer)  
**Security/privacy implications:** Strengthens non-repudiation guarantees. Counter-signatures carry timestamps and identity claims that could be used to infer communication patterns.  
**Replaces / Relates to:** New in v2.0.0. Formalizes GitHub Issue #69.

---

## Abstract

This RFC specifies three transport schemas introduced in Beckn Protocol v2.0.0 that strengthen non-repudiation and auditability: `CounterSignature` (receiver's signed receipt returned in every `Ack`), `InReplyTo` (cryptographic binding of a callback to its originating request), and `LineageEntry` (cross-transaction causal attribution). Together, these schemas enable a complete, cryptographically verifiable audit trail for any Beckn transaction.

---

## 1. Context

In commercial transactions, both parties need proof: the sender needs proof that the message was delivered and verified by the receiver; the receiver needs proof that a callback is genuinely in response to a specific prior request; and auditors need the ability to reconstruct the causal chain of messages across a multi-step transaction.

---

## 2. Problem

The legacy pre-v2 Beckn Signature only proves who sent a message. It does not prove that the receiver received and validated it, nor does it bind callbacks to their originating requests. Without these guarantees, a party could deny receiving a message or dispute the causal relationship between messages.

---

## 3. Specification (Normative)

### 3.1 CounterSignature

A `CounterSignature` MUST be included in every `Ack` response body (HTTP 200). It is signed by the receiver and constitutes a **signed receipt** — proof that a specific signed request was received and validated.

#### Schema

```yaml
CounterSignature:
  type: object
  required: [messageId, signedBy, timestamp, signature]
  properties:
    messageId:
      type: string
      format: uuid
      description: The messageId of the request being acknowledged
    signedBy:
      type: string
      description: "{subscriberId}|{keyId}|{algorithm}" of the receiver
    timestamp:
      type: string
      format: date-time
      description: Time at which the receiver processed the request
    signature:
      type: string
      description: Base64(Ed25519_sign(counterSigningString, receiverPrivateKey))
```

#### Counter-Signing String

```
messageId: {messageId}
signedBy: {subscriberId}|{keyId}|{algorithm}
timestamp: {ISO8601timestamp}
digest: BLAKE-512={Base64(BLAKE2b-512(originalRequestBody))}
```

#### Example

```json
{
  "status": "ACK",
  "counterSignature": {
    "messageId": "a2fe6d52-9fe4-4d1a-9d0b-dccb8b48522d",
    "signedBy": "bpp.example.com|key-001|ed25519",
    "timestamp": "2026-01-04T09:17:56.100Z",
    "signature": "Base64EncodedSignatureHere=="
  }
}
```

### 3.2 InReplyTo

Every `CallbackContainer` MUST include an `inReplyTo` field that cryptographically binds the callback to the originating request.

#### Schema

```yaml
InReplyTo:
  type: object
  required: [messageId, requestDigest, signature]
  properties:
    messageId:
      type: string
      format: uuid
      description: messageId of the originating RequestContainer
    requestDigest:
      type: string
      description: BLAKE-512={Base64(BLAKE2b-512(originalRequestBody))}
    timestamp:
      type: string
      format: date-time
      description: Timestamp from the original request Context
    signature:
      type: string
      description: Base64(Ed25519_sign(inReplyToSigningString, callbackSenderPrivateKey))
```

#### InReplyTo Signing String

```
messageId: {original messageId}
requestDigest: BLAKE-512={digest of original request body}
timestamp: {original request context.timestamp}
```

#### Example

```json
{
  "context": { "action": "on_discover", ... },
  "message": { ... },
  "inReplyTo": {
    "messageId": "a2fe6d52-9fe4-4d1a-9d0b-dccb8b48522d",
    "requestDigest": "BLAKE-512=b6lf6lRgOw...",
    "timestamp": "2026-01-04T09:17:55.971Z",
    "signature": "Base64EncodedSignatureHere=="
  }
}
```

### 3.3 LineageEntry

A `LineageEntry` records a causal attribution between two messages in different transactions. It is used when a message in transaction B is causally triggered by a message in transaction A.

#### Schema

```yaml
LineageEntry:
  type: object
  required: [causeMessageId, causeTransactionId, relationship]
  properties:
    causeMessageId:
      type: string
      format: uuid
      description: messageId of the causal message
    causeTransactionId:
      type: string
      format: uuid
      description: transactionId of the causal transaction
    relationship:
      type: string
      description: Semantic relationship (e.g., "fulfillment-update-of", "cancellation-of")
    signature:
      type: string
      description: Optional — Base64 signature of the lineage entry by the asserting party
```

#### Example

```json
{
  "context": { "action": "on_status", "transactionId": "new-txn-uuid", ... },
  "message": { ... },
  "lineage": [
    {
      "causeMessageId": "a2fe6d52-9fe4-4d1a-9d0b-dccb8b48522d",
      "causeTransactionId": "e6d9f908-1d26-4ff3-a6d1-3af3d3721054",
      "relationship": "fulfillment-update-of"
    }
  ]
}
```

---

## 4. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-014-01 | Every `Ack` (HTTP 200) MUST include a valid `CounterSignature` | MUST |
| CON-014-02 | `CounterSignature.messageId` MUST match the `messageId` of the acknowledged request | MUST |
| CON-014-03 | Every `CallbackContainer` MUST include a valid `InReplyTo` | MUST |
| CON-014-04 | `InReplyTo.messageId` MUST match the `messageId` of the originating request | MUST |
| CON-014-05 | Receivers SHOULD verify `InReplyTo.signature` to confirm callback authenticity | SHOULD |
| CON-014-06 | `LineageEntry` SHOULD be included when a message causally follows a prior transaction | SHOULD |

---

## 5. Security Considerations

- `CounterSignature` creates non-repudiable delivery receipts. Senders SHOULD store received counter-signatures as audit evidence.
- `InReplyTo` prevents callback injection — a malicious party cannot forge a callback without the original request digest.
- `LineageEntry` signatures are optional but SHOULD be used when causal attribution is asserted as a contractual claim.

---

## 6. References

- `api/v2.0.0/beckn.yaml` — authoritative schema definitions
- [05_Signing_Beckn_APIs_in_HTTP.md](./05_Signing_Beckn_APIs_in_HTTP.md)
- GitHub Issue #69

---

## 7. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | | | Initial draft |
