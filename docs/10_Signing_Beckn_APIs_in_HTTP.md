# Signing Beckn APIs in HTTP

**Status:** Draft  
**Author(s):** Ravi Prakash (Beckn Foundation)  
**Created:** 2021-12-10  
**Updated:** 2026-02-01  
**Conformance impact:** Minor (v2 update of existing signing specification)  
**Security/privacy implications:** Defines the cryptographic authentication and message integrity mechanism for all Beckn network communication.  
**Replaces / Relates to:** Adapted and updated from BECKN-006 (v1.x). Removes BG-specific steps; adds DeDi key resolution and v2.0.1 non-repudiation schemas.

---

## Abstract

This RFC specifies how Beckn Network Participants authenticate themselves and ensure message integrity when communicating over HTTP. All requests and callbacks are digitally signed using Ed25519, with BLAKE2b-512 used to hash the request body. This document provides the normative algorithm, worked examples with test vectors, and receiver verification steps.

---

## 1. Context

Beckn protocol transactions are commercial contracts between participants. Every message exchanged must be attributable to a specific registered participant and must be tamper-evident. Since communication happens over public HTTPS, application-layer signing is required independently of transport-layer TLS.

---

## 2. Algorithms

### 2.1 Signing Algorithm: Ed25519

All Beckn Signatures MUST use the **Ed25519** signature scheme ([RFC 8032](https://datatracker.ietf.org/doc/html/rfc8032)).

### 2.2 Hashing Algorithm: BLAKE2b-512

For computing the request body digest, implementations MUST use **BLAKE2b-512** ([RFC 7693](https://datatracker.ietf.org/doc/html/rfc7693)).

Example:
```
BLAKE2b-512("The quick brown fox jumps over the lazy dog") =
a8add4bdddfd93e4877d2746e62817b116364a1fa7bc148d95090bc7333b3673f82401cf7aa2e4cb1ecd90296e3f14cb5413f8ed77be73045b13914cdcd6a918
```

Base64-encoded:
```
qK3Uvd39k+SHfSdG5igXsRY2Sh+nvBSNlQkLxzM7NnP4JAHPeqLkyx7NkCluPxTLVBP47Xe+cwRbE5FM3NapGA==
```

---

## 3. Authorization Header Format

```
Authorization: Signature keyId="{subscriberId}|{keyId}|{algorithm}",
               algorithm="ed25519",
               created="{unixTimestamp}",
               expires="{unixTimestamp}",
               headers="(created) (expires) digest",
               signature="{base64Signature}"
```

### Field Definitions

| Field | Description |
|---|---|
| `keyId` | `{subscriberId}\|{keyId}\|{algorithm}` — three pipe-delimited components |
| `algorithm` | MUST be `ed25519` |
| `created` | Unix timestamp (integer) of signature creation. MUST NOT be in the future. |
| `expires` | Unix timestamp (integer) of signature expiry. MUST NOT be in the past. MUST NOT exceed the registered key's `validUntil`. |
| `headers` | MUST be `(created) (expires) digest` |
| `signature` | Base64(Ed25519_sign(signingString, privateKey)) |

---

## 4. Signing Steps (Sender)

### Step 1 — Compute body digest

```
digest = Base64(BLAKE2b-512(rawRequestBody))
```

### Step 2 — Construct signing string

```
(created): {created_unix_ts}
(expires): {expires_unix_ts}
digest: BLAKE-512={base64_digest}
```

Note: exact newlines are significant. Each line ends with `\n`.

### Step 3 — Sign

```
signature = Base64(Ed25519_sign(signingString, signingPrivateKey))
```

### Step 4 — Compose Authorization header

Assemble as shown in Section 3.

---

## 5. Verification Steps (Receiver)

1. Extract `keyId` from the `Authorization` header.
2. Split `keyId` by `|` → `{ subscriberId, keyId, algorithm }`.
3. If `algorithm` in `keyId` ≠ `algorithm` field in header → return `401 NackUnauthorized`.
4. Query DeDi registry: `lookup(subscriberId, keyId)` → `{ signingPublicKey }`.
5. If no valid key found → return `401 NackUnauthorized`.
6. Check `created` ≤ now ≤ `expires` (with ≤ 5 second clock skew tolerance) → else `401`.
7. Recompute signing string from the request.
8. Verify `signature` using `signingPublicKey` → if invalid, return `401 NackUnauthorized`.
9. Optionally: check `messageId` against a short-lived deduplication cache to prevent replays.

---

## 6. Worked Example

### Request Body

```json
{"context":{"domain":"beckn:retail","action":"search","version":"2.0.1","bapId":"bap.example.com","bapUri":"https://bap.example.com","transactionId":"e6d9f908-1d26-4ff3-a6d1-3af3d3721054","messageId":"a2fe6d52-9fe4-4d1a-9d0b-dccb8b48522d","timestamp":"2026-01-04T09:17:55.971Z","ttl":"PT30S"},"message":{"@type":"SearchAction","intent":{"@type":"Intent","item":{"name":"coffee"}}}}
```

### BAP Key Pair (example — do not use in production)

```
signingPublicKey  = awGPjRK6i/Vg/lWr+0xObclVxlwZXvTjWYtlu6NeOHk=
signingPrivateKey = lP3sHA+9gileOkXYJXh4Jg8tK0gEEMbf9yCPnFpbldhrAY+NErqL9WD+Vav7TE5tyVXGXBle9ONZi2W7o144eQ==
```

### Step 1 — Digest

```
BLAKE2b-512(requestBody) → Base64 → b6lf6lRgOweajukcvcLsagQ2T60+85kRh/Rd2bdS+TG/5ALebOEgDJfyCrre/1+BMu5nA94o4DT3pTFXuUg7sw==
```

### Step 2 — Signing String

```
(created): 1641287875
(expires): 1641291475
digest: BLAKE-512=b6lf6lRgOweajukcvcLsagQ2T60+85kRh/Rd2bdS+TG/5ALebOEgDJfyCrre/1+BMu5nA94o4DT3pTFXuUg7sw==
```

### Step 3 — Signature

```
cjbhP0PFyrlSCNszJM1F/YmHDVAWsZqJUPzojnE/7TJU3fJ/rmIlgaUHEr5E0/2PIyf0tpSnWtT6cyNNlpmoAQ==
```

### Step 4 — Authorization Header

```
Signature keyId="bap.example.com|ae3ea24b-cfec-495e-81f8-044aaef164ac|ed25519",algorithm="ed25519",created="1641287875",expires="1641291475",headers="(created) (expires) digest",signature="cjbhP0PFyrlSCNszJM1F/YmHDVAWsZqJUPzojnE/7TJU3fJ/rmIlgaUHEr5E0/2PIyf0tpSnWtT6cyNNlpmoAQ=="
```

---

## 7. Changes from v1.x (BECKN-006)

| Aspect | v1.x | v2.0.x |
|---|---|---|
| BG signature header | `X-Gateway-Authorization` | Removed (no BG in v2) |
| Key resolution | Bespoke Beckn registry `lookup` | DeDi-compliant registry lookup |
| CounterSignature | Not defined | MUST be returned in `Ack` |
| `inReplyTo` | Not defined | MUST be in `CallbackContainer` |
| Signing algorithm | Ed25519 | Ed25519 (unchanged) |
| Hashing algorithm | BLAKE2b-512 | BLAKE2b-512 (unchanged) |

---

## 8. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-013-01 | Signing algorithm MUST be Ed25519 | MUST |
| CON-013-02 | Body digest MUST use BLAKE2b-512 | MUST |
| CON-013-03 | `headers` field MUST be `(created) (expires) digest` | MUST |
| CON-013-04 | `expires` MUST NOT exceed the registered key's `validUntil` | MUST |
| CON-013-05 | Receivers MUST resolve public key from DeDi registry | MUST |
| CON-013-06 | Receivers MUST reject requests with invalid signatures (401) | MUST |
| CON-013-07 | Receivers SHOULD cache registry lookups for key validity duration | SHOULD |

---

## 9. Security Considerations

- Signatures prevent message tampering and attribute messages to registered participants.
- The `created`/`expires` window limits replay attack windows.
- All Beckn communication MUST use HTTPS in addition to application-layer signing.
- Key compromise requires immediate key rotation and registry update.

---

## 10. References

- [RFC 8032 — Ed25519 signature scheme](https://datatracker.ietf.org/doc/html/rfc8032)
- [RFC 7693 — BLAKE2b hashing](https://datatracker.ietf.org/doc/html/rfc7693)
- [draft-cavage-http-signatures-12 — HTTP Signatures](https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures-12)
- [9_Authentication_and_Security.md](./9_Authentication_and_Security.md)
- [12_Registry_and_Identity.md](./12_Registry_and_Identity.md)

---

## 11. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | 2021-12-10 | Ravi Prakash | Initial draft (BECKN-006 v1.x) |
| Draft-02 | 2026-02-01 | — | v2 update: removed BG steps, added DeDi key resolution, added v2.0.1 non-repudiation requirements |
