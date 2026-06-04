# Authentication and Trust

## Document Details
- **ID:** NFH-007
- **Status:** Draft
- **Authors:**
  - [Ravi Prakash](https://github.com/ravi-prakash-v), [Networks for Humanity](https://networksforhumanity.org)
- **Created:** 2026-05-11
- **Updated:** 2026-05-11
- **Version history:** Draft-01 (2026-05-05): Initial publication.
- **Latest editor's draft:** [Authentication_and_Trust.md](./Authentication_and_Trust.md)
- **Implementation report:** Not available. This document is at Initial Draft status; report will be linked in the next formal release of this RFC, following merge to main.
- **Stress test report:** Not available. This document is at Initial Draft status; report will be linked in the next formal release of this RFC, following merge to main.
- **Conformance impact:** Not determined. This document is at Initial Draft status; impact will be classified in the next formal release of this RFC, following merge to main.
- **Security/privacy implications:** This RFC defines the complete authentication and non-repudiation model for all Beckn Protocol interactions. Incorrect implementation of any normative requirement creates exploitable vulnerabilities including message forgery, replay attacks, and man-in-the-middle substitution.
- **Replaces / Relates to:** Supersedes BECKN-006 Signing Beckn APIs in HTTP Draft-01. Relates to [Identity and Addressing](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Identity_and_Addressing.md) (drafted on `draft` branch, undergoing review).
- **Feedback:**
  - Issues: Click [here](https://github.com/beckn/protocol-specifications-v2/issues?q=is%3Aissue+label%3A%22NFH-007%22)
  - Discussions: Click [here](https://github.com/beckn/protocol-specifications-v2/discussions?discussions_q=label%3A%22NFH-007%22)
  - Pull Requests: Click [here](https://github.com/beckn/protocol-specifications-v2/pulls?q=is%3Apr+label%3A%22NFH-007%22)
- **Errata:** To be published.

## Abstract

This document defines the authentication and trust model for Beckn Protocol v2.0.0. It specifies how network participants (CNs, PNs, and DSes) prove their identity and establish non-repudiation on every message leg of a Beckn interaction using Ed25519 digital signatures over a canonical signing string, keyed to identities registered on the fabric's Global Root Registry.

## Table of Contents

- [Authentication and Trust](#authentication-and-trust)
  - [Document Details](#document-details)
  - [Abstract](#abstract)
  - [Table of Contents](#table-of-contents)
  - [Context](#context)
  - [Specification](#specification)
    - [Definitions](#definitions)
    - [Normative Requirements](#normative-requirements)
      - [1. Cryptographic Primitives](#1-cryptographic-primitives)
      - [2. Key Identity — the keyId Field](#2-key-identity--the-keyid-field)
        - [2.1 Implicit Format](#21-implicit-format)
        - [2.2 Explicit Format](#22-explicit-format)
        - [2.3 Key Lookup Procedure](#23-key-lookup-procedure)
          - [For implicit keyIds](#for-implicit-keyids)
          - [For explicit keyIds](#for-explicit-keyids)
      - [3. Signing String Construction](#3-signing-string-construction)
        - [3.1 Body Digest](#31-body-digest)
        - [3.2 Standard Signing String](#32-standard-signing-string)
        - [3.3 Callback Signing String](#33-callback-signing-string)
        - [3.4 Ack Response Signing String](#34-ack-response-signing-string)
      - [4. Request Signing — CN and PN](#4-request-signing--cn-and-pn)
      - [5. Synchronous Response Signing](#5-synchronous-response-signing)
      - [6. Callback Signing — PN to CN](#6-callback-signing--pn-to-cn)
      - [7. Verifying a Callback — CN Procedure](#7-verifying-a-callback--cn-procedure)
        - [Step 1 — Parse the Authorization header](#step-1--parse-the-authorization-header)
        - [Step 2 — Validate timestamps](#step-2--validate-timestamps)
        - [Step 3 — Validate algorithm](#step-3--validate-algorithm)
        - [Step 4 — Fetch the PN's public key](#step-4--fetch-the-pns-public-key)
        - [Step 5 — Reconstruct the signing string](#step-5--reconstruct-the-signing-string)
        - [Step 6 — Verify the PN's Ed25519 signature](#step-6--verify-the-pns-ed25519-signature)
        - [Step 7 — Verify the request-signature chain (solicited callbacks only)](#step-7--verify-the-request-signature-chain-solicited-callbacks-only)
        - [Step 8 — Return Ack](#step-8--return-ack)
      - [8. Verifying a Request — PN and DS Procedure](#8-verifying-a-request--pn-and-ds-procedure)
      - [9. Pre-call NP Verification](#9-pre-call-np-verification)
        - [9.1 Subscriber Reference Lookup (Same-Network NPs)](#91-subscriber-reference-lookup-same-network-nps)
        - [9.2 Key Expiry Check Before Callbacks](#92-key-expiry-check-before-callbacks)
      - [10. Replay Protection](#10-replay-protection)
        - [10.1 CN Request Replay Protection](#101-cn-request-replay-protection)
        - [10.2 Solicited Callback Replay Protection](#102-solicited-callback-replay-protection)
        - [10.3 PN-Initiated Callback Replay Protection](#103-pn-initiated-callback-replay-protection)
    - [Conformance Requirements](#conformance-requirements)
    - [Cross-cutting considerations](#cross-cutting-considerations)
      - [Clock skew](#clock-skew)
      - [Key rotation](#key-rotation)
      - [Privacy](#privacy)
      - [Key compromise](#key-compromise)
      - [Explicit keyId trust](#explicit-keyid-trust)
    - [Migration Notes](#migration-notes)
    - [Examples](#examples)
      - [Example 1: CN Request to PN](#example-1-cn-request-to-pn)
        - [Step 1 — Compute body digest](#step-1--compute-body-digest)
        - [Step 2 — Construct signing string](#step-2--construct-signing-string)
        - [Step 3 — Sign and assemble header](#step-3--sign-and-assemble-header)
      - [Example 2: PN Synchronous Ack Response](#example-2-pn-synchronous-ack-response)
        - [Step 1 — Extract CN's request signature](#step-1--extract-cns-request-signature)
        - [Step 2 — Compute Ack body digest](#step-2--compute-ack-body-digest)
        - [Step 3 — Construct Ack signing string](#step-3--construct-ack-signing-string)
        - [Step 4 — Assemble Ack response](#step-4--assemble-ack-response)
      - [Example 3: PN Solicited Callback to CN](#example-3-pn-solicited-callback-to-cn)
        - [Step 1 — Extract CN's original signature](#step-1--extract-cns-original-signature)
        - [Step 2 — Compute callback body digest](#step-2--compute-callback-body-digest)
        - [Step 3 — Construct callback signing string](#step-3--construct-callback-signing-string)
        - [Step 4 — Assemble callback request](#step-4--assemble-callback-request)
        - [CN verification](#cn-verification)
  - [Conclusion](#conclusion)
    - [Open Questions](#open-questions)
  - [Acknowledgements](#acknowledgements)
  - [References](#references)

## Context

Beckn Protocol enables bilateral, asynchronous value-exchange interactions between independent network participants (NPs) — Consumer Node (CNs), Provider Node (PNs), and Discovery Services (DSes) — that have no pre-established trust relationship beyond their shared registration on the fabric. Every message in a Beckn interaction crosses trust boundaries: the receiver cannot assume the sender is who it claims to be, and cannot assume the payload was not tampered with in transit.

The trust model in both Beckn Protocol v1.x and v2.0 is identical in principle: each NP independently authenticates inbound messages by fetching the sender's registered public key from a verified public registry and verifying the Ed25519 signature over the message body. The Beckn Gateway (BG), present in v1.x, was a routing intermediary — it forwarded requests between CNs and PNs — but it was never the source of trust and was not an authentication component. The structural change in v2.0 is the registry protocol. In v1.x, NPs issued Beckn Protocol-format API calls to query subscriber records from a Beckn-compliant registry. In v2.0, NPs issue dedi (Decentralized Directory) protocol-format API calls to query namespace and key records from a dedi-compliant registry. The GRR at `fabric.nfh.global/registry` is the canonical v2.0 registry; it is not a Beckn API and implements no Beckn endpoint. The removal of the BG simplifies the message flow to direct CN ↔ PN/DS communication but does not change the underlying trust mechanism.

This RFC specifies: (a) the key identity format that binds a signing key to a fabric-registered namespace; (b) the signing string construction that commits the sender's identity to a specific message body and time window; (c) the request signing procedure; (d) the synchronous response signing procedure that enables the sender to verify authenticated receipt; (e) the callback signing procedure that chains the PN's signature to the CN's original request signature; (f) the pre-call verification procedure for NPs on the same network; and (g) replay protection rules for CN requests and PN callbacks.

## Specification

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described [here](./Keyword_Definitions.md). These definitions aim to ensure that the terms are understood precisely and consistently to avoid confusion in the interpretation of standards, specifications, and protocols.

### Definitions

- **NP (Network Participant):** Any entity participating in a Beckn interaction — CN, PN, or DS.
- **CN (Consumer Node):** The NP that initiates value-exchange requests on behalf of consumers.
- **PN (Provider Node):** The NP that receives value-exchange requests and responds to them via asynchronous callbacks.
- **DS (Discovery Service):** The NP that indexes catalogs published by PNs and responds to discovery requests from CNs.
- **CS (Cataloging Service):** The fabric service that receives, validates, and indexes catalogs submitted by PNs and distributes them to DSes.
- **GRR (Global Root Registry):** The fabric's canonical identity and address lookup service, hosted at `fabric.nfh.global/registry`, operated by the Networks for Humanity Foundation.
- **dedi protocol:** The Decentralized Directory protocol used by the GRR for namespace and key management.
- **keyId:** A structured string that uniquely identifies a signing key registered on a dedi-protocol registry.
- **Signing string:** The canonical byte sequence that is signed and verified using Ed25519.
- **Body digest:** The BLAKE-512 hash of the HTTP request or response body, encoded as described in §3.1.
- **request-signature:** The raw Ed25519 signature value extracted from an incoming request's `Authorization` header and included verbatim in either a PN's callback signing string (§3.3) or a responding NP's Ack response signing string (§3.4), cryptographically binding the outgoing message to the specific request that triggered it.
- **Implicit keyId:** A keyId that uses a path-only format and is resolved exclusively via the GRR at `fabric.nfh.global/registry`.
- **Explicit keyId:** A keyId that embeds the full registry URL, allowing resolution against any dedi-protocol compliant registry.
- **PN-initiated callback:** A callback sent by a PN to a CN's `/on_*` endpoint without a preceding CN request in the current message exchange. Only endpoints designated as supporting PN-initiated callbacks in the Beckn Protocol API specification may send them.
- **Solicited callback:** A callback sent by a PN to a CN's `/on_*` endpoint in direct response to a prior CN request accepted with a `200 Ack`.

### Normative Requirements

#### 1. Cryptographic Primitives

All Beckn authentication MUST use the following primitives:

| Primitive | Value |
|---|---|
| Signature algorithm | Ed25519 (as specified in RFC 8032) |
| Body hash algorithm | BLAKE-512 (as specified in RFC 7693) |
| Body hash encoding | Standard Base64 with `=` padding (RFC 4648 §4) |
| Timestamp format | Unix epoch integer (seconds since 1970-01-01T00:00:00Z) |

No other signature or hash algorithm is permitted. An NP that receives a message carrying an `algorithm` value other than `ed25519` MUST reject it with a `401 NackUnauthorized`.

#### 2. Key Identity — the keyId Field

Every Beckn HTTP Signature carries a `keyId` field that uniquely identifies the signing key. The `keyId` MUST take exactly one of two formats: implicit or explicit.

##### 2.1 Implicit Format

```
{namespace_id}/{registry_id}/{record_id}|{algorithm}
```

- `{namespace_id}` — the NP's namespace on the fabric, as registered via the Namespacing Service.
- `{registry_id}` — the registry within that namespace that holds the key record.
- `{record_id}` — the specific record identifier within the registry.
- `{algorithm}` — MUST be `ed25519`.
- The three path components are separated by `/`; the algorithm is separated from the path by `|`.

An implicit keyId MUST be resolvable via the fabric's Global Root Registry only. Verifying NPs MUST treat an implicit keyId as residing at `https://fabric.nfh.global/registry` and MUST NOT attempt to resolve it against any other registry.

**Example:**
```
example-bap.beckn.io/keys/signing-key-001|ed25519
```

##### 2.2 Explicit Format

```
https://{registry_domain}/{namespace_id}/{registry_id}/{record_id}|{algorithm}
```

- The full URL up to (but not including) the `|` separator is a dedi protocol-compliant registry URL that resolves to the key record.
- `{algorithm}` — MUST be `ed25519`.
- The algorithm is appended after the URL using the `|` separator.

An explicit keyId instructs the verifier to resolve the public key from the specified registry URL rather than from the GRR. The target URL MUST be a dedi protocol-compliant registry. NPs MAY choose not to trust registries outside `fabric.nfh.global/registry`; in that case they MUST reject signatures carrying explicit keyIds from untrusted registries with a `401 NackUnauthorized`.

**Example:**
```
https://registry.example-nfo.io/example-bpp.beckn.io/keys/signing-key-001|ed25519
```

##### 2.3 Key Lookup Procedure

###### For implicit keyIds

The verifying NP MUST fetch the public key by issuing an HTTP GET request to:

```
https://fabric.nfh.global/registry/dedi/lookup/{keyId}
```

where `{keyId}` is the full implicit keyId string — including the `|algorithm` suffix — appended to the path **without URL-encoding**. The `|` and `/` characters MUST be transmitted as literal characters in the path.

**Example lookup URL:**
```
https://fabric.nfh.global/registry/dedi/lookup/example-bap.beckn.io/keys/signing-key-001|ed25519
```

###### For explicit keyIds

The verifying NP MUST extract the URL portion (everything before `|`) and issue an HTTP GET to that URL to retrieve the key record.

In both cases, the verifying NP MUST:

1. Confirm the `algorithm` suffix matches the `algorithm` field in the `Authorization` header. If they differ, reject with `401`.
2. Extract the public key from the registry response.
3. Verify the Ed25519 signature using that public key.
4. If the lookup fails or returns no key, reject with `401`.

#### 3. Signing String Construction

The signing string is a newline-delimited (`\n`) sequence of labeled values. The order of lines MUST match the order of field names declared in the `headers` attribute of the `Authorization` header.

##### 3.1 Body Digest

The body digest is computed as:

```
digest = "BLAKE-512=" + Base64( BLAKE-512( UTF-8(body) ) )
```

- `body` is the raw UTF-8-encoded HTTP request or response body as it appears on the wire, before any transfer encoding is removed.
- For requests with no body (e.g. GET), the digest MUST be computed over the empty byte string.
- The prefix `BLAKE-512=` is a literal string prepended to the Base64-encoded hash.

##### 3.2 Standard Signing String

Used for all outbound CN requests and all synchronous responses:

```
(created): {created_unix_ts}
(expires): {expires_unix_ts}
digest: {body_digest}
```

Each line consists of the field name, a colon, a single space, and the value. Lines are separated by a single newline character (`\n`). No trailing newline.

- `{created_unix_ts}` — the Unix timestamp at which the signature was generated. MUST NOT be in the future at the time of verification.
- `{expires_unix_ts}` — the Unix timestamp at which the signature expires. MUST be greater than `{created_unix_ts}`. MUST NOT be in the past at the time of verification. MUST NOT exceed the expiry of the signing key's registration.
- `{body_digest}` — the body digest as defined in §3.1.

##### 3.3 Callback Signing String

Used exclusively when the PN sends a solicited callback to the CN's `/on_*` endpoint. The PN MUST append a fourth line containing the CN's original request signature:

```
(created): {created_unix_ts}
(expires): {expires_unix_ts}
digest: {callback_body_digest}
request-signature: {cn_signature_value}
```

- `{callback_body_digest}` — digest of the **callback** request body (not the original CN request body).
- `{cn_signature_value}` — the raw Base64-encoded Ed25519 signature value extracted from the CN's `Authorization` header's `signature="..."` field. This MUST be the literal string value of the `signature` attribute only, without the surrounding quotes or any other Authorization header components.

The `headers` attribute of the PN's callback `Authorization` header MUST declare all four fields in order: `"(created) (expires) digest request-signature"`.

##### 3.4 Ack Response Signing String

Used for every synchronous HTTP response. The responding NP MUST append a fourth line containing the incoming request's signature:

```
(created): {created_unix_ts}
(expires): {expires_unix_ts}
digest: {response_body_digest}
request-signature: {incoming_request_signature_value}
```

- `{response_body_digest}` — digest of the **response** body (not the inbound request body).
- `{incoming_request_signature_value}` — the raw Base64-encoded Ed25519 signature value extracted from the incoming request's `Authorization` header's `signature="..."` field. This MUST be the literal string value of the `signature` attribute only, without the surrounding quotes or any other Authorization header components. Extraction procedure is identical to §3.3.

The `headers` attribute of the `Signature` response header MUST declare all four fields in order: `"(created) (expires) digest request-signature"`.

#### 4. Request Signing — CN and PN

Every Beckn HTTP request — whether initiated by a CN (to a PN or DS) or by a PN (callback to a CN) — MUST carry an `Authorization` header in the following format:

```
Authorization: Signature keyId="{keyId}",algorithm="ed25519",created="{created}",expires="{expires}",headers="{headers_list}",signature="{base64_signature}"
```

Attribute definitions:

| Attribute | Type | Description |
|---|---|---|
| `keyId` | string | The signing key identifier in implicit or explicit format (§2). |
| `algorithm` | string | MUST be `ed25519`. |
| `created` | integer string | Unix timestamp of signature creation. |
| `expires` | integer string | Unix timestamp of signature expiry. |
| `headers` | string | Space-separated list of fields included in the signing string. For CN requests and PN-initiated callbacks: `"(created) (expires) digest"`. For PN solicited callbacks: `"(created) (expires) digest request-signature"`. For synchronous responses (`Signature` header): `"(created) (expires) digest request-signature"`. |
| `signature` | string | Standard Base64 encoding of the Ed25519 signature over the signing string. |

The signing procedure for a request is:

1. Serialize the request body to UTF-8.
2. Compute the body digest (§3.1).
3. Construct the signing string (§3.2 for CN requests and PN-initiated callbacks; §3.3 for PN solicited callbacks).
4. Sign the UTF-8 encoding of the signing string using the NP's Ed25519 private key.
5. Base64-encode the resulting 64-byte signature.
6. Assemble the `Authorization` header value as specified above.

#### 5. Synchronous Response Signing

Every synchronous HTTP response — regardless of status code (200, 400, 401, 409, 429, 500) — MUST carry a `Signature` response header. This header proves that the responding NP received and authenticated the specific inbound request, establishing non-repudiation for the synchronous leg.

The `Signature` response header uses the same format as the request `Authorization` header but:

- The header name is `Signature`, not `Authorization`.
- The body digest is computed over the **response** body.
- The signing string is the Ack response signing string (§3.4), which chains the response to the inbound request's signature via `request-signature`.
- The signer is the responding NP (PN or DS for incoming requests; CN for incoming callbacks).

```
Signature: keyId="{keyId}",algorithm="ed25519",created="{created}",expires="{expires}",headers="(created) (expires) digest request-signature",signature="{base64_signature}"
```

The signing procedure for a synchronous response is:

1. Serialize the response body to UTF-8.
2. Compute the body digest (§3.1).
3. Extract the raw Base64 signature value from the incoming request's `Authorization` header `signature="..."` field.
4. Construct the Ack response signing string (§3.4).
5. Sign the UTF-8 encoding of the signing string using the responding NP's Ed25519 private key.
6. Base64-encode the 64-byte signature.
7. Add the `Signature` header to the HTTP response.

The sending NP SHOULD verify the `Signature` response header upon receiving a synchronous response, using the responding NP's public key fetched via the key lookup procedure (§2.3). The sender SHOULD confirm the `request-signature` field in the response matches the `signature` value from its own outbound `Authorization` header for that request. A missing or invalid `Signature` response header does not invalidate the transaction but SHOULD be logged and MAY be treated as a degraded trust signal.

#### 6. Callback Signing — PN to CN

When the PN sends a solicited callback to the CN's `/on_*` endpoint, it MUST sign the callback using the callback signing string (§3.3), which chains the PN's signature to the CN's original request signature. This chain allows the CN to verify that the callback is a genuine response to a request it actually sent.

The PN MUST:

1. Retrieve the CN's `Authorization` header from the original request that triggered this callback.
2. Extract the raw Base64 signature value from the CN's `Authorization` header's `signature="..."` attribute. This value becomes `{cn_signature_value}`.
3. Compute the body digest of the callback request body (§3.1).
4. Construct the callback signing string (§3.3) using the PN's own `{created}` and `{expires}` timestamps, the callback body digest, and `{cn_signature_value}`.
5. Sign the UTF-8 encoding of the signing string with the PN's Ed25519 private key.
6. Assemble the `Authorization` header with `headers="(created) (expires) digest request-signature"`.

The PN MUST retain the CN's original `Authorization` header value at least until the callback has been successfully acknowledged (200 Ack) by the CN, to support retries.

For PN-initiated callbacks (§10.3), the PN MUST omit the `request-signature` field and MUST use the standard signing string (§3.2) with `headers="(created) (expires) digest"`.

#### 7. Verifying a Callback — CN Procedure

Upon receiving a callback at its `/on_*` endpoint, the CN MUST perform the following verification steps in order. If any step fails, the CN MUST return `401 NackUnauthorized`.

##### Step 1 — Parse the Authorization header

Extract `keyId`, `algorithm`, `created`, `expires`, `headers`, and `signature` from the PN's `Authorization` header.

##### Step 2 — Validate timestamps

Confirm that `created` is not in the future beyond the subnet-configured clock skew tolerance (default: 5 seconds) and that `expires` is not in the past.

##### Step 3 — Validate algorithm

Confirm `algorithm` is `ed25519`. Reject any other value.

##### Step 4 — Fetch the PN's public key

Use the key lookup procedure (§2.3) to retrieve the PN's Ed25519 public key.

##### Step 5 — Reconstruct the signing string

Using the `headers` field as the ordered list of fields:

- If `headers` is `"(created) (expires) digest"`: reconstruct the standard signing string (§3.2) using the `created` and `expires` values from the PN's `Authorization` header and the BLAKE-512 digest of the received callback body. This is a PN-initiated callback.
- If `headers` is `"(created) (expires) digest request-signature"`: reconstruct the callback signing string (§3.3) using the above plus the value on the `request-signature` line. This is a solicited callback; proceed to Step 7.

##### Step 6 — Verify the PN's Ed25519 signature

Verify the decoded `signature` against the reconstructed signing string using the PN's public key. If verification fails, reject with `401`.

##### Step 7 — Verify the request-signature chain (solicited callbacks only)

If `headers` contains `request-signature`:

1. Retrieve the `signature` value from the CN's own stored outbound `Authorization` header for the message identified by `context.transactionId` and `context.messageId` from the callback's `context` object.
2. Compare it to the `{cn_signature_value}` extracted from the reconstructed signing string's `request-signature` line.
3. If they do not match, reject with `401`. This mismatch indicates the callback was not issued in response to a request the CN sent.

##### Step 8 — Return Ack

If all steps pass, return `200 Ack` with the CN's own `Signature` response header (§5).

#### 8. Verifying a Request — PN and DS Procedure

Upon receiving a request from a CN, the PN or DS MUST perform the following verification steps. If any step fails, it MUST return `401 NackUnauthorized`.

1. Parse `keyId`, `algorithm`, `created`, `expires`, `headers`, and `signature` from the `Authorization` header.
2. Confirm `created` is not in the future beyond the subnet-configured clock skew tolerance (default: 5 seconds) and `expires` is not in the past.
3. Confirm `algorithm` is `ed25519`.
4. Fetch the CN's public key using the key lookup procedure (§2.3).
5. Reconstruct the standard signing string (§3.2) using the `created` and `expires` values and the BLAKE-512 digest of the received request body.
6. Verify the decoded `signature` against the signing string using the CN's public key.
7. Return the appropriate response with the responding NP's `Signature` response header (§5). The `Signature` header MUST use the Ack response signing string (§3.4), with the `request-signature` field set to the raw Base64 value extracted from the incoming request's `Authorization` header.

#### 9. Pre-call NP Verification

Before sending any Beckn request or callback, the sending NP SHOULD verify that the receiving NP is still active and authorized to participate on the network.

##### 9.1 Subscriber Reference Lookup (Same-Network NPs)

When both the sending and receiving NP are members of the same subnet (i.e. they share the same `networkId` registered with the same NFO), the sending NP SHOULD perform a `subscriber_reference` registry lookup for the receiving NP's entry on that network's NFO-managed registry **immediately before** dispatching the message. The NFO may have revoked the receiving NP's participation since the last interaction, and a revoked NP MUST NOT be called.

If the receiving NP's `subscriber_reference` record is absent or shows a revoked status, the sending NP MUST NOT send the message and MUST treat the condition as a configuration or trust error rather than a transient failure.

##### 9.2 Key Expiry Check Before Callbacks

A PN sending a solicited callback SHOULD verify that its own signing key has not expired in the interval between receiving the original CN request and sending the callback. Because processing latency, queuing, or high system load can introduce delays between a synchronous Ack and the eventual callback, a key that was valid at Ack time may have expired by callback time. A PN that discovers its signing key has expired MUST rotate to a valid key and update its key record in the GRR before sending the callback.

Additionally, if the CN's public key was cached during the original request verification, the PN SHOULD re-verify the CN's key validity before using the cached value to construct the `request-signature` field. A key that was valid at request time may have been revoked or expired in the interim.

#### 10. Replay Protection

Replay protection rules differ between CN requests and PN callbacks because the semantics of the `messageId` field differ for each role.

##### 10.1 CN Request Replay Protection

A CN MUST assign a globally unique `messageId` to every outbound request. No two requests from the same CN, even within the same transaction, may reuse a `messageId`. A PN or DS receiving a request whose `messageId` matches a previously processed request within its replay detection window MUST reject the duplicate with a `400 NackBadRequest`.

##### 10.2 Solicited Callback Replay Protection

A PN MUST use the **same** `messageId` as the triggering CN request in its solicited callback. This shared `messageId` is the mechanism by which the CN correlates the callback to its outbound request.

The CN MUST persist the `messageId` of each outbound request until one of the following occurs, whichever is earlier:

- The corresponding solicited callback is received and accepted.
- The `expires` timestamp from the CN's outbound `Authorization` header for that request passes.

Upon receiving a callback, the CN MUST verify that the `messageId` in the callback's `context` object matches a `messageId` the CN has persisted and for which it has not yet received a callback. A callback with a `messageId` the CN does not recognize, or one for which a callback has already been received, MUST be rejected.

##### 10.3 PN-Initiated Callback Replay Protection

A PN sending a PN-initiated callback MUST assign a unique `messageId` to each notification. No two PN-initiated callbacks may share a `messageId`. However, the `transactionId` in a PN-initiated callback MUST match the `transactionId` of an active, confirmed transaction between the CN and PN. A CN receiving a PN-initiated callback with an unrecognized `transactionId` MUST reject it with a `400 NackBadRequest`.

### Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-004-01 | Every Beckn HTTP request MUST carry an `Authorization` header in Beckn HTTP Signature format. | MUST |
| CON-004-02 | Every Beckn HTTP synchronous response MUST carry a `Signature` response header signing the response body. | MUST |
| CON-004-03 | The signature algorithm MUST be `ed25519`. No other value is permitted. | MUST |
| CON-004-04 | The body digest MUST be computed using BLAKE-512 and encoded as `BLAKE-512={Base64}`. | MUST |
| CON-004-05 | The `keyId` field MUST use either the implicit format (`{namespace_id}/{registry_id}/{record_id}\|{algorithm}`) or the explicit format (full dedi protocol URL with `\|{algorithm}` suffix). | MUST |
| CON-004-06 | An implicit `keyId` MUST be resolved exclusively via `https://fabric.nfh.global/registry/dedi/lookup/{keyId}` without URL-encoding the keyId string. | MUST |
| CON-004-07 | The `expires` timestamp MUST NOT exceed the registered expiry of the signing key. | MUST |
| CON-004-08 | An NP receiving a Beckn request with a missing, expired, or unverifiable signature MUST return `401 NackUnauthorized`. | MUST |
| CON-004-09 | A PN sending a solicited callback to a CN MUST use the callback signing string, appending the CN's original `signature` value as the `request-signature` field. | MUST |
| CON-004-10 | The PN MUST declare `headers="(created) (expires) digest request-signature"` in its callback `Authorization` header when sending a solicited callback. | MUST |
| CON-004-11 | The CN MUST verify the `request-signature` field in a PN solicited callback against its own previously sent signature for the same `transactionId`/`messageId`. | MUST |
| CON-004-12 | A PN sending a PN-initiated callback MUST use the standard signing string with `headers="(created) (expires) digest"`. | MUST |
| CON-004-13 | The `created` timestamp SHOULD NOT be more than 5 seconds in the future relative to the verifier's clock. NFOs MAY configure a different tolerance for their subnet; all NPs on that subnet MUST use the configured value. | SHOULD |
| CON-004-14 | An NP MUST NOT trust an explicit `keyId` resolving to a registry outside `fabric.nfh.global/registry` unless that registry has been explicitly configured as trusted by the NP's operator. | SHOULD |
| CON-004-15 | The `request-signature` value included in the callback signing string MUST be the raw Base64 `signature` attribute value from the CN's `Authorization` header, with no additional encoding or transformation. | MUST |
| CON-004-16 | A CN MUST assign a unique `messageId` to every outbound request. | MUST |
| CON-004-17 | A PN solicited callback MUST carry the same `messageId` as the triggering CN request. | MUST |
| CON-004-18 | A CN MUST persist each outbound request's `messageId` until the corresponding solicited callback is received or the request's `expires` timestamp passes. | MUST |
| CON-004-19 | A PN sending a PN-initiated callback MUST carry a unique `messageId`. | MUST |
| CON-004-20 | A PN sending a PN-initiated callback MUST carry a `transactionId` matching an active, confirmed transaction between that CN and PN. | MUST |
| CON-004-21 | When both the sending and receiving NP are members of the same subnet, the sending NP SHOULD perform a `subscriber_reference` registry lookup for the receiving NP immediately before dispatching a message. | SHOULD |
| CON-004-22 | A PN SHOULD verify that its own signing key has not expired before sending a solicited callback. | SHOULD |
| CON-004-23 | Every synchronous response `Signature` header MUST use the Ack response signing string (§3.4) with `headers="(created) (expires) digest request-signature"`. The `request-signature` value MUST be the raw Base64 `signature` attribute value from the incoming request's `Authorization` header. | MUST |

### Cross-cutting considerations

#### Clock skew

A tolerance of up to 5 seconds is the recommended default for the `created` field. NFOs MAY configure a stricter or more permissive value for their subnet; when they do, all NPs operating within that subnet MUST use the configured value. NPs MUST NOT accept any tolerance for `expires`; an expired signature MUST be rejected without exception regardless of subnet configuration.

#### Key rotation

When an NP rotates its signing key, the old key MUST remain resolvable in the GRR until all in-flight transactions that used it have expired. The NP MUST update its key registration atomically and MUST NOT sign new messages with the old key after rotation.

#### Privacy

The `keyId` path exposes the NP's namespace identifier in every request header. This is by design: fabric identity is not pseudonymous at the protocol level.

#### Key compromise

If an NP's private key is compromised, the NP MUST immediately revoke the key record in the GRR. The GRR revocation status MUST be checked at verification time; a cached public key from a revoked record MUST NOT be used to verify signatures.

#### Explicit keyId trust

Allowing explicit keyIds pointing to arbitrary registries creates a trust bootstrapping problem. NPs that have not configured explicit trust for a given registry SHOULD default to rejecting such signatures rather than accepting them, to avoid being deceived by rogue registries.

### Migration Notes

The following v1.x patterns are breaking changes in v2.0:

1. **BG removed:** There is no `X-Gateway-Authorization` header in v2.0. BG routing infrastructure MUST be decommissioned or bypassed. Direct CN ↔ PN/DS connectivity is required.
2. **Registry protocol change:** The v1.x Beckn Protocol-compliant registry lookup is replaced by dedi protocol-compliant lookup against `fabric.nfh.global/registry`. All registry query code MUST be updated to the dedi protocol API.
3. **Request-signature chaining:** Solicited callbacks now carry the CN's original signature as the `request-signature` field in the signing string. v1.x callback implementations MUST add this field with `headers="(created) (expires) digest request-signature"`.
4. **Synchronous response signing:** Every response now requires a `Signature` header using the Ack response signing string (§3.4), which includes `request-signature`. v1.x implementations that returned unsigned responses MUST add this; implementations that used a 3-line signing string for responses MUST add the `request-signature` field.
5. **keyId format change:** The v1.x format `{subscriber_id}|{unique_key_id}|{algorithm}` is replaced by the path-based implicit format `{namespace_id}/{registry_id}/{record_id}|{algorithm}`. Existing key registrations MUST be migrated to the new namespace structure in the GRR before go-live on v2.0.

### Examples

#### Example 1: CN Request to PN

**Scenario:** CN `cn.example.com` sends a `/select` request to PN `pn.example.com`.

##### Step 1 — Compute body digest

```
body = '{"context":{"action":"select",...},"message":{...}}'
hash = BLAKE-512( UTF-8(body) )
digest = "BLAKE-512=" + Base64(hash)
       = "BLAKE-512=qK3Uvd39k+SHfSdG5igXsRY2Sh+nvBSNlQkLxzM7NnP4..."
```

##### Step 2 — Construct signing string

```
(created): 1746518400
(expires): 1746518700
digest: BLAKE-512=qK3Uvd39k+SHfSdG5igXsRY2Sh+nvBSNlQkLxzM7NnP4...
```

##### Step 3 — Sign and assemble header

```http
POST /select HTTP/1.1
Host: pn.example.com
Authorization: Signature keyId="cn.example.com/keys/k001|ed25519",algorithm="ed25519",created="1746518400",expires="1746518700",headers="(created) (expires) digest",signature="Base64EncodedEd25519SignatureHere=="
Content-Type: application/json

{"context":{"action":"select","transactionId":"550e8400-e29b-41d4-a716-446655440001","messageId":"550e8400-e29b-41d4-a716-446655440000",...},"message":{...}}
```

#### Example 2: PN Synchronous Ack Response

**Scenario:** PN receives the `/select` request from Example 1, verifies it, and returns a synchronous `200 Ack`.

##### Step 1 — Extract CN's request signature

```
cn_signature_value = "Base64EncodedEd25519SignatureHere=="
```

This is the raw Base64 value from the `signature="..."` field of the CN's `Authorization` header in Example 1.

##### Step 2 — Compute Ack body digest

```
ack_body = '{"message":{"status":"ACK","messageId":"550e8400-e29b-41d4-a716-446655440000"}}'
digest = "BLAKE-512=" + Base64( BLAKE-512( UTF-8(ack_body) ) )
       = "BLAKE-512=AckBodyDigestHere..."
```

##### Step 3 — Construct Ack signing string

```
(created): 1746518401
(expires): 1746518701
digest: BLAKE-512=AckBodyDigestHere...
request-signature: Base64EncodedEd25519SignatureHere==
```

##### Step 4 — Assemble Ack response

```http
HTTP/1.1 200 OK
Content-Type: application/json
Signature: keyId="pn.example.com/keys/k002|ed25519",algorithm="ed25519",created="1746518401",expires="1746518701",headers="(created) (expires) digest request-signature",signature="BPPAckSignatureHere=="

{"message":{"status":"ACK","messageId":"550e8400-e29b-41d4-a716-446655440000"}}
```

The PN's `Signature` header signs a four-line string that covers the Ack body digest and the CN's original request signature. The CN verifies the PN's `Signature` and confirms the `request-signature` field matches the `signature` value it sent in its own `Authorization` header.

#### Example 3: PN Solicited Callback to CN

**Scenario:** PN sends the asynchronous `/on_select` callback to the CN. The CN's original `signature` value from Example 1 is `Base64EncodedEd25519SignatureHere==`.

##### Step 1 — Extract CN's original signature

```
cn_signature_value = "Base64EncodedEd25519SignatureHere=="
```

##### Step 2 — Compute callback body digest

```
callback_body = '{"context":{"action":"on_select","transactionId":"550e8400-e29b-41d4-a716-446655440001","messageId":"550e8400-e29b-41d4-a716-446655440000",...},"message":{...}}'
digest = "BLAKE-512=" + Base64( BLAKE-512( UTF-8(callback_body) ) )
       = "BLAKE-512=rN4Wve49l+TIfTeH6jhYtCS3Ti+owCTOmRlMyy8OoQQ5..."
```

##### Step 3 — Construct callback signing string

```
(created): 1746518450
(expires): 1746518750
digest: BLAKE-512=rN4Wve49l+TIfTeH6jhYtCS3Ti+owCTOmRlMyy8OoQQ5...
request-signature: Base64EncodedEd25519SignatureHere==
```

##### Step 4 — Assemble callback request

```http
POST /on_select HTTP/1.1
Host: cn.example.com
Authorization: Signature keyId="pn.example.com/keys/k002|ed25519",algorithm="ed25519",created="1746518450",expires="1746518750",headers="(created) (expires) digest request-signature",signature="BPPCallbackSignatureHere=="
Content-Type: application/json

{"context":{"action":"on_select","transactionId":"550e8400-e29b-41d4-a716-446655440001","messageId":"550e8400-e29b-41d4-a716-446655440000",...},"message":{...}}
```

##### CN verification

1. Fetch PN's public key from `https://fabric.nfh.global/registry/dedi/lookup/pn.example.com/keys/k002|ed25519`.
2. Reconstruct the callback signing string using the four `headers` fields in declared order.
3. Verify PN's `signature` against the reconstructed string.
4. Extract `request-signature` value: `Base64EncodedEd25519SignatureHere==`.
5. Look up CN's persisted signature for `messageId=550e8400-e29b-41d4-a716-446655440000`. They match → callback is authentic and solicited.
6. Return `200 Ack` with CN's own `Signature` response header.

## Conclusion

This RFC establishes a bilateral, non-repudiable authentication model for Beckn Protocol v2.0.0 that extends the existing public-key registry trust model with two new guarantees: solicited callback chaining (every callback cryptographically proves it responds to a specific CN request) and mandatory synchronous response signing (every response proves authenticated receipt). Replay protection rules for CNs and PNs reflect their different roles in the message exchange. Together, these mechanisms ensure that every Beckn message can be attributed to a fabric-registered identity and verified independently by any NP without any centralized intermediary.

### Open Questions

1. **Explicit keyId trust model:** Should the spec provide a standard mechanism for NPs to publish their list of trusted external registries, or leave this to operator configuration?

2. **Challenge-response authentication for fabric service callbacks:** Fabric services (NS, GRR, CS) are implicitly trusted by all NPs on the fabric. Given this implicit trust, should the spec define a challenge-response path as the designated verification mechanism for fabric service callbacks, rather than requiring full request-body signature verification? The proposed mechanism: the NP generates a challenge by encrypting `(input || nonce)` with the fabric service's well-known public key and includes it in the outbound request; the fabric service decrypts the challenge using its private key and echoes the plaintext `(input || nonce)` back in the callback response; the NP verifies the echo matches its original plaintext, confirming the callback originated from a party in possession of the fabric's private key. This would be particularly valuable for large payloads such as `catalog/pull` results delivered by the CS to a DS, where computing and verifying a BLAKE-512 digest and Ed25519 signature over the full response body is non-trivial. Open considerations include: how the challenge is transmitted (a dedicated request header or a field in the `context` object); whether the response body should still carry a signature for non-repudiation even if the challenge-response is used for source authentication; and whether this mechanism should apply to all fabric service interactions or only to specific endpoints where payload size makes full verification costly.

3. **End-to-end catalog integrity — PN origin proof through the CS:** When a PN publishes a catalog to the CS via `/catalog/publish`, the HTTP request signature (defined in §4) authenticates the publish request but does not travel with the catalog payload. When the CS subsequently delivers that catalog to a DS — either via `/on_discover`, a `catalog/pull` callback, or a subscription push — the DS receives a payload signed by the CS, not by the PN. Implicit trust in the CS means the DS trusts the CS not to tamper, but it provides no independent means to verify that the catalog contents are exactly what the PN originally submitted. Should the spec require PNs to produce an application-layer signature over the catalog payload itself (separate from the HTTP request signature) that the CS preserves and forwards verbatim, allowing the DS — and ultimately the CN — to verify PN origin and integrity independently of the CS? Open considerations include: where the PN payload signature is carried (a `signature` field within the `Catalog` schema, or a parallel metadata envelope); whether the CS should validate the PN payload signature before indexing and reject malformed submissions; how key rotation interacts with previously indexed catalogs whose payload signatures were produced with an older key; and whether end-to-end integrity verification should be mandatory or optional given that the CS is already implicitly trusted.

## Acknowledgements

Builds on BECKN-006 Signing Beckn APIs in HTTP Draft-01 and the broader dedi protocol specification. Thanks to all contributors to the Beckn Protocol v2.0 working group.

## References

- **Governance:** Click [here](../GOVERNANCE.md).
- **Keyword definitions:** Click [here](./Keyword_Definitions.md).
- **RFC 8032** — Edwards-Curve Digital Signature Algorithm (EdDSA). IETF.
- **RFC 7693** — The BLAKE2 Cryptographic Hash and Message Authentication Code (MAC). IETF.
- **RFC 4648** — The Base16, Base32, and Base64 Data Encodings. IETF.
- **draft-cavage-http-signatures-12** — Signing HTTP Messages. IETF (expired draft, used as basis for Beckn HTTP Signature format).
- **dedi protocol** — Decentralized Directory Protocol specification. Networks for Humanity Foundation.
- **Identity and Addressing:** Click [here](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Identity_and_Addressing.md) (drafted on `draft` branch, undergoing review).
- **Error Codes:** Click [here](https://github.com/beckn/protocol-specifications-v2/blob/draft/docs/Error_Codes.md) (drafted on `draft` branch, undergoing review).
- **BECKN-006** — Signing Beckn APIs in HTTP Draft-01 (superseded by this RFC).
