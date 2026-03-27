# Communication Protocol

**Status:** Informative  
**Applies to:** Beckn Protocol v2.0.x (current LTS: v2.0.1)

---

## 1. Overview

All communication on a Beckn v2 network is:

1. **Server-to-server** — no client application is involved in the protocol layer. The consumer-facing UI is entirely decoupled from the protocol session.
2. **Asynchronous** — a sender receives an immediate `Ack` (synchronous receipt confirmation), and the actual response arrives later as a separate callback API call.
3. **Digitally signed** — every request and callback carries a Beckn Signature in the `Authorization` header, binding the message to the sender's registered identity.

---

## 2. The Universal Endpoint

Beckn v2.0.1 defines a single universal endpoint that handles all actions across all interaction domains:

```
GET  /beckn/{becknEndpoint}
POST /beckn/{becknEndpoint}
```

The `{becknEndpoint}` path parameter follows the pattern `beckn/<action>`, for example:
- `beckn/search`
- `beckn/confirm`
- `beckn/publish`
- `beckn/discover`

Any Beckn Network Participant — BAP, BPP, CDS, CPS, or Registry — implements this endpoint, selectively supporting the subset of actions relevant to their role.

---

## 3. Request Modes

### 3.1 POST — Forward Request or Callback

**POST** handles both:
- **Forward requests**: `RequestContainer` sent by BAP → BPP/CDS/CPS
- **Callbacks**: `CallbackContainer` sent by BPP → BAP (includes `inReplyTo` binding)

The `Content-Type` is always `application/json`. The Beckn Signature is in the `Authorization` header.

```
POST /beckn/confirm
Authorization: Signature keyId="bap.example.com|key-001|ed25519",...
Content-Type: application/json

{
  "context": { ... },
  "message": { ... }
}
```

### 3.2 GET — Body Mode

The action payload is sent as a JSON request body; the Beckn Signature is in the `Authorization` header. Used for server-to-server interactions where the caller has a registered callback endpoint and expects an asynchronous response.

```
GET /beckn/search
Authorization: Signature keyId="bap.example.com|key-001|ed25519",...
Content-Type: application/json

{
  "context": { ... },
  "message": { ... }
}
```

### 3.3 GET — Query Mode

The entire request — payload and signature — is encoded as URL query parameters, producing a **self-contained URL**:

```
GET /beckn/search?Authorization={Signature}&RequestAction={RequestActionQuery}
```

**Use cases:** QR codes, deep links, bookmarkable pages, frontend UIs, IoT/embedded clients, any context where an HTTP request body cannot be sent.

**Important constraints:**
- In Query Mode, the caller MUST NOT expect an asynchronous callback. The server acknowledges with `Ack` (HTTP 200) only.
- Body Mode and Query Mode are **mutually exclusive**. If query parameters are present, the request body and `Authorization` header MUST be absent, and vice versa.

---

## 4. Message Envelopes

### 4.1 RequestContainer

Used for all forward requests (BAP → BPP, BAP → CDS, BPP → CPS).

```json
{
  "context": {
    "domain": "beckn:retail",
    "action": "search",
    "version": "2.0.1",
    "bapId": "bap.example.com",
    "bapUri": "https://bap.example.com",
    "bppId": "bpp.example.com",
    "bppUri": "https://bpp.example.com",
    "transactionId": "txn-uuid",
    "messageId": "msg-uuid",
    "timestamp": "2026-01-01T00:00:00Z",
    "ttl": "PT30S"
  },
  "message": { }
}
```

### 4.2 CallbackContainer

Used for all callbacks (BPP → BAP). Includes `inReplyTo` for cryptographic binding to the originating request.

```json
{
  "context": { ... },
  "message": { },
  "inReplyTo": {
    "messageId": "msg-uuid-of-original-request",
    "signature": "...",
    "timestamp": "..."
  }
}
```

---

## 5. Asynchronous Communication Lifecycle

```
Sender                               Receiver
  │                                      │
  │── POST /beckn/search ───────────────►│
  │◄── 200 Ack ─────────────────────────│  (same session, immediate)
  │                                      │
  │       ... receiver processes ...     │
  │                                      │
  │◄── POST /beckn/on_search ───────────│  (separate session, callback)
  │── 200 Ack ──────────────────────────►│
  │                                      │
```

Key points:
- The `Ack` in the first session only confirms receipt and signature validity.
- The actual response data arrives in the callback session.
- The callback name is the action name prefixed with `on_` (e.g., `search` → `on_search`).
- The `inReplyTo` field in the `CallbackContainer` cryptographically binds the callback to the originating request.

---

## 6. Context Fields

The `Context` object is mandatory on every request and callback. Key fields:

| Field | Description |
|---|---|
| `domain` | The interaction domain (e.g., `beckn:retail`, `beckn:mobility`) |
| `action` | The action name (e.g., `search`, `confirm`) |
| `version` | Protocol version (e.g., `2.0.1`) |
| `bapId` | Subscriber ID of the BAP |
| `bapUri` | Callback endpoint URI of the BAP |
| `bppId` | Subscriber ID of the BPP (omitted in multicast scenarios) |
| `bppUri` | Endpoint URI of the BPP |
| `transactionId` | UUID identifying the full transaction lifecycle |
| `messageId` | UUID identifying this specific message |
| `timestamp` | ISO 8601 timestamp of message creation |
| `ttl` | ISO 8601 duration — how long this message is valid |

---

## 7. Response Semantics

| HTTP Code | Schema | Meaning |
|---|---|---|
| `200` | `Ack` | Receipt confirmed; signature valid; async callback will follow |
| `409` | `AckNoCallback` | Received but no callback will be sent (business constraint) |
| `400` | `NackBadRequest` | Malformed or invalid request |
| `401` | `NackUnauthorized` | Invalid or missing authentication |
| `500` | `ServerError` | Internal error on the participant's platform |

---

## 8. Comparison with v1.x Communication

| Aspect | v1.x | v2.0.x |
|---|---|---|
| Discovery routing | BAP → BG → (multicast) → BPPs | BAP → CDS (index-based) |
| Transaction routing | BAP → BG → BPP | BAP → BPP (direct) |
| BG signature | `X-Gateway-Authorization` header required | No BG; header removed |
| Endpoint model | Per-action endpoints | Universal `/beckn/{becknEndpoint}` |
| GET support | Not defined | GET Body Mode + GET Query Mode |

---

## 9. Further Reading

- [9_Authentication_and_Security.md](./9_Authentication_and_Security.md) — Beckn Signature construction
- [10_Signing_Beckn_APIs_in_HTTP.md](./10_Signing_Beckn_APIs_in_HTTP.md) — Step-by-step signing guide
- [17_Non_Repudiation_and_Lineage.md](./17_Non_Repudiation_and_Lineage.md) — `CounterSignature`, `InReplyTo`, `LineageEntry`
- [19_Get_Query_Mode.md](./19_Get_Query_Mode.md) — GET Query Mode specification
- `api/v2.0.1/beckn.yaml` — authoritative transport schema definitions
