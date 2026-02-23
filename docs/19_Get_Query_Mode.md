# GET Query Mode — Self-Contained URL Protocol

**Status:** Draft  
**Author(s):**  
**Created:**  
**Updated:**  
**Conformance impact:** Minor (additive — new optional request mode introduced in v2.0.1)  
**Security/privacy implications:** Query Mode encodes the entire request as a URL. URLs may be logged by proxies, servers, and browsers. Sensitive payload data SHOULD be minimized in Query Mode requests. Query Mode requests MUST NOT include authentication credentials beyond the Beckn Signature.  
**Replaces / Relates to:** New in v2.0.1. Introduced alongside GET Body Mode.

---

## Abstract

This RFC specifies the GET Query Mode for Beckn Protocol v2.0.1 — a request mode in which the entire Beckn protocol message (payload and signature) is encoded as URL query parameters, producing a self-contained URL. This enables Beckn protocol interactions to be initiated from QR codes, deep links, bookmarkable pages, frontend UIs, and IoT/embedded clients that cannot send HTTP request bodies.

---

## 1. Context

Standard Beckn requests require an HTTP request body (for `RequestContainer`) and an `Authorization` header (for the Beckn Signature). These are not available in all contexts:

- A QR code can only encode a URL.
- A browser link (`<a href="...">`) carries no body.
- An IoT device may only support simple GET requests.
- A user sharing a link to a specific product discovery query needs a self-contained URL.

GET Query Mode addresses all of these by encoding the complete request in the URL itself.

---

## 2. Specification (Normative)

### 2.1 Query Mode URL Structure

```
GET /beckn/{becknEndpoint}?Authorization={encodedSignature}&RequestAction={encodedPayload}
```

Both parameters MUST be URL-encoded (percent-encoded as per RFC 3986).

### 2.2 Authorization Parameter

The `Authorization` query parameter MUST contain the Beckn Signature string in the exact same format as the `Authorization` header (without the `Signature ` prefix is permitted — see Section 2.6):

```
Authorization=Signature%20keyId%3D%22...%22%2Calgorithm%3D%22ed25519%22...
```

### 2.3 RequestAction Parameter

The `RequestAction` query parameter MUST contain the URL-encoded JSON of the `RequestContainer` (or a compact form thereof).

### 2.4 Mutual Exclusivity

Query Mode and Body Mode are **mutually exclusive**:

- If `Authorization` and `RequestAction` are present as query parameters, the request body MUST be absent and the `Authorization` header MUST be absent.
- If the request body is present, both query parameters MUST be absent.

Servers receiving a request that violates this rule MUST return `400 NackBadRequest`.

### 2.5 Signing String Construction for Query Mode

In Query Mode, there is no request body. The digest component of the signing string MUST be computed over the URL-encoded `RequestAction` value:

```
digest = Base64(BLAKE2b-512(urlEncodedRequestAction))
```

The signing string is otherwise identical to Body Mode:

```
(created): {unixTimestamp}
(expires): {unixTimestamp}
digest: BLAKE-512={base64digest}
```

### 2.6 No Callback Guarantee

Servers handling Query Mode requests MUST NOT send an asynchronous callback. The response MUST be:
- `Ack` (HTTP 200) — request received and processed; no callback will follow.
- `NackBadRequest` (HTTP 400) — malformed request.
- `NackUnauthorized` (HTTP 401) — invalid signature.

The caller MUST NOT register a callback endpoint expectation for a Query Mode request.

### 2.7 CounterSignature in Query Mode

Query Mode responses (`Ack`) MUST include a `CounterSignature`, consistent with all other `Ack` responses.

---

## 3. Use Cases

| Use Case | Mechanism |
|---|---|
| QR code for product discovery | QR encodes `GET /beckn/discover?Authorization=...&RequestAction=...` |
| Deep link in mobile app | App opens URL that triggers a discovery query |
| Bookmarkable search | User shares a URL that re-executes a specific query |
| IoT sensor event | Sensor fires a GET request with discovery intent encoded in URL |
| Frontend UI without backend | Browser JS constructs and sends Query Mode request directly |

---

## 4. Security Considerations

- **URL logging**: Query Mode URLs appear in server logs, proxy logs, and browser history. Sensitive query data (health conditions, financial intent) SHOULD NOT be placed in Query Mode requests.
- **URL length limits**: Long payloads may exceed URL length limits (typically 2048–8192 characters). Implementations MUST test URL length before constructing Query Mode requests.
- **Signature validity window**: The `expires` field in the signature limits how long a Query Mode URL remains valid. Expired URLs MUST be rejected.
- **No callback = no replay risk**: Since Query Mode produces no callback, replay attacks are limited to re-triggering the same read-only query.

---

## 5. Example

### Discovery QR Code URL (unencoded for readability)

```
GET /beckn/discover
  ?Authorization=Signature keyId="bap.example.com|key-001|ed25519",algorithm="ed25519",created="1641287875",expires="1641291475",headers="(created) (expires) digest",signature="..."
  &RequestAction={"context":{"action":"discover","domain":"beckn:retail",...},"message":{"@type":"Intent","item":{"name":"coffee"}}}
```

### Server Response

```json
{
  "status": "ACK",
  "counterSignature": {
    "messageId": "msg-uuid",
    "signedBy": "cds.example.com|key-002|ed25519",
    "timestamp": "2026-01-04T09:17:56.100Z",
    "signature": "..."
  }
}
```

---

## 6. Conformance Requirements

| ID | Requirement | Level |
|---|---|---|
| CON-024-01 | Query Mode MUST use both `Authorization` and `RequestAction` query parameters | MUST |
| CON-024-02 | Query Mode requests MUST NOT include a request body | MUST |
| CON-024-03 | Query Mode requests MUST NOT include an `Authorization` header | MUST |
| CON-024-04 | Digest MUST be computed over the URL-encoded `RequestAction` value | MUST |
| CON-024-05 | Servers MUST NOT send callbacks for Query Mode requests | MUST |
| CON-024-06 | Query Mode `Ack` responses MUST include a `CounterSignature` | MUST |

---

## 7. References

- [8_Core_API_Envelope.md](./8_Core_API_Envelope.md)
- [10_Signing_Beckn_APIs_in_HTTP.md](./10_Signing_Beckn_APIs_in_HTTP.md)
- [RFC 3986 — URI Generic Syntax](https://datatracker.ietf.org/doc/html/rfc3986)
- `api/v2.0.1/beckn.yaml` — `RequestActionQuery` schema

---

## 8. Changelog

| Version | Date | Author | Summary |
|---|---|---|---|
| Draft-01 | | | Initial draft |
