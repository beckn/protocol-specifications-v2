# Beckn v2 Core API Envelope

**Status:** Draft  
**Author(s):**  
**Created:**  
**Updated:**  
**Conformance impact:** Major (defines the normative transport contract)  
**Security/privacy implications:** Defines the authentication and non-repudiation contract for all network communication.  
**Replaces / Relates to:** Supersedes all v1.x endpoint and envelope specifications.

---

## Abstract

This RFC defines the normative transport contract for Beckn Protocol v2.0.1: the universal `/beckn/{becknEndpoint}` endpoint, the three request modes (POST, GET Body Mode, GET Query Mode), all transport schemas (`Context`, `RequestContainer`, `CallbackContainer`, `Message`, `Signature`, `Ack`, `Nack`, etc.), and the response semantics. It is the normative companion document to `api/v2.0.1/beckn.yaml`.

---

## 1. Context

Beckn Protocol defines a minimal, stable transport contract that enables any two registered participants to exchange digitally signed, asynchronous messages without a shared intermediary. The transport contract must be version-stable, domain-agnostic, and composable with any schema layer above it.

---

## 2. Problem

How should the transport envelope be defined so that it is: (a) domain-agnostic, (b) self-authenticating, (c) usable from both server-side and client-side contexts (including QR codes, deep links, and IoT), and (d) stable enough to serve as a long-lived foundation for the ecosystem?

---

## 3. Specification (Normative)

### 3.1 Universal Endpoint

All Beckn v2.0.1 network participants MUST expose the following endpoint:

```
GET  /beckn/{becknEndpoint}
POST /beckn/{becknEndpoint}
```

The `{becknEndpoint}` path parameter MUST match the pattern `beckn/[a-z_]+` (e.g., `beckn/search`, `beckn/confirm`, `beckn/publish`).

### 3.2 POST — Forward Request and Callback

POST MUST be used for:
- **Forward requests** (`RequestContainer`): BAP → BPP, BAP → CDS, BPP → CPS.
- **Callbacks** (`CallbackContainer`): BPP → BAP, CDS → BAP.

The `Content-Type` MUST be `application/json`. The Beckn Signature MUST be in the `Authorization` header.

### 3.3 GET — Body Mode

GET with a JSON request body MUST be used for server-to-server requests where the caller has a registered callback endpoint. The `Authorization` header MUST be present. The request body MUST be a valid `RequestContainer`.

### 3.4 GET — Query Mode

GET with query parameters MUST be used when the caller cannot send a request body (QR codes, deep links, IoT clients). The full payload and signature are encoded as URL query parameters. In Query Mode:

- The `Authorization` header MUST be absent.
- The request body MUST be absent.
- The `Authorization` query parameter MUST contain the Beckn Signature.
- The `RequestAction` query parameter MUST contain the URL-encoded request payload.
- The server MUST NOT send a callback. It acknowledges with `Ack` (HTTP 200) only.

### 3.5 Mandatory Context Fields

Every `RequestContainer` and `CallbackContainer` MUST include a `Context` object with the following fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `domain` | string | MUST | Interaction domain |
| `action` | string | MUST | Action name |
| `version` | string | MUST | Protocol version (e.g., `2.0.1`) |
| `bapId` | string | MUST | BAP subscriber ID |
| `bapUri` | string (URI) | MUST | BAP callback endpoint |
| `bppId` | string | SHOULD | BPP subscriber ID |
| `bppUri` | string (URI) | SHOULD | BPP endpoint |
| `transactionId` | string (UUID) | MUST | Transaction lifecycle ID |
| `messageId` | string (UUID) | MUST | Message-unique ID |
| `timestamp` | string (ISO 8601) | MUST | Message creation time |
| `ttl` | string (ISO 8601 duration) | MUST | Message validity duration |

### 3.6 Message Container

The `Message` object MUST be an open container (`additionalProperties: true`). Implementations MUST NOT apply domain-specific validation to the `Message` object at the transport layer.

### 3.7 Response Semantics

| HTTP Code | Schema | Trigger |
|---|---|---|
| `200` | `Ack` | Request received, signature valid, async callback will follow |
| `409` | `AckNoCallback` | Received but no callback due to a business constraint |
| `400` | `NackBadRequest` | Malformed request, missing fields, schema validation failure |
| `401` | `NackUnauthorized` | Invalid or missing Beckn Signature |
| `500` | `ServerError` | Internal participant error |

### 3.8 Non-Repudiation

Every `Ack` response (HTTP 200) MUST include a `CounterSignature` signed by the receiver.

Every `CallbackContainer` MUST include an `inReplyTo` field binding it to the original request.

### 3.9 Transport Schema Authority

The authoritative definitions of all transport schemas (`Context`, `RequestContainer`, `CallbackContainer`, `Message`, `Signature`, `CounterSignature`, `InReplyTo`, `LineageEntry`, `Ack`, `AckNoCallback`, `NackBadRequest`, `NackUnauthorized`, `ServerError`, `Error`, `AsyncError`) are the schemas defined inline in `api/v2.0.1/beckn.yaml`. This RFC describes their intent and conformance requirements; the YAML file is the machine-verifiable authority.

---

## 4. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-012-01 | All participants MUST expose `/beckn/{becknEndpoint}` | MUST |
| CON-012-02 | POST requests MUST use `application/json` | MUST |
| CON-012-03 | Every request MUST include a valid `Context` | MUST |
| CON-012-04 | `context.version` MUST be `2.0.1` for v2.0.1 networks | MUST |
| CON-012-05 | GET Query Mode requests MUST NOT include a request body | MUST |
| CON-012-06 | GET Query Mode servers MUST NOT send callbacks | MUST |
| CON-012-07 | Every `Ack` MUST include a `CounterSignature` | MUST |
| CON-012-08 | Every `CallbackContainer` MUST include `inReplyTo` | MUST |
| CON-012-09 | `Message` MUST allow `additionalProperties` | MUST |

---

## 5. Security Considerations

All transport communication MUST use HTTPS. The Beckn Signature provides application-layer authentication and non-repudiation. The `CounterSignature` and `inReplyTo` schemas provide cryptographic proof of delivery and callback binding respectively.

---

## 6. Migration Notes

Implementations upgrading from v2.0.0 must add:
- `CounterSignature` to all `Ack` responses.
- `inReplyTo` to all `CallbackContainer` messages.
- GET Query Mode support (optional for existing server-side implementations).

---

## 7. References

- `api/v2.0.1/beckn.yaml` — authoritative transport schemas
- [3_Communication_Protocol.md](./3_Communication_Protocol.md)
- [4_Authentication_and_Security.md](./4_Authentication_and_Security.md)
- [14_Non_Repudiation_and_Lineage.md](./14_Non_Repudiation_and_Lineage.md)

---

## 8. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | | | Initial draft |
