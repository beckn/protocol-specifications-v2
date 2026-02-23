# Beckn Protocol API — v2.0.1

**Status**: LTS (Long Term Support)  
**Spec file**: [`beckn.yaml`](./beckn.yaml)  
**OpenAPI version**: 3.1.1  
**License**: [CC-BY-NC-SA 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)

---

## Overview

`beckn.yaml` defines the **universal API transport envelope** for Beckn Protocol v2.0.1. It specifies a single endpoint — `/beckn/{becknEndpoint}` — that handles all Beckn protocol actions across all interaction domains.

This spec is intentionally **minimal by design**. It defines the message transport envelope and authentication contract only. The semantics of specific actions (`search`, `select`, `init`, `confirm`, etc.) and the schemas for their payloads are defined in the [**beckn/core_schema**](https://github.com/beckn/core_schema) repository.

Full documentation — including Design Principles, API modes, authentication, response semantics, and architecture — is in the [**root README**](../../README.md).

---

## Quick Reference

| Topic | Section in root README |
|-------|----------------------|
| Design Principles (No Schema Folder, Mandatory Fields, Container vs Payload) | [Design Principles](../../README.md#design-principles) |
| Endpoint, GET Body Mode, GET Query Mode, POST | [Section 3.1](../../README.md#31-v201-universal-beckn-becknendpoint-endpoint) |
| Authentication (Signature format) | [Section 3.1 — Authentication](../../README.md#authentication) |
| Response semantics (Ack, Nack, AckNoCallback) | [Section 3.1 — Response semantics](../../README.md#response-semantics) |
| Schema distribution model | [Section 2.2](../../README.md#22-schema-distribution-model) |
| Version history & EoS announcement | [Version History](../../README.md#version-history) |

---

## Transport Schemas (inline in `beckn.yaml`)

All transport-level schemas are defined directly in `beckn.yaml` — no external `$ref` to `schema.beckn.io`:

| Schema | Purpose |
|--------|---------|
| `BecknEndpoint` | Path parameter type — pattern-validated endpoint identifier |
| `Context` | Mandatory transaction context (BAP/BPP IDs, messageId, transactionId, timestamp, etc.) |
| `RequestContainer` | Envelope for forward actions (BAP → BPP/CDS/CPS) |
| `CallbackContainer` | Envelope for async callbacks (BPP → BAP), includes `inReplyTo` |
| `Message` | Open container for the domain payload (`additionalProperties: true`) |
| `Signature` | HTTP Signature credential (`Authorization` header format, Ed25519) |
| `CounterSignature` | Signed receipt in `Ack` response body — proves receipt (Issue #69) |
| `InReplyTo` | Cryptographic request–response binding in callbacks (Issue #69) |
| `LineageEntry` | Cross-transaction causal attribution record (Issue #69) |
| `Ack` | `200` — receipt confirmed, async callback will follow |
| `AckNoCallback` | `409` — received but no callback will follow |
| `NackBadRequest` | `400` — malformed or invalid request |
| `NackUnauthorized` | `401` — invalid or missing authentication |
| `ServerError` | `500` — internal error on the participant's platform |
| `Error` | Base error container |
| `AsyncError` | Error returned inside a `CallbackContainer` |

---

## Related

- [Beckn Protocol v2 — Full Documentation](../../README.md)
- [Beckn core schema](https://github.com/beckn/core_schema)
- [Beckn schema registry](https://schema.beckn.io)
- [DeDi protocol](https://dedi.global)
