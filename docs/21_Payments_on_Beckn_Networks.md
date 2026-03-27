# Payments on Beckn-Enabled Networks
## CWG Working Draft - 2026-03-27

# 1. Document Details
## 1.1 Version History
| Version | Date | Summary |
|---|---|---|
| Draft-01 | 2026-03-27 | Migrated to v2 RFC template structure |

## 1.2 Latest editor's draft
- ./21_Payments_on_Beckn_Networks.md

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
  - [2. Design Principles](#2-design-principles)
  - [3. Payment Roles](#3-payment-roles)
  - [4. Payment Contract Agreement](#4-payment-contract-agreement)
  - [5. Payment Object](#5-payment-object)
  - [6. Payment Flows](#6-payment-flows)
    - [Flow 1: BAP Collects Payment](#flow-1-bap-collects-payment)
    - [Flow 2: BPP Collects Payment](#flow-2-bpp-collects-payment)
  - [7. Payment Object Examples](#7-payment-object-examples)
    - [Example 1 — BAP Collects, Settles POST-FULFILLMENT via Bank Transfer](#example-1-bap-collects-settles-post-fulfillment-via-bank-transfer)
    - [Example 2 — BPP Collects via UPI, ON-ORDER](#example-2-bpp-collects-via-upi-on-order)
    - [Example 3 — BPP Collects via Payment Gateway](#example-3-bpp-collects-via-payment-gateway)
  - [8. Changes from legacy pre-v2 (BECKN-002)](#8-changes-from-legacy-pre-v2-beckn-002)
  - [9. Conformance Requirements](#9-conformance-requirements)
  - [10. References](#10-references)
  - [11. Changelog](#11-changelog)
<!-- TOC END -->

# 2. Context

**Status:** Draft  
**Author(s):** Ravi Prakash (Beckn Foundation)  
**Created:** 2021-12-10  
**Updated:** 2026-02-01  
**Conformance impact:** Informative for core; normative for network payment policy  
**Security/privacy implications:** Payment endpoints and terms are transmitted in cleartext within signed messages. Sensitive payment credentials MUST NOT be included in Beckn protocol messages.  
**Replaces / Relates to:** Adapted and updated from BECKN-002 (legacy pre-v2). Updated for v2 endpoint model and `core_schema` references.

---

## Abstract

This RFC defines how payment terms are negotiated and communicated between BAPs and BPPs on Beckn-enabled networks. Beckn protocol handles only the **Payment Contract Agreement** — the exchange and agreement of payment terms. Actual payment collection and settlement are performed outside the protocol using existing regional payment infrastructure.

---

## 1. Context

Payments are a highly regulated domain that varies significantly across geo-political regions. Beckn Protocol deliberately does not standardize payment execution — it standardizes only the communication of payment terms between a BAP and a BPP during the transaction lifecycle.

---

## 2. Design Principles

- **Out-of-band payment execution**: The actual movement of money is always performed outside the Beckn protocol using existing payment infrastructure (payment gateways, banking APIs, UPI, SEPA, etc.).
- **In-band payment terms**: The terms of payment (amount, currency, payment endpoint, timing, status) are communicated in-band using Beckn protocol messages.
- **Region-agnostic**: The `Payment` schema uses standard URI schemes (`https://`, `payto://`) to express payment endpoints across payment methods and regions.

---

## 3. Payment Roles

| Role | Description |
|---|---|
| **Payer** (BAP) | The entity that collects or arranges payment from the buyer |
| **Payee** (BPP) | The entity that receives payment for the fulfilled order |

---

## 4. Payment Contract Agreement

A Payment Contract Agreement between BAP and BPP is reached during the `init` / `on_init` exchange:

1. BAP calls `init` — includes billing details and optionally states that it will collect payment.
2. BPP responds via `on_init` — includes the `Payment` object with its terms.
3. BAP agrees to the terms by proceeding to call `confirm`.

---

## 5. Payment Object

The `Payment` object is defined in `core_schema`. Key fields:

| Field | Description |
|---|---|
| `url` | Payment endpoint URL. Supported schemes: `https://` (payment gateway), `payto://` (RFC 8905) |
| `params` | Key-value map of payment parameters: `amount`, `currency`, `ifsc`, `vpa`, etc. |
| `type` | Payment timing: `ON-ORDER`, `PRE-FULFILLMENT`, `ON-FULFILLMENT`, `POST-FULFILLMENT` |
| `status` | `NOT-PAID`, `PAID`, `PENDING` |
| `time` | For `POST-FULFILLMENT` — the deadline by which payment must be made |
| `collected_by` | `BAP` or `BPP` — which party collects the payment |

---

## 6. Payment Flows

### Flow 1: BAP Collects Payment

1. BAP informs BPP (via `init`) that it will collect the payment.
2. BPP agrees and sends settlement terms in `on_init`.
3. BAP renders payment interface to buyer; buyer pays BAP.
4. BAP settles with BPP per agreed terms.

### Flow 2: BPP Collects Payment

1. BAP informs BPP (via `init`) that it will NOT collect — BPP should provide payment details.
2. BPP sends payment endpoint and parameters in `on_init`.
3. BAP renders the BPP's payment interface to the buyer.
4. Buyer pays BPP directly.
5. BAP queries BPP for payment status via `status` / `on_status`.

---

## 7. Payment Object Examples

### Example 1 — BAP Collects, Settles POST-FULFILLMENT via Bank Transfer

```json
{
  "collected_by": "BAP",
  "url": "payto://bank/98273982749428?amount=$currency:$value&ifsc=$ifsc",
  "tl_method": "PAYTO",
  "type": "POST-FULFILLMENT",
  "status": "NOT-PAID",
  "params": {
    "ifsc": "SBIN0000575",
    "value": "200",
    "currency": "INR"
  },
  "time": {
    "range": { "end": "2026-11-30T00:00:00Z" }
  }
}
```

### Example 2 — BPP Collects via UPI, ON-ORDER

```json
{
  "url": "payto://upi/example@upi?amount=$currency:$value",
  "tl_method": "PAYTO",
  "type": "ON-ORDER",
  "status": "NOT-PAID",
  "params": {
    "value": "200",
    "currency": "INR"
  }
}
```

### Example 3 — BPP Collects via Payment Gateway

```json
{
  "url": "https://pay.example.com?amount=$value&cur=$currency",
  "tl_method": "HTTP/POST",
  "type": "ON-ORDER",
  "status": "NOT-PAID",
  "params": {
    "value": "200",
    "currency": "INR"
  }
}
```

---

## 8. Changes from legacy pre-v2 (BECKN-002)

| Aspect | legacy pre-v2 | v2.0.x |
|---|---|---|
| `Payment` schema location | Inline in `beckn.yaml` | Defined in `core_schema` |
| Payment terms exchange | During `init`/`on_init` | Same (unchanged) |
| Supported URI schemes | `https://`, `payto://` | Same (unchanged) |
| Endpoint model | `/init` | `POST /init` |
| Signature | BAP signs `init` | Same (unchanged) |

---

## 9. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-020-01 | Actual payment execution MUST be performed outside Beckn protocol | MUST |
| CON-020-02 | BPPs MUST include a `Payment` object in `on_init` responses | MUST |
| CON-020-03 | Payment endpoints MUST use `https://` or `payto://` URI schemes | MUST |
| CON-020-04 | Sensitive payment credentials MUST NOT be included in Beckn messages | MUST |
| CON-020-05 | Networks SHOULD define allowed payment types and settlement windows in their Network Profile | SHOULD |

---

## 10. References

- [RFC 8905 — The `payto` URI Scheme](https://datatracker.ietf.org/doc/html/rfc8905)
- [`beckn/core_schema`](https://github.com/beckn/core_schema) — `Payment` schema definition
- [20_Network_Policy_Profiles.md](./20_Network_Policy_Profiles.md)

---

## 11. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | 2021-12-10 | Ravi Prakash | Initial draft (BECKN-002 legacy pre-v2) |
| Draft-02 | 2026-02-01 | — | Updated for v2 endpoint model; moved Payment schema reference to core_schema |
