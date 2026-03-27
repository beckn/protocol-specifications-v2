# Authentication and Security

**Status:** Informative  
**Applies to:** Beckn Protocol v2.0.x (current LTS: v2.0.0)

---

## 1. Overview

Every request and callback on a Beckn v2 network is digitally signed by the sender. This provides:

- **Authentication** — the receiver can verify who sent the message.
- **Message integrity** — the receiver can detect if the message was altered in transit.
- **Non-repudiation** — the sender cannot later deny having sent the message.

Beckn v2 uses the **Ed25519** signature scheme and **BLAKE2b-512** hashing, consistent with legacy pre-v2. The key material is published in and resolved from the **DeDi-compliant Registry**.

---

## 2. Beckn Signature Format

All requests (except legacy GET Query mode) MUST carry a Beckn Signature in the `Authorization` header:

```
Authorization: Signature keyId="{subscriberId}|{keyId}|{algorithm}",
               algorithm="{algorithm}",
               created="{unixTimestamp}",
               expires="{unixTimestamp}",
               headers="(created) (expires) digest",
               signature="{base64EncodedSignature}"
```

### Field Descriptions

| Field | Description |
|---|---|
| `keyId` | `{subscriberId}\|{keyId}\|{algorithm}` — uniquely identifies the key in the registry |
| `algorithm` | Signing algorithm. MUST be `ed25519` |
| `created` | Unix timestamp when the signature was created |
| `expires` | Unix timestamp when the signature expires |
| `headers` | The components included in the signing string. MUST be `(created) (expires) digest` |
| `signature` | Base64-encoded Ed25519 signature of the signing string |

---

## 3. Signing Algorithm

### Step 1 — Compute the Request Body Digest

Hash the raw JSON request body using **BLAKE2b-512**:

```
digest = Base64(BLAKE2b-512(requestBody))
```

The digest is transmitted in the signing string as:

```
digest: BLAKE-512={base64digest}
```

### Step 2 — Construct the Signing String

Concatenate the three components in this exact format:

```
(created): {unixTimestamp}
(expires): {unixTimestamp}
digest: BLAKE-512={base64digest}
```

### Step 3 — Sign

Sign the signing string using the sender's Ed25519 private key:

```
signature = Base64(Ed25519_sign(signingString, privateKey))
```

### Step 4 — Compose the Authorization Header

Assemble the header as shown in Section 2.

For a complete worked example with test vectors, see [14_Signing_Beckn_APIs_in_HTTP.md](./14_Signing_Beckn_APIs_in_HTTP.md).

---

## 4. Key Resolution via DeDi Registry

When a receiver needs to verify an incoming request:

1. Extract `subscriberId`, `keyId`, and `algorithm` from the `keyId` field of the `Authorization` header.
2. If the algorithm extracted from `keyId` does not match the `algorithm` field, return `401 NackUnauthorized`.
3. Query the DeDi-compliant Registry:
   ```
   lookup(subscriberId, keyId) → { publicKey, endpoint, capabilities, ... }
   ```
4. If no valid key is found, return `401 NackUnauthorized`.
5. Use the resolved `publicKey` to verify the Ed25519 signature.
6. If verification fails, return `401 NackUnauthorized`.
7. Check that `created` is not in the future and `expires` is not in the past.

---

## 5. Non-Repudiation Schemas (v2.0.0)

v2.0.0 introduces three transport schemas that strengthen the non-repudiation guarantees of the protocol:

### 5.1 CounterSignature

A `CounterSignature` is returned inside the `Ack` response body. It is the receiver's signed receipt of the message — proof that a specific signed request was received and validated at a specific time.

```json
{
  "ack": {
    "status": "ACK",
    "counterSignature": {
      "messageId": "msg-uuid",
      "signedBy": "bpp.example.com|key-001|ed25519",
      "timestamp": "2026-01-01T00:00:00Z",
      "signature": "..."
    }
  }
}
```

### 5.2 InReplyTo

The `inReplyTo` field in a `CallbackContainer` cryptographically binds the callback to the originating request. It contains a reference to the original `messageId` and a digest of the original request, signed by the callback sender.

### 5.3 LineageEntry

A `LineageEntry` records cross-transaction causal attribution — for example, when a fulfillment update is causally linked to a prior `confirm` message. This enables auditability of multi-step transaction flows.

For the normative specification of these schemas, see [24_Non_Repudiation_and_Lineage.md](./24_Non_Repudiation_and_Lineage.md).

---

## 6. legacy GET Query mode — Signature Encoding

In legacy GET Query mode, the Beckn Signature cannot be placed in the `Authorization` header (there is no request body). Instead:

- The `Authorization` parameter encodes the Signature in the same format as the header value.
- The request action payload is encoded in the `RequestAction` query parameter.
- The signing string is constructed from the encoded `RequestAction` value instead of a body digest.

Query Mode requests MUST NOT expect callbacks. They are acknowledged with `Ack` (HTTP 200) only.

See []() for the full encoding rules.

---

## 7. Key Lifecycle

| Event | Action |
|---|---|
| Participant onboarding | Register signing key in DeDi Registry via `subscribe` |
| Key rotation | Generate new key pair; register new key; retain old key until all in-flight requests expire |
| Key revocation | Mark key as revoked in Registry; any request signed with a revoked key MUST be rejected |
| Key expiry | `expires` value in signature MUST NOT exceed the key's registered expiry time |

---

## 8. Security Considerations

- **Replay attacks**: The `created` / `expires` window limits the validity of a signature. Receivers SHOULD maintain a short-lived cache of processed `messageId` values to detect replays within the window.
- **Key compromise**: Participants MUST rotate keys immediately upon suspicion of compromise and notify the registry.
- **Transport security**: All Beckn communication MUST use HTTPS (TLS 1.2 or later). The Beckn Signature provides application-layer non-repudiation; TLS provides transport-layer confidentiality and integrity.
- **Clock skew**: Participants SHOULD allow a small clock skew tolerance (recommended: ≤ 5 seconds) when validating `created` and `expires`.

---

## 9. Further Reading

- [14_Signing_Beckn_APIs_in_HTTP.md](./14_Signing_Beckn_APIs_in_HTTP.md) — complete step-by-step signing example with test vectors
- [24_Non_Repudiation_and_Lineage.md](./24_Non_Repudiation_and_Lineage.md) — `CounterSignature`, `InReplyTo`, `LineageEntry` schemas
- [07_Registry_and_Identity.md](./07_Registry_and_Identity.md) — DeDi registry key registration and lookup
- `api/v2.0.0/beckn.yaml` — authoritative `Signature`, `CounterSignature`, `InReplyTo`, `LineageEntry` schema definitions
