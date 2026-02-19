# Beckn Protocol API — v2.0.1

**Status**: LTS (Long Term Support)  
**Spec file**: [`beckn.yaml`](./beckn.yaml)  
**OpenAPI version**: 3.1.1  
**License**: [CC-BY-NC-SA 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)

---

## Overview

`beckn.yaml` defines the **universal API envelope** for Beckn Protocol v2. It specifies a single endpoint — `/beckn/{action}` — that handles all Beckn protocol actions across all interaction domains (Discovery, Ordering, Fulfillment, Post-Fulfillment, and future domains).

This spec is intentionally **minimal by design**. It defines the message transport envelope and authentication contract only. The semantics of specific actions (`search`, `select`, `init`, `confirm`, etc.) and the schemas for their payloads are defined in the [**beckn/core_schema**](https://github.com/beckn/core_schema) repository, which is referenced via `$ref` throughout this file.

---

## Endpoint

```
GET  /beckn/{action}
POST /beckn/{action}
```

The `{action}` path parameter identifies the specific Beckn protocol operation being performed. Any Beckn Network Participant — BAP, BPP, Catalog Discovery Service (CDS), Catalog Publishing Service (CPS), or Registry — may implement this endpoint, selectively supporting the subset of actions relevant to their role.

---

## Modes

### POST — Standard server-to-server mode

Handles both forward actions and callbacks:

- **`RequestAction`** — originated by a BAP directed at a BPP, CDS, or CPS.
- **`CallbackAction`** — originated by a BPP or CPS directed back at a BAP.

All POST requests MUST be authenticated using a Beckn Signature transmitted in the `Authorization` header. The receiver validates the signature against the sender's public key resolved from the Beckn Registry (DeDi-compliant).

### GET — Body Mode

The action payload is sent as a JSON request body; the signature is transmitted in the `Authorization` header. Used for server-to-server interactions where the caller has a registered callback endpoint, similar to POST.

### GET — Query Mode

The action payload and signature are both expressed as URL query parameters:

```
GET /beckn/{action}?Authorization={Signature}&RequestAction={RequestActionQuery}
```

Query Mode makes the entire request a **self-contained URL** — suitable for:
- QR codes
- Deep links
- Bookmarkable pages
- Frontend UIs and single-page applications
- IoT and embedded clients
- Browser-triggered interactions

> **Important**: In Query Mode, the caller MUST NOT expect an asynchronous callback. The server acknowledges receipt with `Ack` (HTTP 200) but will not send a callback to the caller. Query Mode is designed for stateless, one-way interactions where the originating client has no registered callback endpoint.

The two modes (Body Mode and Query Mode) are mutually exclusive. If `Authorization` and `RequestAction` are present as query parameters, the request body MUST be absent and the `Authorization` header MUST be absent.

---

## Response Semantics

| HTTP Code | Schema | Meaning |
|-----------|--------|---------|
| `200` | `Ack` | Receipt confirmed; signature valid; asynchronous callback will follow |
| `409` | `AckNoCallback` | Received but no callback will follow (e.g. agents not found, inventory unavailable) |
| `400` | `NackBadRequest` | Malformed or invalid request |
| `401` | `NackUnauthorized` | Invalid or missing authentication credentials |
| `500` | `ServerError` | Internal failure on the network participant's platform |

---

## Schema References

All schema types used in this spec are externalized and resolved at runtime:

| Schema | Source |
|--------|--------|
| `Action` | `https://schema.beckn.io/Action/ref` |
| `Signature` | `https://schema.beckn.io/Signature/ref` |
| `RequestAction` | `https://schema.beckn.io/RequestAction/ref` |
| `RequestActionQuery` | `https://schema.beckn.io/RequestActionQuery/ref` |
| `CallbackAction` | `https://schema.beckn.io/CallbackAction/ref` |
| `Ack` | `https://schema.beckn.io/Ack/ref` |
| `AckNoCallback` | `https://schema.beckn.io/AckNoCallback/ref` |
| `NackBadRequest` | `https://schema.beckn.io/NackBadRequest/ref` |
| `NackUnauthorized` | `https://schema.beckn.io/NackUnauthorized/ref` |
| `ServerError` | `https://schema.beckn.io/ServerError/ref` |

Full OWL definitions, JSON-LD annotations, and examples for these types are maintained in the [**beckn/core_schema**](https://github.com/beckn/core_schema) repository.

---

## Authentication

All requests (except GET Query Mode) MUST carry a Beckn Signature in the `Authorization` header:

```
Authorization: Signature keyId="{subscriber_id}|{key_id}|{algorithm}",algorithm="{algorithm}",created="{created}",expires="{expires}",headers="(created) (expires) digest",signature="{base64_signature}"
```

The receiver resolves the sender's public key from the Beckn Registry ([DeDi](https://dedi.global)-compliant) using the `keyId` field and validates the signature before processing the request.

---

## Related

- [Beckn Protocol v2 — Main README](../../README.md)
- [Beckn core schema](https://github.com/beckn/core_schema)
- [Beckn schema registry](https://schema.beckn.io)
- [DeDi protocol](https://dedi.global)
