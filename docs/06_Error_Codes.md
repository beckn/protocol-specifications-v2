# Error Codes and Error Handling
## CWG Working Draft - 2026-03-27

# 1. Document Details
## 1.1 Version History
| Version | Date | Summary |
|---|---|---|
| Draft-01 | 2026-03-27 | Migrated to v2 RFC template structure |

## 1.2 Latest editor's draft
- ./06_Error_Codes.md

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
  - [1. Transport-Level Errors](#1-transport-level-errors)
  - [2. Application-Level Error Object](#2-application-level-error-object)
  - [3. Application-Level Error Code Registry](#3-application-level-error-code-registry)
    - [3.1 Request Errors (3xxxx)](#31-request-errors-3xxxx)
    - [3.2 Business Errors (4xxxx)](#32-business-errors-4xxxx)
    - [3.3 Policy Errors (5xxxx)](#33-policy-errors-5xxxx)
    - [3.4 Transport / Authentication Errors (6xxxx)](#34-transport-authentication-errors-6xxxx)
  - [4. AsyncError](#4-asyncerror)
  - [5. Conformance Requirements](#5-conformance-requirements)
  - [6. Changes from legacy pre-v2 (BECKN-005)](#6-changes-from-legacy-pre-v2-beckn-005)
  - [7. References](#7-references)
  - [8. Changelog](#8-changelog)
<!-- TOC END -->

# 2. Context

**Status:** Draft  
**Author(s):** Ravi Prakash (Beckn Foundation)  
**Created:** 2022-01-21  
**Updated:** 2026-02-01  
**Conformance impact:** Minor (extends transport error model with application-level codes)  
**Security/privacy implications:** Error messages MUST NOT expose internal system details, stack traces, or sensitive data.  
**Replaces / Relates to:** Supersedes BECKN-005 (legacy pre-v2). Transport-level errors are now defined in `beckn.yaml`; this RFC defines the application-level error code taxonomy.

---

## Abstract

This RFC defines the error code taxonomy for Beckn Protocol v2. It covers two layers: (1) transport-level errors, expressed via `NackBadRequest`, `NackUnauthorized`, and `ServerError` schemas defined in `beckn.yaml`; and (2) application-level error codes, expressed via the `Error` object inside those transport schemas. It supersedes the BECKN-005 legacy pre-v2 error code table.

---

## 1. Transport-Level Errors

Transport-level errors are returned as HTTP response schemas and are defined in `api/v2.0.0/beckn.yaml`.

| HTTP Code | Schema | When to Use |
|---|---|---|
| `200` | `Ack` | Request received and validated successfully |
| `409` | `AckNoCallback` | Received but no callback will follow (business constraint) |
| `400` | `NackBadRequest` | Request is malformed, schema-invalid, or missing required fields |
| `401` | `NackUnauthorized` | Invalid, expired, or missing Beckn Signature |
| `500` | `ServerError` | Internal server error on the receiver's platform |

---

## 2. Application-Level Error Object

When returning `NackBadRequest`, `AckNoCallback`, or `ServerError`, the response body MUST include an `Error` object:

```json
{
  "error": {
    "code": "30004",
    "message": "Item not found",
    "path": "message.order.items[0].id"
  }
}
```

| Field | Description |
|---|---|
| `code` | Machine-readable error code (see Section 3) |
| `message` | Human-readable description. MUST NOT contain sensitive data. |
| `path` | (Optional) JSON path to the field that caused the error |

---

## 3. Application-Level Error Code Registry

### 3.1 Request Errors (3xxxx)

| Code | Name | Description |
|---|---|---|
| `30000` | Invalid request | Generic invalid request error |
| `30001` | Provider not found | BPP cannot find the `provider.id` sent by BAP |
| `30002` | Provider location not found | BPP cannot find the `provider.location.id` |
| `30003` | Provider category not found | BPP cannot find the `provider.category.id` |
| `30004` | Item not found | BPP cannot find the `item.id` |
| `30005` | Category not found | BPP cannot find the `category.id` |
| `30006` | Offer not found | BPP cannot find the `offer.id` |
| `30007` | Fulfillment unavailable | BPP cannot find or fulfill the `fulfillment.id` |
| `30008` | Order not found | BPP cannot find the `order.id` |
| `30009` | Invalid cancellation reason | BPP cannot find or accept the `cancellationReasonId` |
| `30010` | Invalid update target | BPP cannot process the requested `updateTarget` |
| `30011` | Entity to rate not found | BPP cannot find the entity referenced in the `rate` request |
| `30012` | Invalid rate value | BPP received an invalid value in the `rate` request |

### 3.2 Business Errors (4xxxx)

| Code | Name | Description |
|---|---|---|
| `40000` | Business error | Generic business logic error |
| `40001` | Action not applicable | The called action is not implemented or not applicable to this BPP |
| `40002` | Item quantity unavailable | Requested quantity is not available |
| `40003` | Quote unavailable | The quoted price is no longer valid |
| `40004` | Payment not supported | The payment method sent by BAP is not accepted by BPP |
| `40005` | Tracking not supported | BPP does not support tracking for this order |
| `40006` | Fulfillment agent unavailable | No agent available to fulfill the order |
| `40007` | Schema pack not supported | BPP does not support the schema pack declared in `@context` |

### 3.3 Policy Errors (5xxxx)

| Code | Name | Description |
|---|---|---|
| `50000` | Policy error | Generic policy violation error |
| `50001` | Cancellation not possible | BPP cannot cancel the order per its cancellation policy |
| `50002` | Update not possible | BPP cannot update the order per its update policy |
| `50003` | Unsupported rate category | BPP does not support the rate category sent |
| `50004` | Support unavailable | BPP does not provide support for the referenced entity |
| `50005` | Domain not supported | BPP does not operate in the domain specified in `context.domain` |
| `50006` | Version not supported | BPP does not support the `context.version` value |

### 3.4 Transport / Authentication Errors (6xxxx)

These are surfaced via `NackUnauthorized` or `NackBadRequest`:

| Code | Name | Description |
|---|---|---|
| `60000` | Authentication error | Generic authentication failure |
| `60001` | Invalid signature | Beckn Signature verification failed |
| `60002` | Expired signature | Signature `expires` timestamp is in the past |
| `60003` | Key not found | No valid key found in registry for the `keyId` |
| `60004` | Algorithm mismatch | `keyId` algorithm does not match `algorithm` field |
| `60005` | Context schema error | `Context` object is missing required fields or has invalid values |

---

## 4. AsyncError

When an error occurs during asynchronous processing and must be communicated via a `CallbackContainer`, the `message` field SHOULD contain an `AsyncError` object:

```json
{
  "context": { "action": "on_confirm", ... },
  "message": {
    "@type": "AsyncError",
    "error": {
      "code": "40002",
      "message": "Item quantity unavailable"
    }
  },
  "inReplyTo": { ... }
}
```

---

## 5. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-021-01 | Error responses MUST use the transport schema (`NackBadRequest`, `NackUnauthorized`, `ServerError`) | MUST |
| CON-021-02 | Error responses MUST include an `Error` object with a `code` field | MUST |
| CON-021-03 | Error `message` MUST NOT expose internal implementation details | MUST |
| CON-021-04 | Async errors MUST be communicated via `CallbackContainer` with `AsyncError` | MUST |

---

## 6. Changes from legacy pre-v2 (BECKN-005)

| Aspect | legacy pre-v2 | v2.0.x |
|---|---|---|
| Transport error schemas | Single `Nack` | Typed: `NackBadRequest`, `NackUnauthorized`, `ServerError`, `AckNoCallback` |
| Error code range | `30000`–`50004` | Extended to include `40007`, `50005`, `50006`, `6xxxx` range |
| Async error delivery | Not specified | Via `CallbackContainer` with `AsyncError` |

---

## 7. References

- `api/v2.0.0/beckn.yaml` — `NackBadRequest`, `NackUnauthorized`, `ServerError`, `Error`, `AsyncError` schemas
- [03_Core_API_Envelope.md](./03_Core_API_Envelope.md)

---

## 8. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | 2022-01-21 | Ravi Prakash | Initial draft (BECKN-005 legacy pre-v2) |
| Draft-02 | 2026-02-01 | — | v2 update: extended error code registry, added 6xxxx range, added AsyncError |
